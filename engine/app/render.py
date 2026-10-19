import html,ipaddress,json,logging,os,shutil,socket,subprocess,time,uuid,wave
import httpx
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlparse
from .config import settings
from .planner import plan_scenes,split_script
from .providers import FootageProvider,get_footage_provider,search_footage
log=logging.getLogger("scriptflow.render")
def now(): return datetime.now(timezone.utc).isoformat()
def run(cmd,timeout=600): return subprocess.run(cmd,check=True,capture_output=True,text=True,timeout=timeout)
def download_clip(url,path):
    limit=settings.max_stock_clip_mb*1024*1024
    total=0
    with httpx.stream("GET",url,follow_redirects=True,timeout=30) as response:
        response.raise_for_status()
        with path.open("wb") as out:
            for chunk in response.iter_bytes(1024*1024):
                if not chunk:continue
                total+=len(chunk)
                if total>limit:
                    path.unlink(missing_ok=True)
                    raise ValueError(f"Stock clip exceeds {settings.max_stock_clip_mb} MB limit.")
                out.write(chunk)
    if total<1024:
        path.unlink(missing_ok=True)
        raise ValueError("Stock clip download was empty or too small.")
    return path

def validate_remote_audio_url(url):
    """Allow HTTPS audio URLs only for explicitly configured hosts with public DNS answers."""
    parsed=urlparse(url)
    host=(parsed.hostname or "").rstrip(".").lower()
    if parsed.scheme!="https" or not host or parsed.username or parsed.password or parsed.fragment:
        raise ValueError("Remote audio URL must be a credential-free HTTPS URL.")
    if parsed.port not in (None,443):
        raise ValueError("Remote audio URLs may only use HTTPS port 443.")
    allowed=set(settings.audio_url_allowed_hosts)
    if not allowed or host not in allowed:
        raise ValueError("Remote audio host is not allow-listed; configure AUDIO_URL_ALLOWED_HOSTS.")
    try:
        ipaddress.ip_address(host)
        raise ValueError("Remote audio host must be a DNS name, not an IP literal.")
    except ValueError as exc:
        if str(exc).startswith("Remote audio host"):
            raise
    try:
        addresses=socket.getaddrinfo(host,443,type=socket.SOCK_STREAM)
    except OSError as exc:
        raise ValueError("Remote audio host could not be resolved.") from exc
    if not addresses:
        raise ValueError("Remote audio host has no DNS addresses.")
    for address in addresses:
        try:
            ip=ipaddress.ip_address(address[4][0])
        except ValueError as exc:
            raise ValueError("Remote audio host resolved to an invalid IP address.") from exc
        if not ip.is_global:
            raise ValueError("Remote audio host resolves to a non-public IP address.")
    suffix=Path(parsed.path).suffix.lower()
    if suffix not in {".mp3",".wav",".m4a"}:
        raise ValueError("Remote audio URL path must end in .mp3, .wav, or .m4a.")
    return host,suffix


def download_remote_audio(url, upload_dir):
    host,suffix=validate_remote_audio_url(url)
    upload_dir=Path(upload_dir)
    upload_dir.mkdir(parents=True,exist_ok=True)
    target=upload_dir/f"remote-{uuid.uuid4()}{suffix}"
    limit=settings.max_upload_mb*1024*1024
    total=0
    try:
        # Redirects are intentionally disabled so an allow-listed URL cannot redirect to a private host.
        with httpx.stream("GET",url,follow_redirects=False,timeout=httpx.Timeout(30,connect=10)) as response:
            if 300<=response.status_code<400:
                raise ValueError("Remote audio redirects are not allowed.")
            response.raise_for_status()
            content_type=response.headers.get("content-type","").split(";",1)[0].strip().lower()
            allowed_types={"audio/mpeg","audio/mp3","audio/wav","audio/x-wav","audio/wave","audio/mp4","audio/x-m4a","application/octet-stream"}
            if content_type not in allowed_types:
                raise ValueError("Remote URL did not return a supported audio content type.")
            declared=response.headers.get("content-length")
            if declared:
                try:
                    if int(declared)>limit: raise ValueError(f"Remote audio exceeds {settings.max_upload_mb} MB limit.")
                except ValueError as exc:
                    if "exceeds" in str(exc): raise
            with target.open("wb") as output:
                for chunk in response.iter_bytes(1024*1024):
                    if not chunk: continue
                    total+=len(chunk)
                    if total>limit:
                        raise ValueError(f"Remote audio exceeds {settings.max_upload_mb} MB limit.")
                    output.write(chunk)
        if total<1024:
            raise ValueError("Remote audio download was empty or too small.")
        return target
    except Exception:
        target.unlink(missing_ok=True)
        raise


