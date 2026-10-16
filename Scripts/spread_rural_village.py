"""Expand the village spacing while retaining axis-aligned buildings and walkable yards."""
from build_companion_combat import *
import math,re
PROG='editor_toolset.toolsets.programmatic.ProgrammaticToolset'
p=ROOT/'ContentSource/RuralVillage/layout.json';layout=json.loads(p.read_text())
assert not layout.get('spacing_expanded'),'Spacing revision already applied'
specs=json.loads((p.parent/'buildings.json').read_text())
def spread(point):return [round(780+(point[0]-780)*1.35,2),round(point[1]*1.35,2)]+list(point[2:])
changes=[]
for b in layout['buildings']:
 new=spread(b['position']);changes.append({'name':b['name'],'delta':[new[i]-b['position'][i] for i in range(3)]});b['position']=new
farms=[]
for f in layout['farms']:
 new=spread(f['position']);farms.append({'old':f['position'],'delta':[new[i]-f['position'][i] for i in range(2)]});f['position']=new
for name,points in layout['approaches'].items():layout['approaches'][name]=[spread(v) for v in points]
layout['trail'][-1]=spread(layout['trail'][-1])
layout['trail'][-2]=[780,135]
segments=[]
for a,b in zip(layout['trail'],layout['trail'][1:]):segments.append([a,b,260 if a[0]>800 else 260])
for b in layout['buildings']:
 x,y,z=b['position'];d=specs[b['asset']]['depth'];points=[[x,y+d/2+100]]+layout['approaches'][b['name']]
 for a,c in zip(points,points[1:]):
  if a!=c:segments.append([a,c,190])
body='''import json,math
def tool(n,a):return execute_tool(n,json.dumps(a))['returnValue']
def find(n):return tool('editor_toolset.toolsets.scene.SceneTools.find_actors',{'name':n,'tag':'','collision_channels':[]})
def xf(a):return tool('editor_toolset.toolsets.actor.ActorTools.get_actor_transform',{'actor':a})
def put(a,t):return tool('editor_toolset.toolsets.actor.ActorTools.set_actor_transform',{'actor':a,'xform':t,'worldspace':True})
def run():
 for change in CHANGES:
  dx,dy,dz=change['delta']
  for a in find(change['name']):
   t=xf(a);p=t['location']
   if p['y']<-5000:continue
   p['x']+=dx;p['y']+=dy;put(a,t)
  for a in find(change['name']+'_Exit'):
   prop=json.loads(tool('editor_toolset.toolsets.object.ObjectTools.get_properties',{'instance':a,'properties':['Destination']}))['Destination']
   prop['x']+=dx;prop['y']+=dy
   tool('editor_toolset.toolsets.object.ObjectTools.set_properties',{'instance':a,'values':json.dumps({'Destination':prop})})
 for a in tool('editor_toolset.toolsets.scene.SceneTools.get_actors_in_folder',{'folder_path':'Farms'}):
  t=xf(a);p=t['location'];f=min(FARMS,key=lambda f:(p['x']-f['old'][0])**2+(p['y']-f['old'][1])**2);p['x']+=f['delta'][0];p['y']+=f['delta'][1];put(a,t)
 for folder in ['Forest','Forest Backdrop','Common Ground','Village Signs','Villagers']:
  for a in tool('editor_toolset.toolsets.scene.SceneTools.get_actors_in_folder',{'folder_path':folder}):
   t=xf(a);p=t['location']
   if p['y']<-5000 or p['x']>=1000:continue
   p['x']=780+(p['x']-780)*1.35;p['y']*=1.35;put(a,t)
 ground=find('Village_ContinuousGround')[0];put(ground,{'location':{'x':0,'y':0,'z':-22},'rotation':{'pitch':0,'yaw':0,'roll':0},'scale':{'x':180,'y':140,'z':.44}})
 for a in find('World_Boundary'):
  t=xf(a);p=t['location'];s=t['scale']
  if abs(p['y'])>2000:p['x']=200;p['y']=3300 if p['y']>0 else -3300;s['x']=90
  else:p['x']=-4300 if p['x']<0 else 4680;s['y']=66
  put(a,t)
'''
# Reuse the road authoring operations, without repeating the straightening migration.
s=(ROOT/'Scripts/straighten_rural_layout.py').read_text();roads=s[s.index(" for a in tool('editor_toolset.toolsets.scene.SceneTools.get_actors_in_folder',{'folder_path':'Paths'})"):s.index(" return {'axis_aligned_buildings'")]
body+=roads+" return {'spacing_multiplier':1.35,'paths':len(SEGMENTS)}\n"
for k,v in [('CHANGES',changes),('FARMS',farms),('SEGMENTS',segments)]:body=body.replace(k,json.dumps(v))
print(call('execute_tool_script',{'script':body},PROG),flush=True)
layout['spacing_expanded']=1.35;p.write_text(json.dumps(layout,indent=2))
builder=ROOT/'Scripts/author_rural_map_unreal.py';s=builder.read_text()
s=re.sub(r'buildings=\[.*?\]\napproaches=', 'buildings='+repr([(b['name'],b['asset'],tuple(b['position']),0) for b in layout['buildings']])+'\napproaches=',s,flags=re.S)
s=re.sub(r'approaches=\{.*?\}\nfor index', 'approaches='+repr(layout['approaches'])+'\nfor index',s,flags=re.S)
s=re.sub(r'farm_plots=\[.*?\]\nfor fi', 'farm_plots='+repr([(f['position'][0],f['position'][1],f['size'][0],f['size'][1],f['crop'],0) for f in layout['farms']])+'\nfor fi',s,flags=re.S)
s=re.sub(r'trail=\[.*?\]\nfor i,', 'trail='+repr(layout['trail'])+'\nfor i,',s,flags=re.S)
s=s.replace('(12000,10000,44)','(18000,14000,44)').replace('path_segment(a,b,125,','path_segment(a,b,190,').replace('240 if a[0]>800 else 190','260')
builder.write_text(s)
W='/Game/Game/World/BP_WoodlandWorld.BP_WoodlandWorld'
code=(ROOT/'Saved/CombatAudit/UpdateCamera.dsl').read_text().replace('-2700.0 4300.0','-3950.0 4300.0').replace('-1900.0 1900.0','-3000.0 3000.0')
graph(W,'UpdateCamera',code);call('compile_blueprint',{'blueprint':ref(W),'warnings_as_errors':True})
call('save_assets',{'asset_paths':['/Game/Maps/L_EvergroveStart',W]},ASSET)
print('SPACIOUS_VILLAGE_SAVED',flush=True)
