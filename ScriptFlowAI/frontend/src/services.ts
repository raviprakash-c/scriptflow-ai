import type {Project} from "./types";
import {scenesFromScript} from "./types";
const KEY="scriptflow.projects.v1";
const read=():Project[]=>{try{return JSON.parse(localStorage.getItem(KEY)||"[]") as Project[]}catch{return []}};
const write=(items:Project[])=>localStorage.setItem(KEY,JSON.stringify(items));
export const projectService={
 list:async()=>read(),
 get:async(id:string)=>read().find(p=>p.id===id),
 save:async(project:Project)=>{const all=read();const i=all.findIndex(p=>p.id===project.id);if(i<0)all.unshift(project);else all[i]=project;write(all);return project},
 create:async(input:{title:string;script:string;ratio:"16:9"|"9:16";voice:string;language:string;captions:boolean})=>{const now=new Date().toISOString();const p:Project={id:crypto.randomUUID(),...input,status:"draft",createdAt:now,lastUpdated:now,scenes:scenesFromScript(input.script)};await projectService.save(p);return p},
 remove:async(id:string)=>write(read().filter(p=>p.id!==id)),
 update:async(id:string,patch:Partial<Project>)=>{const p=read().find(x=>x.id===id);if(!p)throw new Error("Project not found");return projectService.save({...p,...patch,lastUpdated:new Date().toISOString()})}
};
export const renderService={
 start:async(id:string)=>projectService.update(id,{status:"queued"}),
 retry:async(id:string)=>projectService.update(id,{status:"draft"})
};
export const integrationStatus={mode:"local-demo" as const,apiBaseUrl:import.meta.env.VITE_API_BASE_URL||"",message:"Local demo adapter active. Connect a backend to create real narration and licensed-footage renders."};