def probe_duration(path):
    exe=shutil.which("ffprobe")
    if not exe: raise RuntimeError("ffprobe is required for audio inputs; install FFmpeg.")
    try: return float(run([exe,"-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",str(path)],30).stdout.strip())
    except ValueError as e: raise ValueError("Could not read audio duration; audio may be corrupted.") from e

def _stream_number(stream, key, default):
    try:
        value = float(stream.get(key, default))
        return value if value >= 0 else default
    except (TypeError, ValueError):
        return default


def validate_av_sync(video, audio, expected_duration):
    """Validate stream start alignment and per-stream durations when ffprobe reports them."""
    video_start = _stream_number(video, "start_time", 0.0)
    audio_start = _stream_number(audio, "start_time", 0.0)
    if abs(video_start - audio_start) > 0.25:
        raise ValueError("Rendered audio and video start times are out of sync.")
    tolerance = max(1.0, expected_duration * 0.05)
    video_duration = _stream_number(video, "duration", expected_duration)
    audio_duration = _stream_number(audio, "duration", expected_duration)
    if abs(video_duration - audio_duration) > tolerance:
        raise ValueError("Rendered audio and video durations are out of sync.")
    return {
        "video_start_seconds": round(video_start, 3),
        "audio_start_seconds": round(audio_start, 3),
        "video_duration_seconds": round(video_duration, 3),
        "audio_duration_seconds": round(audio_duration, 3),
        "start_delta_seconds": round(abs(video_start - audio_start), 3),
        "duration_delta_seconds": round(abs(video_duration - audio_duration), 3),
    }


