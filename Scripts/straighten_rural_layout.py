"""Keep staggered town positions, square structures and yards to the world axes."""
from build_companion_combat import *
import math,re
PROG='editor_toolset.toolsets.programmatic.ProgrammaticToolset'
source=ROOT/'ContentSource/RuralVillage/layout.json'
layout=json.loads(source.read_text())
approaches={
 'LocalGuild':[(-180,-340),(-180,100)],
 'MaraCottage':[(-1530,-600),(-1530,100)],
 'TobinCottage':[(-2310,300),(-1850,300),(-1850,100)],
 'NellCottage':[(-1210,1120),(-1660,1120),(-1660,100)],
 'OrchardCottage':[(-110,1720),(-650,1720),(-650,100)],
 'TrailCottage':[(610,1000),(1050,1000),(1050,100),(780,100)],
 'FarmBarn':[(-2380,1690),(-1740,1690),(-1740,100)],
 'EdgeCottage':[(460,-1280),(460,-700),(650,-700),(650,100)]}
trail=[(4400,360),(3900,360),(3550,260),(3200,100),(2900,-80),(2500,-40),(2200,140),(1850,110),(1500,-40),(1100,-70),(780,100),(-1850,100)]
if layout.get('spacing_expanded'):
 approaches=layout['approaches'];trail=layout['trail']
specs=json.loads((ROOT/'ContentSource/RuralVillage/buildings.json').read_text())
segments=[]
for a,b in zip(trail,trail[1:]):segments.append([a,b,240 if a[0]>800 else 190])
for b in layout['buildings']:
 x,y,z=b['position'];d=specs[b['asset']]['depth'];points=[(x,y+d/2+150)]+approaches[b['name']]
 for a,c in zip(points,points[1:]):
  if a!=c:segments.append([a,c,125])
