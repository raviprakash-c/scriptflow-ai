import html,json,logging,os,shutil,subprocess,time,wave
from datetime import datetime,timezone
from pathlib import Path
from .config import settings
from .planner import plan_scenes,split_script
from .providers import get_footage_provider
log=logging.getLogger("scriptflow.render")
def now(): return datetime.now(timezone.utc).isoformat()
def run(cmd,timeout=600): return subprocess.run(cmd,check=True,capture_output=True,text=True,timeout=timeout)
def probe_duration(path):
    exe=shutil.which("ffprobe")
    if not exe: raise RuntimeError("ffprobe is required for audio inputs; install FFmpeg.")
    try: return float(run([exe,"-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",str(path)],30).stdout.strip())
    except ValueError as e: raise ValueError("Could not read audio duration; audio may be corrupted.") from e
def make_silent_audio(path,dur):
    with wave.open(str(path),"wb") as wf:
        wf.setnchannels(1);wf.setsampwidth(2);wf.setframerate(16000);wf.writeframes(b"\\x00\\x00"*int(dur*16000))
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
    return "\\n".join(lines).strip()+"\\n"
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
    if request.audio_url and not input_path: raise ValueError("Remote audio URL is not enabled in this local build; use the upload endpoint.")
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
        warnings_scene=["Generated placeholder visual; commercial use is not verified."]
        if score<.4:warnings_scene.append("Low relevance confidence; manual review needed.")
        rows.append({"scene_id":f"scene-{i+1:03}","text":scene.text,"start":scene.start,"end":scene.end,"duration":round(scene.end-scene.start,3),"footage_id":asset.footage_id,"source":asset.source,"source_url":asset.source_url,"license":asset.license,"attribution":asset.attribution,"commercial_use":asset.commercial_use,"ai_generated":asset.ai_generated,"selection_reason":reason,"relevance_score":score,"warnings":warnings_scene,"color":colors.get(asset.footage_id,"#A3A9B7")})
        progress(10+int(25*(i+1)/len(plan)),"matching-footage")
    ffmpeg=shutil.which("ffmpeg");outputs={};sizes={"16:9":(1920,1080),"9:16":(1080,1920),"1:1":(1080,1080)}
    if not ffmpeg:warnings.append("FFmpeg missing; no MP4 output rendered.")
    else:
        for ri,ratio in enumerate(request.aspect_ratios):
            progress(38+int(12*ri/len(request.aspect_ratios)),f"rendering-{ratio.replace(':','x')}")
            w,h=sizes[ratio];files=[]
            for row in rows:
                tag=ratio.replace(":","x");svg=outdir/f"{row['scene_id']}-{tag}.svg";png=svg.with_suffix(".png");seg=outdir/f"{row['scene_id']}-{tag}.mp4"
                write_svg(svg,row["text"],row["color"],ratio)
                run([ffmpeg,"-y","-loglevel","error","-i",str(svg),"-frames:v","1",str(png)],60)
                run([ffmpeg,"-y","-loglevel","error","-loop","1","-framerate",str(settings.default_fps),"-i",str(png),"-t",f"{max(.1,row['duration']):.3f}","-vf",f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,format=yuv420p","-r",str(settings.default_fps),"-an","-c:v","libx264","-preset","veryfast","-pix_fmt","yuv420p",str(seg)],120)
                files.append(seg)
            concat=outdir/f"concat-{ratio.replace(':','x')}.txt";concat.write_text("".join(f"file '{x.as_posix()}'\\n" for x in files))
            video=outdir/f"video_{ratio.replace(':','x')}.mp4"
            run([ffmpeg,"-y","-loglevel","error","-f","concat","-safe","0","-i",str(concat),"-c","copy",str(video)],300)
            if input_path and input_path.exists():
                mux=outdir/f"mux-{ratio.replace(':','x')}.mp4"
                run([ffmpeg,"-y","-loglevel","error","-i",str(video),"-i",str(input_path),"-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-shortest","-movflags","+faststart",str(mux)],300);mux.replace(video)
            outputs[f"video_{ratio.replace(':','x')}.mp4"]=f"/api/v1/jobs/{job_id}/files/video_{ratio.replace(':','x')}.mp4"
    progress(82,"writing-outputs")
    if request.captions.srt:
        (outdir/"captions.srt").write_text(build_srt(rows));outputs["captions.srt"]=f"/api/v1/jobs/{job_id}/files/captions.srt"
    safe_rows=[{k:v for k,v in x.items() if k!="color"} for x in rows]
    timeline={"job_id":job_id,"duration":round(duration,3),"audio_source":audio_source,"scenes":safe_rows,"coverage_seconds":round(sum(x["duration"] for x in rows),3),"repeated_clip_ids":[],"warnings":warnings}
    (outdir/"timeline.json").write_text(json.dumps(timeline,indent=2,ensure_ascii=False));outputs["timeline.json"]=f"/api/v1/jobs/{job_id}/files/timeline.json"
    manifest={"job_id":job_id,"status":"succeeded","providers":{"footage":provider.name,"tts":tts_provider},"versions":{"scriptflow":"0.2.0","ffmpeg":None},"settings":{"voice":request.voice,"style":request.style,"avoid":request.avoid,"aspect_ratios":request.aspect_ratios,"captions":request.captions.model_dump(),"fps":settings.default_fps},"seed":request.seed,"timings":{"elapsed_seconds":round(time.perf_counter()-t0,3),"duration_seconds":duration},"cost_estimate_usd":0 if tts_provider=="mock-silent" else None,"warnings":warnings,"rights":{"commercial_media_verified":False,"note":"Only generated placeholder visuals included; configure a verified commercial source before publishing."},"outputs":outputs}
    (outdir/"manifest.json").write_text(json.dumps(manifest,indent=2));outputs["manifest.json"]=f"/api/v1/jobs/{job_id}/files/manifest.json"
    manifest["output_validation"]={n:{"exists":(outdir/n).exists(),"size_bytes":(outdir/n).stat().st_size if (outdir/n).exists() else 0} for n in outputs}
    (outdir/"manifest.json").write_text(json.dumps(manifest,indent=2));progress(100,"complete")
    return {"outputs":outputs,"timeline":timeline,"manifest":manifest,"duration":duration,"warnings":warnings}
