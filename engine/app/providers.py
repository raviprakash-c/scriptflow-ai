import base64,html,os,re
from dataclasses import dataclass
import httpx

@dataclass(frozen=True)
class FootageCandidate:
    footage_id:str
    source:str
    source_url:str
    license:str
    attribution:str
    commercial_use:bool
    ai_generated:bool
    visual:str
    download_url:str|None=None
    rights_note:str=""

DEMO=[
 ("growth","progress growth chart improvement","#6F6BFF","An abstract upward trend"),
 ("planning","planning organization checklist workflow","#63C7B8","A stylized planning board"),
 ("nature","nature green environment trees outdoors","#6DB77C","An abstract landscape"),
 ("technology","technology digital computing data network code","#4C9CEB","A geometric network"),
 ("money","money savings budget finance coins banking","#E5B454","A savings visualization"),
 ("people","team collaboration learning working community","#CF8FDE","Abstract linked team shapes"),
 ("travel","travel city roads transport journey","#E98970","A simplified city and road"),
 ("abstract","trust value meaning abstract idea concept","#A3A9B7","Minimal abstract fallback")]

def tokens(s):
    return {x.lower() for x in re.findall(r"[a-zA-Z0-9]+",s) if len(x)>2}

def svg_data(title,color):
    label=html.escape(title[:36],quote=True)
    raw='''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720"><rect width="100%" height="100%" fill="#171b29"/><circle cx="1000" cy="160" r="220" fill="COLOR" opacity=".3"/><path d="M200 520 Q500 150 720 400 T1100 220" fill="none" stroke="COLOR" stroke-width="16"/><rect x="240" y="270" width="800" height="180" rx="24" fill="#090c13" opacity=".65"/><text x="640" y="360" fill="#fff" font-size="38" text-anchor="middle" font-family="Arial">TITLE</text><text x="640" y="410" fill="#ddd" font-size="20" text-anchor="middle" font-family="Arial">SCRIPTFlow AI - LOCAL DEMO VISUAL</text></svg>'''
    return "data:image/svg+xml;base64,"+base64.b64encode(raw.replace("COLOR",color).replace("TITLE",label).encode()).decode()

def search_footage(query,avoid=None,used_ids=None):
    used_ids=used_ids or set()
    q=tokens(query)-tokens(" ".join(avoid or []))
    rows=[]
    for key,kw,color,visual in DEMO:
        k=tokens(kw); overlap=len(q&k)
        score=min(.82,.25+overlap/max(1,len(q))*.45+overlap/max(1,len(q|k))*.35)
        if "demo-"+key in used_ids: score-=.65
        rows.append((score,key,kw,color,visual))
    rows.sort(reverse=True)
    score,key,kw,color,visual=rows[0]
    if "demo-"+key in used_ids:
        score,key,kw,color,visual=next((r for r in rows if "demo-"+r[1] not in used_ids),rows[-1])
    candidate=FootageCandidate("demo-"+key,"scriptflow-local-demo",svg_data(visual,color),"Procedural placeholder; not certified stock footage","ScriptFlow AI local procedural visual",False,True,visual,rights_note="Placeholder visual. Commercial rights are not verified.")
    reason=f"Token-overlap selector chose category '{key}'."
    if key=="abstract": reason="Low semantic match confidence; neutral abstract fallback selected."
    return candidate,round(max(0,min(score,1)),3),reason

class FootageProvider:
    name="mock"
    def search(self,query,avoid=None,used_ids=None):
        return search_footage(query,avoid,used_ids)

