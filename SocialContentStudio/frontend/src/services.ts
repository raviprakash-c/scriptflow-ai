import type {Campaign,Post} from "./types";import {sampleCampaign,samplePosts} from "./types";
const CK="socialstudio.campaigns.v1",PK="socialstudio.posts.v1";
function read<T>(key:string,fallback:T):T{try{const x=localStorage.getItem(key);return x?JSON.parse(x) as T:fallback}catch{return fallback}}
function write<T>(key:string,value:T){localStorage.setItem(key,JSON.stringify(value))}
const campaigns=()=>read<Campaign[]>(CK,[sampleCampaign]);const posts=()=>read<Post[]>(PK,samplePosts);
export const studioService={
 listCampaigns:async()=>campaigns(),listPosts:async()=>posts(),
 saveCampaign:async(c:Campaign)=>{const all=campaigns(),i=all.findIndex(x=>x.id===c.id);if(i<0)all.unshift(c);else all[i]=c;write(CK,all);return c},
 createCampaign:async(input:Omit<Campaign,"id"|"createdAt">)=>{const c:Campaign={...input,id:crypto.randomUUID(),createdAt:new Date().toISOString()};await studioService.saveCampaign(c);return c},
 savePost:async(p:Post)=>{const all=posts(),i=all.findIndex(x=>x.id===p.id);if(i<0)all.unshift(p);else all[i]=p;write(PK,all);return p},
 updatePost:async(id:string,patch:Partial<Post>)=>{const p=posts().find(x=>x.id===id);if(!p)throw new Error("Post not found");return studioService.savePost({...p,...patch,updatedAt:new Date().toISOString(),source:"user-edited"})},
 deletePost:async(id:string)=>write(PK,posts().filter(p=>p.id!==id)),
 generate:async(campaign:Campaign,count:number)=>{const existing=posts();const created:Post[]=[];const templates=[
{hook:"A small change can make a meaningful difference.",text:"Progress does not always need a big launch. Start with one useful change, notice what improves, and build from there.",cta:"What small change will you try this week?",hashtags:["SmallSteps","BetterEveryday","Growth"]},
{hook:"Here is your reminder to keep it simple.",text:"The most sustainable plan is the one you can return to. Keep the next step clear, make it manageable, and give yourself room to learn.",cta:"Save this for your next planning session.",hashtags:["SimpleSystems","BuildBetter","Consistency"]},
{hook:"Good ideas deserve a practical next step.",text:"Inspiration is a start. A clear action turns it into progress. Choose one thing you can do today and make it easy to begin.",cta:"Share one action you are taking today.",hashtags:["IdeasIntoAction","DailyProgress","Marketing"]}];
for(let i=0;i<count;i++){const t=templates[i%templates.length],platform=campaign.platforms[i%campaign.platforms.length];const p:Post={id:crypto.randomUUID(),campaignId:campaign.id,platform,hook:t.hook,text:t.text+"\n\n"+campaign.topic+".",cta:t.cta,hashtags:t.hashtags,status:"draft",plannedDate:"",createdAt:new Date().toISOString(),updatedAt:new Date().toISOString(),source:"generated-sample"};created.push(p)}
write(PK,[...created,...existing]);return created},
exportCSV:()=>{const esc=(v:string)=>'"'+v.replace(/"/g,'""')+'"';const header=["post_id","campaign","platform","status","planned_date","hook","text","cta","hashtags","source"];const cs=campaigns();return [header.map(esc).join(","),...posts().map(p=>[p.id,cs.find(c=>c.id===p.campaignId)?.name||"Unknown campaign",p.platform,p.status,p.plannedDate,p.hook,p.text,p.cta,p.hashtags.join(" "),p.source].map(esc).join(","))].join("\n")},
resetSamples:()=>{write(CK,[sampleCampaign]);write(PK,samplePosts)}
};
export const integrations={apiBaseUrl:import.meta.env.VITE_API_BASE_URL||"",mode:"local-demo",publishing:"not-connected"};