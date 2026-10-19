from typing import Literal
from pydantic import BaseModel,Field,model_validator
AspectRatio=Literal["16:9","9:16","1:1"]
class CaptionOptions(BaseModel):
    burn_in: bool=True
    srt: bool=True
class SceneInput(BaseModel):
    text: str=Field(min_length=1,max_length=5000)
    visual_hint: str|None=Field(default=None,max_length=500)
class JobRequest(BaseModel):
    audio_url: str|None=None
    script: str|None=None
    scenes: list[SceneInput]|None=None
    voice: str="en-IN-female"
    aspect_ratios: list[AspectRatio]=Field(default_factory=lambda:["16:9"])
    style: str="bright, modern, real-world footage"
    avoid: list[str]=Field(default_factory=list)
    captions: CaptionOptions=Field(default_factory=CaptionOptions)
    seed: int=42
    @model_validator(mode="after")
    def validate_input(self):
        modes=int(bool(self.audio_url))+int(bool(self.script and self.script.strip()))+int(bool(self.scenes))
        if modes!=1: raise ValueError("Provide exactly one of audio_url, script, or scenes.")
        if not self.aspect_ratios: raise ValueError("At least one aspect ratio is required.")
        if len(set(self.aspect_ratios))!=len(self.aspect_ratios): raise ValueError("Aspect ratios must not contain duplicates.")
        return self