class PexelsFootageProvider:
    name="pexels"
    endpoint="https://api.pexels.com/v1/videos/search"
    def __init__(self,api_key:str):
        self.api_key=api_key
    def search(self,query,avoid=None,used_ids=None):
        used_ids=used_ids or set()
        search_terms=" ".join(x for x in query.split() if x.lower() not in tokens(" ".join(avoid or []))).strip() or query
        try:
            response=httpx.get(self.endpoint,headers={"Authorization":self.api_key},params={"query":search_terms,"per_page":15,"orientation":"landscape"},timeout=20,follow_redirects=True)
            response.raise_for_status()
            videos=response.json().get("videos",[])
            for video in videos:
                vid=str(video.get("id",""))
                if not vid or f"pexels-{vid}" in used_ids: continue
                files=[f for f in video.get("video_files",[]) if f.get("file_type")=="video/mp4" and f.get("link")]
                if not files: continue
                # Prefer a practical 720p/1080p file rather than downloading 4K unnecessarily.
                files.sort(key=lambda f:(abs(int(f.get("width") or 1280)-1280),int(f.get("width") or 0)>1920,-int(f.get("width") or 0)))
                chosen=files[0];person=(video.get("user") or {}).get("name") or "Pexels contributor"
                asset=FootageCandidate(
                    footage_id=f"pexels-{vid}",
                    source="Pexels",
                    source_url=video.get("url") or "https://www.pexels.com/",
                    license="Pexels License",
                    attribution=f"Video by {person} on Pexels",
                    commercial_use=True,
                    ai_generated=False,
                    visual=f"Stock footage from Pexels: {search_terms}",
                    download_url=chosen.get("link"),
                    rights_note="Pexels permits commercial use under its license; review depicted people, trademarks, and third-party rights before publication."
                )
                score=.72 if tokens(search_terms)&tokens(video.get("url","")) else .62
                return asset,score,f"Pexels API matched query: {search_terms}."
            raise RuntimeError("Pexels returned no unused MP4 video candidates.")
        except Exception as exc:
            # Fail closed to a clearly-labelled local placeholder; never relabel a placeholder as licensed stock.
            asset,score,reason=search_footage(query,avoid,used_ids)
            return asset,score,f"Pexels search failed ({type(exc).__name__}); placeholder fallback selected. {reason}"

class PixabayFootageProvider:
    name="pixabay"
    endpoint="https://pixabay.com/api/videos/"
    def __init__(self,api_key:str):
        self.api_key=api_key
    def search(self,query,avoid=None,used_ids=None):
        used_ids=used_ids or set()
        search_terms=" ".join(x for x in query.split() if x.lower() not in tokens(" ".join(avoid or []))).strip() or query
        try:
            response=httpx.get(self.endpoint,params={"key":self.api_key,"q":search_terms,"per_page":20,"safesearch":"true","order":"popular"},timeout=20,follow_redirects=True)
            response.raise_for_status()
            for video in response.json().get("hits",[]):
                vid=str(video.get("id",""))
                if not vid or f"pixabay-{vid}" in used_ids:continue
                versions=video.get("videos") or {}
                chosen=versions.get("medium") or versions.get("small") or versions.get("tiny") or versions.get("large")
                if not chosen or not chosen.get("url"):continue
                user=video.get("user") or "Pixabay contributor"
                asset=FootageCandidate(
                    footage_id=f"pixabay-{vid}",
                    source="Pixabay",
                    source_url=video.get("pageURL") or "https://pixabay.com/videos/",
                    license="Pixabay Content License",
                    attribution=f"Video by {user} via Pixabay",
                    commercial_use=True,
                    ai_generated=False,
                    visual=f"Stock footage from Pixabay: {search_terms}",
                    download_url=chosen.get("url"),
                    rights_note="Pixabay permits commercial use subject to its Content License; review depicted people, trademarks, logos and other third-party rights before publication."
                )
                return asset,.68,f"Pixabay API matched query: {search_terms}."
            raise RuntimeError("Pixabay returned no unused MP4 video candidates.")
        except Exception as exc:
            asset,score,reason=search_footage(query,avoid,used_ids)
            return asset,score,f"Pixabay search failed ({type(exc).__name__}); placeholder fallback selected. {reason}"

class CompositeFootageProvider:
    name="pexels+pixabay"
    def __init__(self,providers):
        self.providers=providers
    def search(self,query,avoid=None,used_ids=None):
        fallback=None;reasons=[]
        for provider in self.providers:
            asset,score,reason=provider.search(query,avoid,used_ids)
            if asset.source in {"Pexels","Pixabay"} and asset.download_url:
                return asset,score,reason
            fallback=(asset,score,reason);reasons.append(f"{provider.name}: {reason}")
        if fallback:
            asset,score,reason=fallback
            return asset,score,"No licensed provider returned a downloadable clip. "+" | ".join(reasons)
        return search_footage(query,avoid,used_ids)

def get_footage_provider():
    requested=os.getenv("FOOTAGE_PROVIDER","mock").strip().lower()
    pexels_key=os.getenv("PEXELS_API_KEY","").strip()
    pixabay_key=os.getenv("PIXABAY_API_KEY","").strip()
    if requested in {"pexels","composite","auto"}:
        providers=[]
        if pexels_key:providers.append(PexelsFootageProvider(pexels_key))
        if pixabay_key:providers.append(PixabayFootageProvider(pixabay_key))
        if len(providers)>1:return CompositeFootageProvider(providers)
        if providers:return providers[0]
    if requested=="pixabay" and pixabay_key:return PixabayFootageProvider(pixabay_key)
    return FootageProvider()