def inspect_visual_quality(path):
    """Return black/frozen-frame diagnostics; findings are warnings for human review, not proof of defects."""
    exe = shutil.which("ffmpeg")
    if not exe:
        return ["Visual quality scan skipped: ffmpeg is unavailable."]
    try:
        result = subprocess.run(
            [exe, "-hide_banner", "-i", str(path), "-vf",
             "blackdetect=d=2:pix_th=0.10,freezedetect=n=-60dB:d=3",
             "-an", "-f", "null", "-"],
            check=False, capture_output=True, text=True, timeout=180,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return [f"Visual quality scan unavailable ({type(exc).__name__})."]
    log_text = (result.stderr or "") + "\n" + (result.stdout or "")
    findings = []
    black_events = re.findall(r"black_start:([0-9.]+)\s+black_end:([0-9.]+)", log_text)
    if black_events:
        findings.append("Visual scan detected black intervals: " + ", ".join(
            f"{start}-{end}s" for start, end in black_events[:10]
        ) + ". Review the video; intentional dark scenes can trigger this warning.")
    freeze_events = re.findall(r"lavfi\.freezedetect\.freeze_start:([0-9.]+)", log_text)
    if freeze_events:
        findings.append("Visual scan detected potentially frozen intervals starting at: " +
                        ", ".join(f"{value}s" for value in freeze_events[:10]) +
                        ". Static placeholder visuals can trigger this warning.")
    if result.returncode != 0 and not findings:
        findings.append("Visual quality scan did not complete successfully; inspect the render manually.")
    return findings


def validate_video(path, expected_width, expected_height, expected_duration):
    """Fail invalid MP4s and report stream synchronization plus visual-quality diagnostics."""
    exe=shutil.which("ffprobe")
    if not exe: raise RuntimeError("ffprobe is required to validate rendered MP4 output; install FFmpeg.")
    raw=run([exe,"-v","error","-show_streams","-show_format","-of","json",str(path)],30).stdout
    try: data=json.loads(raw)
    except json.JSONDecodeError as exc: raise ValueError("ffprobe returned invalid output metadata.") from exc
    streams=data.get("streams",[])
    video=next((s for s in streams if s.get("codec_type")=="video"),None)
    audio=next((s for s in streams if s.get("codec_type")=="audio"),None)
    if not video: raise ValueError("Rendered MP4 has no video stream.")
    if not audio: raise ValueError("Rendered MP4 has no audio stream.")
    if int(video.get("width") or 0)!=expected_width or int(video.get("height") or 0)!=expected_height:
        raise ValueError(f"Rendered dimensions do not match expected {expected_width}x{expected_height}.")
    if video.get("codec_name")!="h264": raise ValueError("Rendered video codec is not H.264.")
    try: actual_duration=float(data.get("format",{}).get("duration",0))
    except (TypeError,ValueError) as exc: raise ValueError("Rendered MP4 duration is invalid.") from exc
    if actual_duration<=0: raise ValueError("Rendered MP4 has no positive duration.")
    if abs(actual_duration-expected_duration)>max(2.0,expected_duration*.05):
        raise ValueError("Rendered MP4 duration differs materially from the planned timeline.")
    sync = validate_av_sync(video, audio, expected_duration)
    size=Path(path).stat().st_size
    if size<1024: raise ValueError("Rendered MP4 is unexpectedly small.")
    return {"codec":video.get("codec_name"),"width":expected_width,"height":expected_height,
            "duration_seconds":round(actual_duration,3),"has_audio":True,"size_bytes":size,
            "audio_video_sync":sync,"quality_warnings":inspect_visual_quality(path)}

def ffmpeg_filter_path(path):
    # FFmpeg filter arguments use their own escaping rules, even on Windows.
    return str(Path(path).resolve()).replace("\\","/").replace(":","\\:").replace("'","\\'").replace(",","\\,")
def make_silent_audio(path,dur):
    with wave.open(str(path),"wb") as wf:
        wf.setnchannels(1);wf.setsampwidth(2);wf.setframerate(16000);wf.writeframes(b"\x00\x00"*int(dur*16000))
def srt_time(sec):
    ms=int(round(sec*1000));h,rem=divmod(ms,3600000);m,rem=divmod(rem,60000);s,ms=divmod(rem,1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"
def build_srt(scenes):
    lines=[];n=1
    for sc in scenes:
        words=sc["text"].split() or [sc["text"]]; chunks=[" ".join(words[i:i+10]) for i in range(0,len(words),10)]
        weights=[max(1,len(c.split())) for c in chunks];total=sum(weights);at=sc["start"];dur=max(.1,sc["end"]-sc["start"])
        for c,w in zip(chunks,weights):
            dt=dur*w/total;lines.extend([str(n),f"{srt_time(at)} --> {srt_time(at+dt)}",c,""]);n+=1;at+=dt
    return "\n".join(lines).strip()+"\n"
def write_svg(path,title,color,ratio):
    sizes={"16:9":(1920,1080),"9:16":(1080,1920),"1:1":(1080,1080)};w,h=sizes[ratio]
    label=html.escape(title[:80],quote=True);font=int(min(w,h)*.044)
    raw=f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#111521"/><stop offset="1" stop-color="#222e43"/></linearGradient></defs><rect width="100%" height="100%" fill="url(#g)"/><circle cx="{w*.78}" cy="{h*.25}" r="{min(w,h)*.24}" fill="{color}" opacity=".24"/><circle cx="{w*.18}" cy="{h*.78}" r="{min(w,h)*.3}" fill="{color}" opacity=".12"/><path d="M{w*.15} {h*.63} Q{w*.39} {h*.28} {w*.55} {h*.55} T{w*.88} {h*.32}" fill="none" stroke="{color}" stroke-width="{max(5,int(min(w,h)*.008))}" stroke-linecap="round"/><rect x="{w*.09}" y="{h*.38}" width="{w*.82}" height="{h*.24}" rx="{min(w,h)*.025}" fill="#090c13" opacity=".62" stroke="{color}" stroke-opacity=".55"/><text x="50%" y="{h*.49}" fill="#fff" font-size="{font}" text-anchor="middle" font-family="Arial" font-weight="700">{label}</text><text x="50%" y="{h*.55}" fill="#c8cede" font-size="{int(font*.42)}" text-anchor="middle" font-family="Arial">SCRIPTFlow AI - PLACEHOLDER VISUAL</text></svg>'''
    path.write_text(raw,encoding="utf-8")
def transcribe(path):
    try:
        from faster_whisper import WhisperModel
        model=WhisperModel(os.getenv("WHISPER_MODEL","base"),device=os.getenv("WHISPER_DEVICE","cpu"),compute_type=os.getenv("WHISPER_COMPUTE_TYPE","int8"))
        segs,_=model.transcribe(str(path),vad_filter=True);text=" ".join(s.text.strip() for s in segs).strip()
        return (text,[]) if text else (None,["Audio contains no detectable speech; it may be silent or music-only."])
    except ImportError: return None,["Install the audio extra (faster-whisper) to transcribe uploads."]
    except Exception as e: return None,[f"Transcription failed: {type(e).__name__}."]
def make_tts(text,voice,path):
    if os.getenv("TTS_PROVIDER","mock").lower()=="edge-tts":
        try:
            import asyncio,edge_tts
            async def save(): await edge_tts.Communicate(text,voice=voice if voice!="en-IN-female" else "en-IN-NeerjaNeural").save(str(path))
            asyncio.run(save());return True,"edge-tts",[]
        except Exception as e:return False,"mock-silent",[f"TTS failed ({type(e).__name__}); silence used."]
    return False,"mock-silent",["No TTS provider configured; timing audio is silent, not narration."]
def render_job(job_id,request,input_path,progress):
    t0=time.perf_counter();outdir=settings.output_dir/job_id;outdir.mkdir(parents=True,exist_ok=True)
    warnings=[];tts_provider="input-audio"
    if request.audio_url and not input_path:
        input_path=download_remote_audio(request.audio_url,settings.output_dir/"uploads")
    if input_path:
        if input_path.suffix.lower() not in {".mp3",".wav",".m4a"}:raise ValueError("Supported audio formats: mp3, wav, m4a.")
        duration=probe_duration(input_path)
        if duration<=0:raise ValueError("Audio has no playable duration.")
        if duration>settings.max_audio_seconds:raise ValueError(f"Audio exceeds {settings.max_audio_seconds} seconds.")
        transcript,audio_warnings=transcribe(input_path);warnings.extend(audio_warnings)
        if not transcript:raise ValueError("Audio transcript unavailable; install/configure transcription and use speech audio.")
        pairs=[(x,None) for x in split_script(transcript)];audio_source="uploaded-audio"
    else:
        pairs=[(s.text.strip(),s.visual_hint) for s in request.scenes] if request.scenes else [(x,None) for x in split_script((request.script or "").strip())]
        if not pairs:raise ValueError("No scenes could be planned from the input.")
        planned=plan_scenes(pairs);duration=sum(x.end-x.start for x in planned)
        voice=outdir/"voiceover.mp3";tts_used,tts_provider,ww=make_tts(" ".join(x for x,_ in pairs),request.voice,voice);warnings.extend(ww)
        if tts_used:duration=probe_duration(voice);input_path=voice;audio_source="generated-tts"
        else:input_path=outdir/"timing-audio.wav";make_silent_audio(input_path,duration);audio_source="silent-timing-audio"
    if duration>settings.max_audio_seconds:raise ValueError(f"Duration exceeds {settings.max_audio_seconds} seconds.")
    if not request.scenes:pairs=[(x,None) for x in split_script(" ".join(t for t,_ in pairs))]
    plan=plan_scenes(pairs,total_duration=duration);progress(10,"planning-scenes")
    provider=get_footage_provider();used=set();rows=[]
    colors={"demo-growth":"#6F6BFF","demo-planning":"#63C7B8","demo-nature":"#6DB77C","demo-technology":"#4C9CEB","demo-money":"#E5B454","demo-people":"#CF8FDE","demo-travel":"#E98970","demo-abstract":"#A3A9B7"}
    for i,scene in enumerate(plan):
        asset,score,reason=provider.search(scene.visual_hint or scene.text,request.avoid,used)
        if asset.footage_id in used:raise RuntimeError("Repeated footage selected; refusing duplicate clips.")
        used.add(asset.footage_id)
        local_video_path=None
        if asset.download_url:
            try:
                local_video_path=download_clip(asset.download_url,outdir/f"scene-{i+1:03}-source.mp4")
            except Exception as exc:
                fallback,score,why=provider.search(scene.visual_hint or scene.text,request.avoid,used)
                if fallback.download_url:
                    try:
                        local_video_path=download_clip(fallback.download_url,outdir/f"scene-{i+1:03}-fallback.mp4")
                    except Exception:
                        fallback,score,why=search_footage(scene.visual_hint or scene.text,request.avoid,used)
                        local_video_path=None
                if fallback.footage_id in used:raise RuntimeError("No unique footage fallback remains for this scene.")
                asset=fallback;used.add(asset.footage_id);reason=f"Primary stock download failed ({type(exc).__name__}); fallback selected. {why}"
        warnings_scene=[]
        if local_video_path:
            warnings_scene.append(asset.rights_note or "Review third-party rights before publication.")
        else:
            warnings_scene.append("Generated placeholder visual; commercial use is not verified.")
        if score<.4:warnings_scene.append("Low relevance confidence; manual review needed.")
        rows.append({"scene_id":f"scene-{i+1:03}","text":scene.text,"start":scene.start,"end":scene.end,"duration":round(scene.end-scene.start,3),"footage_id":asset.footage_id,"source":asset.source,"source_url":asset.source_url,"license":asset.license,"attribution":asset.attribution,"commercial_use":asset.commercial_use,"ai_generated":asset.ai_generated,"selection_reason":reason,"relevance_score":score,"warnings":warnings_scene,"color":colors.get(asset.footage_id,"#A3A9B7"),"local_video_path":str(local_video_path) if local_video_path else None})
        progress(10+int(25*(i+1)/len(plan)),"matching-footage")
    ffmpeg=shutil.which("ffmpeg");outputs={};validated_outputs={};sizes={"16:9":(1920,1080),"9:16":(1080,1920),"1:1":(1080,1080)}
    if not ffmpeg: raise RuntimeError("FFmpeg is required to create MP4 output; install FFmpeg and ffprobe.")
    srt_path=outdir/"captions.srt"
    if request.captions.srt or request.captions.burn_in:
        srt_path.write_text(build_srt(rows),encoding="utf-8")
    for ri,ratio in enumerate(request.aspect_ratios):
            progress(38+int(12*ri/len(request.aspect_ratios)),f"rendering-{ratio.replace(':','x')}")
            w,h=sizes[ratio];files=[]
            for row in rows:
                tag=ratio.replace(":","x");svg=outdir/f"{row['scene_id']}-{tag}.svg";png=svg.with_suffix(".png");seg=outdir/f"{row['scene_id']}-{tag}.mp4"
                if row.get("local_video_path"):
                    run([ffmpeg,"-y","-loglevel","error","-stream_loop","-1","-i",row["local_video_path"],"-t",f"{max(.1,row['duration']):.3f}","-vf",f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},fps={settings.default_fps},format=yuv420p","-an","-c:v","libx264","-preset","veryfast","-pix_fmt","yuv420p","-movflags","+faststart",str(seg)],180)
                else:
                    write_svg(svg,row["text"],row["color"],ratio)
                    run([ffmpeg,"-y","-loglevel","error","-i",str(svg),"-frames:v","1",str(png)],60)
                    run([ffmpeg,"-y","-loglevel","error","-loop","1","-framerate",str(settings.default_fps),"-i",str(png),"-t",f"{max(.1,row['duration']):.3f}","-vf",f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,format=yuv420p","-r",str(settings.default_fps),"-an","-c:v","libx264","-preset","veryfast","-pix_fmt","yuv420p",str(seg)],120)
                files.append(seg)
            concat=outdir/f"concat-{ratio.replace(':','x')}.txt";concat.write_text("".join(f"file '{x.as_posix()}'\n" for x in files))
            video=outdir/f"video_{ratio.replace(':','x')}.mp4"
            run([ffmpeg,"-y","-loglevel","error","-f","concat","-safe","0","-i",str(concat),"-c","copy",str(video)],300)
            if request.captions.burn_in:
                captioned=outdir/f"captioned-{ratio.replace(':','x')}.mp4"
                font_size=42 if ratio=="9:16" else 32
                subtitle_filter=f"subtitles='{ffmpeg_filter_path(srt_path)}':force_style='FontName=Arial,FontSize={font_size},Outline=2,Shadow=1,Alignment=2,MarginV=48'"
                run([ffmpeg,"-y","-loglevel","error","-i",str(video),"-vf",subtitle_filter,"-c:v","libx264","-preset","veryfast","-pix_fmt","yuv420p","-movflags","+faststart",str(captioned)],300)
                captioned.replace(video)
            if input_path and input_path.exists():
                mux=outdir/f"mux-{ratio.replace(':','x')}.mp4"
                run([ffmpeg,"-y","-loglevel","error","-i",str(video),"-i",str(input_path),"-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-shortest","-movflags","+faststart",str(mux)],300);mux.replace(video)
            validation=validate_video(video,w,h,duration)
            validated_outputs[f"video_{ratio.replace(':','x')}.mp4"]=validation
            outputs[f"video_{ratio.replace(':','x')}.mp4"]=f"/api/v1/jobs/{job_id}/files/video_{ratio.replace(':','x')}.mp4"
    progress(82,"writing-outputs")
    if request.captions.srt:
        outputs["captions.srt"]=f"/api/v1/jobs/{job_id}/files/captions.srt"
    safe_rows=[{k:v for k,v in x.items() if k not in {"color","local_video_path"}} for x in rows]
    timeline={"job_id":job_id,"duration":round(duration,3),"audio_source":audio_source,"scenes":safe_rows,"coverage_seconds":round(sum(x["duration"] for x in rows),3),"repeated_clip_ids":[],"warnings":warnings}
    (outdir/"timeline.json").write_text(json.dumps(timeline,indent=2,ensure_ascii=False));outputs["timeline.json"]=f"/api/v1/jobs/{job_id}/files/timeline.json"
    manifest={"job_id":job_id,"status":"succeeded","providers":{"footage":provider.name,"tts":tts_provider},"versions":{"scriptflow":"0.2.0","ffmpeg":None},"settings":{"voice":request.voice,"style":request.style,"avoid":request.avoid,"aspect_ratios":request.aspect_ratios,"captions":request.captions.model_dump(),"fps":settings.default_fps},"seed":request.seed,"timings":{"elapsed_seconds":round(time.perf_counter()-t0,3),"duration_seconds":duration},"cost_estimate_usd":0 if tts_provider=="mock-silent" else None,"warnings":warnings,"rights":{"commercial_media_verified":bool(rows) and all(x["commercial_use"] and x["source"] in {"Pexels","Pixabay"} and x.get("local_video_path") for x in rows),"rights_review_required":True,"note":"Pexels/Pixabay clips are used under their respective licenses when downloaded successfully. Review depicted people, trademarks and other third-party rights before publication; placeholders are not commercially verified."},"outputs":outputs}
    (outdir/"manifest.json").write_text(json.dumps(manifest,indent=2));outputs["manifest.json"]=f"/api/v1/jobs/{job_id}/files/manifest.json"
    manifest["output_validation"]={n:{"exists":(outdir/n).exists(),"size_bytes":(outdir/n).stat().st_size if (outdir/n).exists() else 0,**validated_outputs.get(n,{})} for n in outputs}
    (outdir/"manifest.json").write_text(json.dumps(manifest,indent=2));progress(100,"complete")
    return {"outputs":outputs,"timeline":timeline,"manifest":manifest,"duration":duration,"warnings":warnings}
