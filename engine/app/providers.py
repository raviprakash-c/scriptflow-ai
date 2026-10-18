import base64,html,re
from dataclasses import dataclass
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
DEMO=[
 ("growth","progress growth chart improvement","#6F6BFF","An abstract upward trend"),
 ("planning","planning organization checklist workflow","#63C7B8","A stylized planning board"),
 ("nature","nature green environment trees outdoors","#6DB77C","An abstract landscape"),
 ("technology","technology digital computing data network code","#4C9CEB","A geometric network"),
 ("money","money savings budget finance coins banking","#E5B454","A savings visualization"),
 ("people","team collaboration learning working community","#CF8FDE","Abstract linked team shapes"),
 ("travel","travel city roads transport journey","#E98970","A simplified city and road"),
 ("abstract","trust value meaning abstract idea concept","#A3A9B7","Minimal abstract fallback")]
def tokens(s): return {x.lower() for x in re.findall(r"[a-zA-Z0-9]+",s) if len(x)>2}
def svg_data(title,color):
    label=html.escape(title[:36],quote=True)
    raw='''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720"><rect width="100%" height="100%" fill="#171b29"/><circle cx="1000" cy="160" r="220" fill="COLOR" opacity=".3"/><path d="M200 520 Q500 150 720 400 T1100 220" fill="none" stroke="COLOR" stroke-width="16"/><rect x="240" y="270" width="800" height="180" rx="24" fill="#090c13" opacity=".65"/><text x="640" y="360" fill="#fff" font-size="38" text-anchor="middle" font-family="Arial">TITLE</text><text x="640" y="410" fill="#ddd" font-size="20" text-anchor="middle" font-family="Arial">SCRIPTFlow AI - LOCAL DEMO VISUAL</text></svg>'''
    return "data:image/svg+xml;base64,"+base64.b64encode(raw.replace("COLOR",color).replace("TITLE",label).encode()).decode()
def search_footage(query,avoid=None,used_ids=None):
    used_ids=used_ids or set(); q=tokens(query)-tokens(" ".join(avoid or [])); rows=[]
    for key,kw,color,visual in DEMO:
        k=tokens(kw); overlap=len(q&k); score=min(.82,.25+overlap/max(1,len(q))*.45+overlap/max(1,len(q|k))*.35)
        if "demo-"+key in used_ids: score-=.65
        rows.append((score,key,kw,color,visual))
    rows.sort(reverse=True); score,key,kw,color,visual=rows[0]
    if "demo-"+key in used_ids: score,key,kw,color,visual=next((r for r in rows if "demo-"+r[1] not in used_ids),rows[-1])
    candidate=FootageCandidate("demo-"+key,"scriptflow-local-demo",svg_data(visual,color),"Original procedural SVG placeholder; not certified stock license","ScriptFlow AI local procedural visual",False,True,visual)
    reason=f"Token-overlap selector chose category '{key}'."
    if key=="abstract": reason="Low semantic match confidence; neutral abstract fallback selected."
    return candidate,round(max(0,min(score,1)),3),reason
class FootageProvider:
    name="mock"
    def search(self,query,avoid=None,used_ids=None): return search_footage(query,avoid,used_ids)
def get_footage_provider(): return FootageProvider()
