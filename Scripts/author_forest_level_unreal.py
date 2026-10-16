"""A separate, grassy canopy forest with clearings, side passages, water and a village exit."""
import unreal as u,json,math,random
from pathlib import Path
ROOT=Path('E:/UE5 Projects/AdventureRPG');SOURCE=ROOT/'ContentSource/RuralVillage';F='/Game/Environment/RuralVillage'
assets=u.EditorAssetLibrary;levels=u.get_editor_subsystem(u.LevelEditorSubsystem);actors=u.get_editor_subsystem(u.EditorActorSubsystem)
LEVEL='/Game/Maps/L_EvergroveForest'
if assets.does_asset_exist(LEVEL):
 assert levels.load_level(LEVEL)
else:
 assert levels.new_level_from_template(LEVEL,'/Game/Maps/L_WoodlandBlockout')
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
for volume in actors.get_all_level_actors():
 if isinstance(volume,u.PostProcessVolume):
  volume.modify();settings=volume.get_editor_property('settings')
  settings.set_editor_property('override_color_saturation',True);settings.set_editor_property('color_saturation',u.Vector4(.9,.9,.9,1))
  settings.set_editor_property('override_color_gain',True);settings.set_editor_property('color_gain',u.Vector4(.96,1.0,1.12,1))
  volume.set_editor_property('settings',settings)
for a in actors.get_all_level_actors():
 cls=a.get_class().get_name()
 keep=isinstance(a,(u.WorldSettings,u.DirectionalLight,u.SkyLight,u.SkyAtmosphere,u.ExponentialHeightFog,u.PostProcessVolume,u.CameraActor,u.NavMeshBoundsVolume,u.RecastNavMesh,u.PlayerStart)) or cls in ['BP_WoodlandWorld_C','WorldDataLayers','WorldPartitionMiniMap'] or 'WoodlandWindVisual' in [str(t) for t in a.tags]
 if not keep:actors.destroy_actor(a)
materials={name:u.load_asset(F+'/M_Rural_'+name) for name in json.loads((SOURCE/'palette.json').read_text())}
helper=(ROOT/'Scripts/author_rural_map_unreal.py').read_text();exec(helper[helper.index('mesh_cache={}'):helper.index('# A single continuous ground')])
cube('Forest_GrassGround',(6700,-700,-22),(15000,14000,44),'/Game/Environment/CartoonGround/M_PaintedGrass',True,folder='Forest Terrain')
route=[(9200,1800),(9800,1800),(9800,900),(8700,900),(8700,-350),(7600,-350),(7600,-1500),(6400,-1500),(6400,-300),(5600,-300),(5600,1000),(4600,1000)]
forks=[[(8700,900),(7900,900),(7900,1800)],[(7600,-1500),(8100,-1500),(8100,-2350)],[(5600,1000),(6100,1000),(6100,2100)]]
def expand(p):return (9200+(p[0]-9200)*1.5,1800+(p[1]-1800)*1.5)
route=[expand(p) for p in route];forks=[[expand(p) for p in points] for points in forks]
forks.append([(9200,1800),(9600,1800),(9600,3300),(8900,3300)])
segments=[(a,b) for points in [route]+forks for a,b in zip(points,points[1:])]
exec(compile((ROOT/'Scripts/forest_feature_details.py').read_text(),'forest_feature_details.py','exec'))
def distance(x,y):
 result=1e9
 for a,b in segments:
  dx=b[0]-a[0];dy=b[1]-a[1];t=max(0,min(1,((x-a[0])*dx+(y-a[1])*dy)/(dx*dx+dy*dy)))
  result=min(result,math.hypot(x-a[0]-t*dx,y-a[1]-t*dy))
 return result
rng=random.Random(16216);tree_count=0
for x in range(1740,11900,300):
 for y in range(-5800,4700,300):
  clearing=math.hypot(x-9200,y-1800)<470 or (8700<x<9700 and 1800<y<3200) or water_clearance(x,y)
  if distance(x,y)<390 or clearing:continue
  scale=rng.uniform(.84,1.08);asset='/Game/Environment/BreezeWoodland/SM_BreezeTree_'+rng.choice(['A','B','C'])
  a=place('Forest_CanopyTree',asset,(x,y,0),(scale,scale,scale),folder='Forest Canopy');a.static_mesh_component.set_cast_shadow(False)
  collider('Forest_Thicket',(x,y,0),0,(0,0,120),(292,292,240));tree_count+=1
# Grass passages stay unpaved. Small loose plants break up the clearings without drawing a road.
for i in range(150):
 x=rng.uniform(2000,11500);y=rng.uniform(-5400,4300)
 if distance(x,y)>310 or is_water(x,y):continue
 place('Forest_Wildflowers','/Game/Environment/BreezeWoodland/SM_BreezeFlowers_'+rng.choice(['White','Yellow']),(x,y,2),(.55,.55,.55),folder='Forest Groundcover')
for i in range(90):
 x=rng.uniform(2000,11500);y=rng.uniform(-5400,4300)
 if not 160<distance(x,y)<390 or math.hypot(x-9200,y-1800)<450 or is_water(x,y):continue
 place('Forest_Fern','/Game/Environment/PixelProps/SM_Prop_Bush',(x,y,0),(.45,.45,.45),mat='/Game/Environment/LayeredWoodland/M_StackedLeaf_1',folder='Forest Groundcover')