script='''import json,math
def tool(n,a):return execute_tool(n,json.dumps(a))['returnValue']
def find(n):return tool('editor_toolset.toolsets.scene.SceneTools.find_actors',{'name':n,'tag':'','collision_channels':[]})
def xf(a):return tool('editor_toolset.toolsets.actor.ActorTools.get_actor_transform',{'actor':a})
def put(a,t):return tool('editor_toolset.toolsets.actor.ActorTools.set_actor_transform',{'actor':a,'xform':t,'worldspace':True})
def run():
 exterior=[]
 for folder in ['Buildings','Collision','Doors','Lighting','Village Signs']:
  exterior+=tool('editor_toolset.toolsets.scene.SceneTools.get_actors_in_folder',{'folder_path':folder})
 for b in BUILDINGS:
  origin=b['position'];angle=math.radians(-b['yaw'])
  for a in find(b['name']):
   if a not in exterior:continue
   t=xf(a);p=t['location']
   if p['y']<-5000:continue
   dx=p['x']-origin[0];dy=p['y']-origin[1]
   p['x']=origin[0]+dx*math.cos(angle)-dy*math.sin(angle);p['y']=origin[1]+dx*math.sin(angle)+dy*math.cos(angle)
   t['rotation']['yaw']-=b['yaw'];put(a,t)
  front={'x':origin[0],'y':origin[1]+SPECS[b['asset']]['depth']/2+215,'z':100}
  for a in find(b['name']+'_Exit'):
   tool('editor_toolset.toolsets.object.ObjectTools.set_properties',{'instance':a,'values':json.dumps({'Destination':front})})
 for a in find('VillageGuildSign'):
  p=BUILDINGS[0]['position'];put(a,{'location':{'x':p[0],'y':p[1]+SPECS[BUILDINGS[0]['asset']]['depth']/2+50,'z':370},'rotation':{'pitch':0,'yaw':90,'roll':0}})
 for a in tool('editor_toolset.toolsets.scene.SceneTools.get_actors_in_folder',{'folder_path':'Farms'}):
  t=xf(a);p=t['location'];f=min(FARMS,key=lambda f:(p['x']-f['position'][0])**2+(p['y']-f['position'][1])**2)
  x,y=f['position'];angle=math.radians(-f['yaw']);dx=p['x']-x;dy=p['y']-y
  p['x']=x+dx*math.cos(angle)-dy*math.sin(angle);p['y']=y+dx*math.sin(angle)+dy*math.cos(angle);t['rotation']['yaw']-=f['yaw'];put(a,t)
 for a in tool('editor_toolset.toolsets.scene.SceneTools.get_actors_in_folder',{'folder_path':'Paths'}):tool('editor_toolset.toolsets.scene.SceneTools.remove_from_scene',{'actor':a})
 for i,s in enumerate(SEGMENTS):
  a,b,w=s;dx=b[0]-a[0];dy=b[1]-a[1];length=math.sqrt(dx*dx+dy*dy)
  t={'location':{'x':(a[0]+b[0])/2,'y':(a[1]+b[1])/2,'z':3},'rotation':{'pitch':0,'yaw':math.degrees(math.atan2(dy,dx)),'roll':0},'scale':{'x':(length+w*.55)/100,'y':w/100,'z':.05}}
  actor=tool('editor_toolset.toolsets.scene.SceneTools.add_to_scene_from_asset',{'asset_path':'/Engine/BasicShapes/Cube','name':'Village_Path_'+str(i),'xform':t,'snap_to_ground':False})
  tool('editor_toolset.toolsets.scene.SceneTools.set_actor_folder',{'actor':actor,'folder_path':'Paths'})
  c=tool('editor_toolset.toolsets.actor.ActorTools.get_components',{'actor':actor,'component_type':{'refPath':'/Script/Engine.StaticMeshComponent'}})[0]
  tool('editor_toolset.toolsets.object.ObjectTools.set_properties',{'instance':c,'values':json.dumps({'OverrideMaterials':['/Game/Environment/CartoonGround/M_PaintedRoad.M_PaintedRoad'],'bUseDefaultCollision':False,'BodyInstance':{'CollisionProfileName':'NoCollision','CollisionEnabled':'NoCollision'},'bCanEverAffectNavigation':False})})
 return {'axis_aligned_buildings':len(BUILDINGS),'axis_aligned_farms':len(FARMS),'paths':len(SEGMENTS)}
'''
for key,value in [('BUILDINGS',layout['buildings']),('FARMS',layout['farms']),('SPECS',specs),('SEGMENTS',segments)]:script=script.replace(key,json.dumps(value))
print(call('execute_tool_script',{'script':script},PROG),flush=True)
call('save_assets',{'asset_paths':['/Game/Maps/L_EvergroveStart']},ASSET)
for b in layout['buildings']:b['yaw']=0
for f in layout['farms']:f['yaw']=0
layout['layout_style']='Axis-aligned, staggered village blocks inspired by Pokemon town layouts'
layout['trail']=trail;layout['approaches']=approaches
source.write_text(json.dumps(layout,indent=2))
p=ROOT/'Scripts/author_rural_map_unreal.py';s=p.read_text()
s=re.sub(r'buildings=\[.*?\]\napproaches=', 'buildings='+repr([(b['name'],b['asset'],tuple(b['position']),0) for b in layout['buildings']])+'\napproaches=',s,flags=re.S)
s=re.sub(r'approaches=\{.*?\}\nfor index', 'approaches='+repr(approaches)+'\nfor index',s,flags=re.S)
s=re.sub(r'farm_plots=\[.*?\]\nfor fi', 'farm_plots='+repr([(f['position'][0],f['position'][1],f['size'][0],f['size'][1],f['crop'],0) for f in layout['farms']])+'\nfor fi',s,flags=re.S)
s=re.sub(r'trail=\[.*?\]\nfor i,', 'trail='+repr(trail)+'\nfor i,',s,flags=re.S)
p.write_text(s)
print('STRAIGHT_STAGGERED_LAYOUT_SAVED',flush=True)
