"""Fill the forest backdrop and remove prototype encounter rows from the new town."""
from build_companion_combat import *
import random,math
PROG='editor_toolset.toolsets.programmatic.ProgrammaticToolset'
layout=json.loads((ROOT/'ContentSource/RuralVillage/layout.json').read_text());specs=json.loads((ROOT/'ContentSource/RuralVillage/buildings.json').read_text())
rng=random.Random(5151);trees=[]
for side in [-1,1]:
 for row in range(3):
  for x in range(-3650,1250,430):trees.append({'x':x+rng.uniform(-150,150),'y':side*(2500+row*440+rng.uniform(-140,140)),'scale':rng.uniform(.78,1.22),'asset':'/Game/Environment/BreezeWoodland/SM_BreezeTree_'+rng.choice(['A','B','C'])})
for y in range(-2200,2300,430):
 for x in [-3500,-3900]:trees.append({'x':x+rng.uniform(-100,100),'y':y+rng.uniform(-120,120),'scale':rng.uniform(.8,1.2),'asset':'/Game/Environment/BreezeWoodland/SM_BreezeTree_'+rng.choice(['A','B','C'])})
floors=[{'name':b['name'],'pos':b['position'],'yaw':b['yaw'],'width':specs[b['asset']]['width'],'depth':specs[b['asset']]['depth']} for b in layout['buildings']]
script='''import json,math
def tool(n,a):return execute_tool(n,json.dumps(a))['returnValue']
def run():
 ground=tool('editor_toolset.toolsets.scene.SceneTools.find_actors',{'name':'Village_ContinuousGround','tag':'','collision_channels':[]})[0]
 tool('editor_toolset.toolsets.actor.ActorTools.set_actor_transform',{'actor':ground,'xform':{'scale':{'x':120,'y':100,'z':.44}},'worldspace':True})
 for actor in tool('editor_toolset.toolsets.scene.SceneTools.find_actors',{'name':'Forest_Tree','tag':'','collision_channels':[]}):
  xf=tool('editor_toolset.toolsets.actor.ActorTools.get_actor_transform',{'actor':actor});p=xf['location']
  if p['x']<950 and abs(p['y'])>2000:
   p['y']=(1 if p['y']>0 else -1)*(2800+140*math.sin(p['x']*.013))
   tool('editor_toolset.toolsets.actor.ActorTools.set_actor_transform',{'actor':actor,'xform':xf,'worldspace':True})
 for index,t in enumerate(TREES):
  a=tool('editor_toolset.toolsets.scene.SceneTools.add_to_scene_from_asset',{'asset_path':t['asset'],'name':'Rural_BackdropTree_'+str(index),'xform':{'location':{'x':t['x'],'y':t['y'],'z':0},'scale':{'x':t['scale'],'y':t['scale'],'z':t['scale']}},'snap_to_ground':False})
  tool('editor_toolset.toolsets.scene.SceneTools.set_actor_folder',{'actor':a,'folder_path':'Forest Backdrop'})
 for item in FLOORS:
  a=tool('editor_toolset.toolsets.scene.SceneTools.add_to_scene_from_asset',{'asset_path':'/Engine/BasicShapes/Cube','name':item['name']+'_PorchFloor','xform':{'location':{'x':item['pos'][0],'y':item['pos'][1],'z':28},'rotation':{'pitch':0,'yaw':item['yaw'],'roll':0},'scale':{'x':item['width']/100,'y':item['depth']/100,'z':.14}},'snap_to_ground':False})
  c=tool('editor_toolset.toolsets.actor.ActorTools.get_components',{'actor':a,'component_type':{'refPath':'/Script/Engine.StaticMeshComponent'}})[0]
  tool('editor_toolset.toolsets.object.ObjectTools.set_properties',{'instance':c,'values':json.dumps({'OverrideMaterials':['/Game/Environment/RuralVillage/M_Rural_Timber.M_Rural_Timber'],'bUseDefaultCollision':False,'BodyInstance':{'CollisionProfileName':'NoCollision','CollisionEnabled':'NoCollision'},'bCanEverAffectNavigation':False})})
 return {'backdrop_trees':len(TREES),'wooden_thresholds':len(FLOORS)}
'''.replace('TREES',json.dumps(trees)).replace('FLOORS',json.dumps(floors))
print(call('execute_tool_script',{'script':script},PROG),flush=True)
source=ROOT/'Saved/CombatAudit/Setup.dsl';code=source.read_text()
start=code.index('(bind beast0');end=code.index('(Utilities|Time|SetTimerbyFunctionName',start)
encounters=code[start:end]
if 'L_EvergroveStart' not in code:
 code=code[:start]+'(if (not (Utilities|String|EqualExactly(String) (Game|GetCurrentLevelName :bRemovePrefixString true) "L_EvergroveStart")) '+encounters+') '+code[end:]
 graph(DIRECTOR,'Setup',code)
 call('compile_blueprint',{'blueprint':ref(DIRECTOR),'warnings_as_errors':True})
call('save_assets',{'asset_paths':['/Game/Maps/L_EvergroveStart',DIRECTOR]},ASSET)
print('RURAL_BACKDROP_AND_CLEAN_START_SAVED',flush=True)