place_forest_features()
exec(compile((ROOT/'Scripts/riverbank_thickets.py').read_text(),'riverbank_thickets.py','exec'))
fill_riverbanks(place,collider,actors.get_all_level_actors())
NPC=u.load_class(None,'/Game/Game/Characters/NPCs/BP_Npc.BP_Npc_C')
hunter=actors.spawn_actor_from_class(NPC,u.Vector(9010,1740,100));hunter.set_actor_label('Village_Rein');hunter.set_folder_path('Forest Hunter');hunter.set_editor_property('is_spatially_loaded',False)
for k,v in {'NPCName':'Rein','NPCDialogueText':"I'm Rein, a hunter from Evergrove. I found you unconscious. Explore the clearings, cross the old bridge, and look for the western timber gate. The village is beyond the forest.",'HasChoices':False,'CompletesQuestOnInteract':False}.items():hunter.set_editor_property(k,v)
cube('Hunter_Satchel',(8930,1820,35),(80,55,70),materials['Timber'],folder='Forest Hunter')
def passage(label,pos,target,map_label,dest):
 a=actors.spawn_actor_from_class(u.load_class(None,'/Game/Game/World/BP_MapPassage.BP_MapPassage_C'),u.Vector(*pos));a.set_actor_label(label);a.set_editor_property('is_spatially_loaded',False)
 for k,v in {'DestinationMap':target,'DestinationLabel':map_label,'DestinationLocation':u.Vector(*dest),'Radius':135.0}.items():a.set_editor_property(k,v)
 return a
passage('Forest_ExitToVillage',(2150,600,100),'/Game/Maps/L_EvergroveStart','L_EvergroveStart',(3200,0,110))
for y in [400,800]:cube('Forest_ExitGatePost',(2150,y,160),(35,35,320),materials['Timber'],folder='Forest Exit')
cube('Forest_ExitGateBeam',(2150,600,330),(45,440,35),materials['Timber'],folder='Forest Exit')
text('Forest_ExitSign','EVERGROVE',(2350,850,180),24)
for x,y,sx,sy in [(6700,-6000,10400,40),(6700,4800,10400,40),(1700,-600,40,10800),(11800,-600,40,10800)]:cube('Forest_Boundary',(x,y,100),(sx,sy,250),collision=True,visible=False,folder='Collision')
world.get_world_settings().set_editor_property('default_game_mode',u.load_class(None,'/Game/Game/Characters/Player/Blueprints/BP_Gamemode.BP_Gamemode_C'))
for a in actors.get_all_level_actors():
 if isinstance(a,u.PlayerStart):a.modify();a.set_actor_location(u.Vector(9200,1800,110),False,False)
 if isinstance(a,u.CameraActor):a.modify();a.set_actor_rotation(u.Rotator(pitch=-31,yaw=-90,roll=0),False);a.camera_component.set_editor_property('ortho_width',1200)
 if isinstance(a,u.NavMeshBoundsVolume):a.modify();a.set_actor_location(u.Vector(6700,-600,280),False,False);a.set_actor_scale3d(u.Vector(115,115,6))
assert levels.save_current_level();assert u.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
(SOURCE/'forest_layout.json').write_text(json.dumps({'map':LEVEL,'route':route,'forks':forks,'waking_clearing':[9200,1800],'hunter':[9010,1740],'exit':[2150,600],'return_arrival':[2600,600],'water_bodies':water_bodies,'river_x':5750,'forest_scale':1.5,'town_arrival':[3200,0],'trees':tree_count,'unpaved':True},indent=2))
# Town is its own settlement map. Retain its furnished houses and the approach road, remove the prototype eastern forest.
assert levels.load_level('/Game/Maps/L_EvergroveStart')
for a in actors.get_all_level_actors():
 label=a.get_actor_label();p=a.get_actor_location();folder=str(a.get_folder_path())
 remove=(p.x>4500 and p.y>-5000 and (label.startswith(('Forest_','Footpath_','Hunter_','Tree_Trunk')) or folder.startswith('Forest')))
 remove=remove or (p.x>1500 and p.y>-5000 and (label.startswith(('Forest_Tree','Forest_Bush','Tree_Trunk','Wildflowers')))) or label in ['Village_Rein','Village_ReturnToForest','Village_ApproachSign'] or label.startswith('Village_ForestGateway')
 if remove:actors.destroy_actor(a);continue
 if isinstance(a,u.PlayerStart):a.modify();a.set_actor_location(u.Vector(3200,0,110),False,False)
 if label.startswith('World_Boundary') and p.x>10000:a.modify();a.set_actor_location(u.Vector(4300,0,100),False,False)
passage('Village_ReturnToForest',(3600,0,100),'/Game/Maps/L_EvergroveForest','L_EvergroveForest',(2600,600,110))
for y in [-200,200]:cube('Village_ForestGatewayPost',(3600,y,160),(35,35,320),materials['Timber'],folder='Town Approach')
cube('Village_ForestGatewayBeam',(3600,0,330),(45,440,35),materials['Timber'],folder='Town Approach')
text('Village_ApproachSign','EVERGROVE',(3000,260,190),25)
assert levels.save_current_level();assert u.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
u.log('SEPARATE_UNPAVED_FOREST_AND_TOWN_APPROACH_SAVED')

# Restore atmosphere, terrain, and natural prop placement after generated geometry.
exec(compile((ROOT/'Scripts/author_forest_natural_pass_unreal.py').read_text(),'author_forest_natural_pass_unreal.py','exec'),{})
