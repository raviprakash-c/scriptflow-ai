import re
from dataclasses import dataclass
@dataclass
class PlannedScene:
    text:str
    visual_hint:str|None
    start:float
    end:float
_SPLIT=re.compile(r"(?<=[.!?。！？])\\s+|\\n+")
def split_script(script:str)->list[str]:
    clean=re.sub(r"\\s+"," ",script).strip()
    if not clean: return []
    out=[]
    for sentence in (s.strip() for s in _SPLIT.split(clean) if s.strip()):
        words=sentence.split()
        out.extend([sentence] if len(words)<=34 else [" ".join(words[i:i+24]) for i in range(0,len(words),24)])
    return out
def estimate_word_duration(text:str)->float:
    words=max(1,len(re.findall(r"\\b[\\w'-]+\\b",text)))
    pause=sum(text.count(x) for x in ",;:")*.12+sum(text.count(x) for x in ".!?。！？")*.22
    return max(2.5,words/145*60+pause)
def plan_scenes(texts:list[tuple[str,str|None]],total_duration:float|None=None)->list[PlannedScene]:
    if not texts: return []
    weights=[estimate_word_duration(t) for t,_ in texts]; total=total_duration or sum(weights)
    if total<=0: raise ValueError("Duration must be positive")
    ds=[total*w/sum(weights) for w in weights]; cur=0.; out=[]
    for (text,hint),d in zip(texts,ds):
        out.append(PlannedScene(text,hint,round(cur,3),round(cur+d,3))); cur+=d
    out[-1].end=round(total,3)
    return out
