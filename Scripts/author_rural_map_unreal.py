"""Run in a hidden Unreal editor: import original village meshes and build a new map.

The old woodland/guild map and every original guild asset remain untouched.
"""
import unreal as u,json,math,random
from pathlib import Path
ROOT=Path('E:/UE5 Projects/AdventureRPG');SOURCE=ROOT/'ContentSource/RuralVillage'
F='/Game/Environment/RuralVillage';LEVEL='/Game/Maps/L_EvergroveStart'
tools=u.AssetToolsHelpers.get_asset_tools();levels=u.get_editor_subsystem(u.LevelEditorSubsystem);actors=u.get_editor_subsystem(u.EditorActorSubsystem)
assets=u.EditorAssetLibrary;mel=u.MaterialEditingLibrary
palette=json.loads((SOURCE/'palette.json').read_text());specs=json.loads((SOURCE/'buildings.json').read_text())
materials={}
for name,rgb in palette.items():
 path=F+'/M_Rural_'+name
 if assets.does_asset_exist(path):
  materials[name]=u.load_asset(path)
  continue
 mat=u.load_asset(path) if assets.does_asset_exist(path) else tools.create_asset('M_Rural_'+name,F,u.Material,u.MaterialFactoryNew())
 mel.delete_all_material_expressions(mat)
 color=mel.create_material_expression(mat,u.MaterialExpressionConstant3Vector)
 color.set_editor_property('constant',u.LinearColor(*rgb,1))
 mel.connect_material_property(color,'',u.MaterialProperty.MP_BASE_COLOR)
 rough=mel.create_material_expression(mat,u.MaterialExpressionConstant);rough.set_editor_property('r',.92)
 mel.connect_material_property(rough,'',u.MaterialProperty.MP_ROUGHNESS)
 mat.set_editor_property('two_sided',True)
 if name=='Glass':
  night=mel.create_material_expression(mat,u.MaterialExpressionCollectionParameter)
  night.set_editor_property('collection',u.load_asset('/Game/Environment/DayNight/MPC_WorldClock'))
  night.set_editor_property('parameter_name','NightGlow')
  glow=mel.create_material_expression(mat,u.MaterialExpressionMultiply)
  mel.connect_material_expressions(color,'',glow,'A');mel.connect_material_expressions(night,'',glow,'B')
  mel.connect_material_property(glow,'',u.MaterialProperty.MP_EMISSIVE_COLOR)
 mel.recompile_material(mat);assets.save_loaded_asset(mat);materials[name]=mat
for item in json.loads((SOURCE/'manifest.json').read_text()):
 name=item['name'];path=F+'/'+name
 if assets.does_asset_exist(path):continue
 if not assets.does_asset_exist(path):
  task=u.AssetImportTask();task.filename=item['file'];task.destination_path=F;task.destination_name=name;task.automated=True;task.save=True
  options=u.FbxImportUI();options.import_materials=False;options.import_textures=False;options.import_mesh=True;options.mesh_type_to_import=u.FBXImportType.FBXIT_STATIC_MESH
  options.static_mesh_import_data.combine_meshes=True;options.static_mesh_import_data.auto_generate_collision=False
  task.options=options;tools.import_asset_tasks([task])
 mesh=u.load_asset(path);assert mesh,path
 for index,slot in enumerate(mesh.get_editor_property('static_materials')):
  key=str(slot.get_editor_property('material_slot_name'));mesh.set_material(index,materials[key])
 u.get_editor_subsystem(u.StaticMeshEditorSubsystem).remove_collisions(mesh)
 assets.save_loaded_asset(mesh)
if assets.does_asset_exist(LEVEL):
 # Only this newly generated map is reset after an incomplete authoring run.
 assert assets.delete_asset(LEVEL)
 assert levels.new_level_from_template(LEVEL,'/Game/Maps/L_WoodlandBlockout')
else:assert levels.new_level_from_template(LEVEL,'/Game/Maps/L_WoodlandBlockout')
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
all_before=actors.get_all_level_actors();kept=[]
for actor in all_before:
 cls=actor.get_class().get_name();label=actor.get_actor_label();tags=[str(t) for t in actor.tags]
 retain=isinstance(actor,(u.WorldSettings,u.DirectionalLight,u.SkyLight,u.SkyAtmosphere,u.ExponentialHeightFog,u.PostProcessVolume,u.CameraActor,u.NavMeshBoundsVolume,u.RecastNavMesh,u.PlayerStart)) or cls in ['BP_WoodlandWorld_C','WorldDataLayers','WorldPartitionMiniMap'] or 'WoodlandWindVisual' in tags
 if retain:kept.append(actor)
 else:actors.destroy_actor(actor)
world.get_world_settings().set_editor_property('default_game_mode',u.load_class(None,'/Game/Game/Characters/Player/Blueprints/BP_Gamemode.BP_Gamemode_C'))
rng=random.Random(20261015);report={'map':LEVEL,'buildings':[],'farms':[],'trees':0,'interiors':[],'kept_original_assets':True}
mesh_cache={};mat_cache={}
def mesh(path):
 if path not in mesh_cache:mesh_cache[path]=u.load_asset(path)
 assert mesh_cache[path],path
 return mesh_cache[path]
def material(path):
 if path not in mat_cache:mat_cache[path]=u.load_asset(path)
 return mat_cache[path]
def place(label,path,pos,scale=(1,1,1),yaw=0,mat=None,collision=False,folder='Rural Village'):
 actor=actors.spawn_actor_from_class(u.StaticMeshActor,u.Vector(*pos),u.Rotator(pitch=0,yaw=yaw,roll=0));assert actor,label
 actor.set_actor_label(label);actor.set_folder_path(folder)
 if folder in ['Interiors','Collision','Doors','Lighting']:actor.set_editor_property('is_spatially_loaded',False)
 c=actor.static_mesh_component;c.set_static_mesh(mesh(path));c.set_world_scale3d(u.Vector(*scale))
 c.set_editor_property('use_default_collision',False)
 c.set_collision_profile_name('BlockAll' if collision else 'NoCollision')
 c.set_collision_enabled(u.CollisionEnabled.QUERY_AND_PHYSICS if collision else u.CollisionEnabled.NO_COLLISION)
 c.set_editor_property('can_ever_affect_navigation',collision)
 if mat:c.set_material(0,material(mat) if isinstance(mat,str) else mat)
 return actor
def cube(label,pos,size,mat=None,collision=False,visible=True,folder='Rural Village'):
 a=place(label,'/Engine/BasicShapes/Cube',pos,tuple(v/100 for v in size),mat=mat,collision=collision,folder=folder)
 if not visible:a.static_mesh_component.set_visibility(False);a.set_actor_hidden_in_game(True)
 return a
def local(origin,yaw,offset):
 a=math.radians(yaw);x,y,z=offset
 return (origin[0]+x*math.cos(a)-y*math.sin(a),origin[1]+x*math.sin(a)+y*math.cos(a),origin[2]+z)
def collider(label,origin,yaw,offset,size):
 a=cube(label,local(origin,yaw,offset),size,collision=True,visible=False,folder='Collision');a.set_actor_rotation(u.Rotator(pitch=0,yaw=yaw,roll=0),False);return a
def light(label,pos,intensity=350,radius=270,tag=None):
 a=actors.spawn_actor_from_class(u.PointLight,u.Vector(*pos));a.set_actor_label(label);a.set_folder_path('Lighting')
 a.set_editor_property('is_spatially_loaded',False)
 c=a.point_light_component;c.set_mobility(u.ComponentMobility.MOVABLE);c.set_intensity_units(u.LightUnits.LUMENS);c.set_intensity(intensity);c.set_attenuation_radius(radius);c.set_light_color(u.LinearColor(1,.70,.38),False);c.set_cast_shadows(False)
 if tag:a.tags=[tag]
 return a
def text(label,value,pos,size=35,yaw=90):
 a=actors.spawn_actor_from_class(u.TextRenderActor,u.Vector(*pos),u.Rotator(pitch=0,yaw=yaw,roll=0));a.set_actor_label(label);a.set_folder_path('Village Signs')
 c=a.text_render;c.set_text(value);c.set_world_size(size);c.set_horizontal_alignment(u.HorizTextAligment.EHTA_CENTER);c.set_text_render_color(u.Color(233,216,167,255));return a
def portal(label,pos,yaw,destination,leaf=None,width=70):
 a=actors.spawn_actor_from_class(u.load_class(None,'/Game/Game/World/BP_WalkThroughDoor.BP_WalkThroughDoor_C'),u.Vector(*pos),u.Rotator(pitch=0,yaw=yaw,roll=0));a.set_actor_label(label);a.set_folder_path('Doors')
 a.set_editor_property('is_spatially_loaded',False)
 for key,value in {'Destination':u.Vector(*destination),'DestinationYaw':180.0 if yaw<90 else 0.0,'TriggerWidth':float(width),'TriggerDepth':110.0,'LeftLeaf':leaf}.items():a.set_editor_property(key,value)
 return a
# A single continuous ground surface, winding trail, and branching footpaths.
grass='/Game/Environment/CartoonGround/M_PaintedGrass';road='/Game/Environment/CartoonGround/M_PaintedRoad'
cube('Village_ContinuousGround',(700,0,-22),(26000,16000,44),grass,True,folder='Terrain')
path_segments=[]
def path_segment(a,b,width,label):
 path_segments.append((a,b,width))
 dx=b[0]-a[0];dy=b[1]-a[1];length=math.hypot(dx,dy)
 # Rounded ends overlap organically instead of forming a street grid.
 obj=cube(label,((a[0]+b[0])/2,(a[1]+b[1])/2,3),(length+width*.55,width,5),road,folder='Paths');obj.set_actor_rotation(u.Rotator(pitch=0,yaw=math.degrees(math.atan2(dy,dx)),roll=0),False)
 for endpoint in [a,b]:place(label+'_SoftEnd','/Engine/BasicShapes/Cylinder',(endpoint[0],endpoint[1],3),(width/100,width/100,.055),mat=road,folder='Paths')
trail=[[9200,1800],[9800,1800],[9800,900],[8700,900],[8700,-350],[7600,-350],[7600,-1500],[6400,-1500],[6400,-300],[5600,-300],[5600,1000],[4700,1000],[4700,360],[4400, 360], [3900, 360], [3550, 260], [3200, 100], [2900, -80], [2500, -40], [2200, 140], [1850, 110], [1500, -40], [1100, -70], [780, 100], [-2770.5, 135.0]]
for i,(a,b) in enumerate(zip(trail,trail[1:])):path_segment(a,b,260,'Footpath_'+str(i))
forest_forks=[[(8700,900),(7900,900),(7900,1800)],[(7600,-1500),(8100,-1500),(8100,-2350)],[(5600,1000),(6100,1000),(6100,2100)]]
for fi,points in enumerate(forest_forks):
 for ai,(a,b) in enumerate(zip(points,points[1:])):path_segment(a,b,220,'ForestFork_'+str(fi)+'_'+str(ai))
buildings=[('LocalGuild', 'SM_RuralGuildHall', (-516.0, -1215.0, 0), 0), ('MaraCottage', 'SM_RuralCottage_A', (-2338.5, -1458.0, 0), 0), ('TobinCottage', 'SM_RuralCottage_B', (-3391.5, -216.0, 0), 0), ('NellCottage', 'SM_RuralCottage_C', (-1906.5, 1053.0, 0), 0), ('OrchardCottage', 'SM_RuralCottage_B', (-421.5, 1782.0, 0), 0), ('TrailCottage', 'SM_RuralCottage_C', (550.5, 864.0, 0), 0), ('FarmBarn', 'SM_RuralBarn', (-3486.0, 1687.5, 0), 0), ('EdgeCottage', 'SM_RuralCottage_C', (348.0, -2214.0, 0), 0)]
approaches={'LocalGuild': [[-516.0, -459.0], [-516.0, 135.0]], 'MaraCottage': [[-2338.5, -810.0], [-2338.5, 135.0]], 'TobinCottage': [[-3391.5, 405.0], [-2770.5, 405.0], [-2770.5, 135.0]], 'NellCottage': [[-1906.5, 1512.0], [-2514.0, 1512.0], [-2514.0, 135.0]], 'OrchardCottage': [[-421.5, 2322.0], [-1150.5, 2322.0], [-1150.5, 135.0]], 'TrailCottage': [[550.5, 1350.0], [1144.5, 1350.0], [1144.5, 135.0], [780.0, 135.0]], 'FarmBarn': [[-3486.0, 2281.5], [-2622.0, 2281.5], [-2622.0, 135.0]], 'EdgeCottage': [[348.0, -1728.0], [348.0, -945.0], [604.5, -945.0], [604.5, 135.0]]}
exec(compile((ROOT/'Scripts/rural_interior_details.py').read_text(),'rural_interior_details.py','exec'))
for index,(name,asset,origin,yaw) in enumerate(buildings):
 spec=specs[asset];w=spec['width'];d=spec['depth'];h=spec['height'];door=spec['door'];guild=name=='LocalGuild'
 place(name,F+'/'+asset,origin,yaw=yaw,folder='Buildings')
 floor=cube(name+'_PorchFloor',(origin[0],origin[1],28),(w,d,14),materials['Timber'],folder='Buildings');floor.set_actor_rotation(u.Rotator(pitch=0,yaw=yaw,roll=0),False)
 for offset,size,suffix in [((0,-d/2,180),(w,28,360),'Back'),((-w/2,0,180),(28,d,360),'Left'),((w/2,0,180),(28,d,360),'Right')]:collider(name+'_'+suffix,origin,yaw,offset,size)
 for side in [-1,1]:collider(name+'_Front'+str(side),origin,yaw,(side*(w+door)/4,d/2,140),((w-door)/2,25,280))
 doorpos=local(origin,yaw,(-door/2,d/2+19,38));leaf=place(name+'_DoorLeaf',F+'/SM_RuralDoor',doorpos,(door/120,1,1),yaw=yaw,folder='Doors');leaf.static_mesh_component.set_mobility(u.ComponentMobility.MOVABLE)
 front=local(origin,yaw,(0,d/2+55,0))
 points=[(front[0],front[1]+95)]+approaches[name]
 for ai,(a,b) in enumerate(zip(points,points[1:])):path_segment(a,b,190,name+'_Approach'+str(ai))
 for wi,window in enumerate(spec['windows']):light(name+'_WindowLight'+str(wi),local(origin,yaw,(window[0],window[1]+55,window[2])),tag='RuralWindowLight')
 room=(index*12000,-22000 if guild else -34000,0)
 rw,rd=(2600,2100) if guild else ((2600,2200) if name=='FarmBarn' else ((2500,1900) if asset=='SM_RuralCottage_B' else (2200,1800)))
 cube(name+'_InteriorFloor',(room[0],room[1],0),(rw,rd,24),materials['Plank'],True,folder='Interiors')
 for offset,size,suffix in [((0,-rd/2,185),(rw,24,370),'Back'),((-rw/2,0,185),(24,rd,370),'Left'),((rw/2,0,185),(24,rd,370),'Right')]:cube(name+'_Interior_'+suffix,local(room,0,offset),size,materials['PlankLight'],True,folder='Interiors')
 for sx in [-1,1]:cube(name+'_InteriorFront'+str(sx),(room[0]+sx*(rw+160)/4,room[1]+rd/2,110),((rw-160)/2,24,220),materials['Timber'],True,folder='Interiors')
 for x in [-rw/2+20,rw/2-20]:cube(name+'_InteriorBeam',(room[0]+x,room[1],335),(26,rd,26),materials['Timber'],folder='Interiors')
 cube(name+'_InteriorRug',(room[0],room[1]+30,14),(rw*.48,rd*.43,3),materials['Moss'],folder='Interiors')
 zone=cube(name+'_StableInterior',(room[0],room[1],180),(rw+80,rd+80,420),visible=False,folder='Lighting');zone.tags=['StableInteriorLighting']
 light(name+'_InteriorLight',(room[0],room[1]-80,280),800,950)
 furnish_room(name,room,rw,rd,guild,name=='FarmBarn',index)
 if guild:text('VillageGuildSign','GUILD',local(origin,yaw,(0,d/2+50,370)),31,90)
 portal(name+'_Entrance',front,yaw,(room[0],room[1]+rd/2-190,100),leaf,door/2)
 portal(name+'_Exit',(room[0],room[1]+rd/2-20,0),180,(front[0],front[1]+160,100),width=85)
 report['buildings'].append({'name':name,'asset':asset,'position':origin,'yaw':yaw,'kind':'guild' if guild else ('barn' if name=='FarmBarn' else 'home')})
 report['interiors'].append({'building':name,'center':room,'size':[rw,rd]})
# Small, uneven farms separated by footpaths and working space.
farm_plots=[(-3175.5, 2632.5, 800, 300, 'wheat', 0), (-1947.0, 2133.0, 560, 360, 'cabbage', 0), (604.5, 2362.5, 600, 400, 'wheat', 0), (834.0, -1660.5, 450, 320, 'cabbage', 0)]
for fi,(x,y,w,d,crop,fyaw) in enumerate(farm_plots):
 soil=cube('Farm_'+str(fi)+'_Soil',(x,y,4),(w,d,9),materials['Soil'],folder='Farms');soil.set_actor_rotation(u.Rotator(pitch=0,yaw=fyaw,roll=0),False)
 for row in range(int(d//75)):
  furrow=cube('Farm_Furrow',local((x,y,0),fyaw,(0,-d/2+40+row*75,10)),(w-35,12,9),materials['Timber'],folder='Farms');furrow.set_actor_rotation(u.Rotator(pitch=0,yaw=fyaw,roll=0),False)
  for col in range(int(w//70)):
   place('Farm_'+crop,F+'/SM_Rural'+('Wheat' if crop=='wheat' else 'Cabbage'),local((x,y,0),fyaw,(-w/2+40+col*70,-d/2+40+row*75,12)),(.8,.8,.8),yaw=fyaw,folder='Farms')
 for side in [-1,1]:
  for col in range(max(1,int(w//200))):place('Farm_Fence',F+'/SM_RuralFence',local((x,y,0),fyaw,(-w/2+100+col*200,side*(d/2+30),0)),yaw=fyaw,folder='Farms')
 for row in range(max(1,int(d//200))):place('Farm_Fence',F+'/SM_RuralFence',local((x,y,0),fyaw,(-w/2-25,-d/2+100+row*200,0)),yaw=fyaw+90,folder='Farms')
 report['farms'].append({'position':[x,y],'size':[w,d],'crop':crop,'yaw':fyaw})
place('Village_Well',F+'/SM_RuralWell',(-620,380,0),folder='Common Ground')
for pos,yaw in [((-400,480,0),-10),((-820,100,0),20),((380,180,0),80)]:place('Village_Bench',F+'/SM_RuralBench',pos,yaw=yaw,folder='Common Ground')
cube('Evergrove_SignPost',(760,330,100),(16,18,200),materials['Timber'],folder='Village Signs')
cube('Evergrove_SignBoard',(760,330,190),(245,24,70),materials['Plank'],folder='Village Signs')
text('Evergrove_WelcomeSign','EVERGROVE',(760,350,215),27)
# Forest trees, native bushes, grass and wildflowers. Never decorative plant pots.
def tree(x,y,scale=1):
 global report
 if 8700<x<9700 and 1800<y<3200:return
 if math.hypot(x-9200,y-1800)<360:return
 for a,b,width in path_segments:
  dx=b[0]-a[0];dy=b[1]-a[1];t=max(0,min(1,((x-a[0])*dx+(y-a[1])*dy)/(dx*dx+dy*dy)))
  if math.hypot(x-a[0]-t*dx,y-a[1]-t*dy)<width/2+100:return
 asset='/Game/Environment/BreezeWoodland/SM_BreezeTree_'+rng.choice(['A','B','C'])
 tree_actor=place('Forest_Tree',asset,(x,y,0),(scale,scale,scale),folder='Forest')
 if x>4500:tree_actor.static_mesh_component.set_cast_shadow(False)
 collider('Tree_Trunk',(x,y,0),0,(0,0,105),(55,55,210));report['trees']+=1
for x in range(1030,4610,340):
 for y in [-1160,-780,-480,850,1190,1590]:tree(x+rng.uniform(-110,110),y+rng.uniform(-90,90),rng.uniform(.82,1.18))
for x in range(-2900,900,380):
 for side in [-1,1]:
  tx=x+rng.uniform(-90,90);ty=side*(2800+140*math.sin(tx*.013))
  tree(780+(tx-780)*1.35,ty*1.35,rng.uniform(.8,1.12))
for x,y in [(-2900,-1350),(-2900,-700),(-2800,80),(-2880,850),(-2800,1500),(-800,-1760),(-240,-1860),(1060,-1620),(940,1400)]:
 if x<1000:x,y=780+(x-780)*1.35,y*1.35
 tree(x,y,.92)
# Dense forest surrounds a winding route with optional side trails and dead ends.
for tx in range(4600,10800,360):
 for ty in range(-3000,3100,360):
  nearest=1e9
  for a,b,width in path_segments:
   dx=b[0]-a[0];dy=b[1]-a[1];t=max(0,min(1,((tx-a[0])*dx+(ty-a[1])*dy)/(dx*dx+dy*dy)))
   nearest=min(nearest,math.hypot(tx-a[0]-t*dx,ty-a[1]-t*dy))
  if nearest<470 or math.hypot(tx-9200,ty-1800)<500 or (8700<tx<9700 and 1800<ty<3200):continue
  tree(tx,ty,rng.uniform(.85,1.15))
  collider('Forest_ThicketBarrier',(tx,ty,0),0,(0,0,120),(350,350,240))
for mx,my in [(9550,1800),(8700,100),(6400,-900),(4800,1000)]:
 cube('Forest_TrailMarkerPost',(mx,my,95),(18,18,190),materials['Timber'],folder='Forest Trail Details')
 cube('Forest_TrailMarkerBoard',(mx,my,160),(160,22,60),materials['PlankLight'],folder='Forest Trail Details')
 text('Forest_TrailMarker','OLD TRAIL',(mx,my+14,175),18)
cube('Hunter_Satchel',(9000,1890,35),(80,55,70),materials['Timber'],folder='Forest Trail Details')
cube('Hunter_SatchelFlap',(9000,1890,74),(90,60,14),materials['PlankLight'],folder='Forest Trail Details')
cube('Hunter_SatchelClasp',(9000,1920,52),(18,8,20),materials['Iron'],folder='Forest Trail Details')

# A loose, deep woodland surround beyond the walking bounds.
backdrop_rng=random.Random(5151)
for side in [-1,1]:
 for row in range(3):
  for x in range(-3650,1250,430):
   tx=x+backdrop_rng.uniform(-150,150);ty=side*(2500+row*440+backdrop_rng.uniform(-140,140));scale=backdrop_rng.uniform(.78,1.22)
   asset='/Game/Environment/BreezeWoodland/SM_BreezeTree_'+backdrop_rng.choice(['A','B','C'])
   if tx<1000:tx,ty=780+(tx-780)*1.35,ty*1.35
   place('Rural_BackdropTree',asset,(tx,ty,0),(scale,scale,scale),folder='Forest Backdrop')
for y in range(-2200,2300,430):
 for x in [-3500,-3900]:
  tx=x+backdrop_rng.uniform(-100,100);ty=y+backdrop_rng.uniform(-120,120);scale=backdrop_rng.uniform(.8,1.2)
  asset='/Game/Environment/BreezeWoodland/SM_BreezeTree_'+backdrop_rng.choice(['A','B','C'])
  place('Rural_BackdropTree',asset,(780+(tx-780)*1.35,ty*1.35,0),(scale,scale,scale),folder='Forest Backdrop')
for i in range(100):
 x=rng.uniform(900,4500);y=rng.choice([-1,1])*rng.uniform(430,1800)
 if math.hypot(x-9200,y-1800)<240:continue
 place('Forest_Bush','/Game/Environment/PixelProps/SM_Prop_Bush',(x,y,0),(rng.uniform(.6,1.1),)*3,mat='/Game/Environment/LayeredWoodland/M_StackedLeaf_1',folder='Forest Understory')
for i in range(90):
 x=rng.uniform(-2500,4400);y=rng.uniform(-1900,2100)
 if any(abs(x-b[2][0])<specs[b[1]]['width']/2+80 and abs(y-b[2][1])<specs[b[1]]['depth']/2+150 for b in buildings):continue
 place('Wildflowers','/Game/Environment/BreezeWoodland/SM_BreezeFlowers_'+rng.choice(['White','Yellow']),(x,y,2),(.7,.7,.7),folder='Wildflowers')
for x,y,sx,sy in [(3250,-3300,15100,40),(3250,3300,15100,40),(-4300,0,40,6600),(10800,0,40,6600)]:cube('World_Boundary',(x,y,100),(sx,sy,240),collision=True,visible=False,folder='Collision')
# Simple navigation bounds are inherited from the source map, then expanded.
for a in kept:
 if isinstance(a,u.NavMeshBoundsVolume):
  a.set_actor_location(u.Vector(3250,0,280),False,False);a.set_actor_scale3d(u.Vector(160,70,6))
  inside=actors.duplicate_actor(a,world,u.Vector(2100,-9700,0))
  if inside:inside.set_actor_label('Rural_InteriorNavigation');inside.set_actor_scale3d(u.Vector(120,34,6))
 if isinstance(a,u.PlayerStart):a.set_actor_location(u.Vector(9200,1800,110),False,False)
 if isinstance(a,u.CameraActor):a.set_actor_location(u.Vector(0,2796,1500),False,False);a.set_actor_rotation(u.Rotator(pitch=-31,yaw=-90,roll=0),False);a.camera_component.set_editor_property('ortho_width',1200)
# Familiar faces and a few quiet village residents; quest behavior remains native.
NPC=u.load_class(None,'/Game/Game/Characters/NPCs/BP_Npc.BP_Npc_C')
for name,pos,line,choices in [('Luna',(-580,-22200,100),"You're safe in Evergrove. Rest a little; we can work out the rest together.",True),('Rein',(9090,1790,100),"I'm Rein, a hunter from Evergrove. I found you unconscious here. Follow the old trail markers west; explore carefully and you'll reach the village.",False),('Mara',(-1160,-600,100),"The roof leaks when it rains, but there's always a dry chair by the window.",False),('Tobin',(-1850,450,100),"Mind the seedlings. That little patch has kept this village fed for years.",False),('Nell',(-850,1100,100),"New faces are rare out here. You're welcome to stay awhile.",False)]:
 a=actors.spawn_actor_from_class(NPC,u.Vector(*pos));a.set_actor_label('Village_'+name);a.set_folder_path('Villagers')
 a.set_editor_property('is_spatially_loaded',False)
 for key,value in {'NPCName':name,'NPCDialogueText':line,'HasChoices':choices,'CompletesQuestOnInteract':name in ['Luna','Rein'],'QuestToComplete':'0_Delivery_001','QuestNPCID':'None'}.items():a.set_editor_property(key,value)
lighting=u.load_class(None,'/Game/Game/World/BP_RuralVillageLighting.BP_RuralVillageLighting_C')
assert lighting
actors.spawn_actor_from_class(lighting,u.Vector(0,0,0)).set_actor_label('Rural_WindowLighting')
# Spread shared village details with the structures, retaining the guild sign's authored facade position.
for a in actors.get_all_level_actors():
 if str(a.get_folder_path()) not in ['Common Ground','Village Signs','Villagers'] or a.get_actor_label()=='VillageGuildSign':continue
 p=a.get_actor_location()
 if p.x<1000 and p.y>-5000:a.set_actor_location(u.Vector(780+(p.x-780)*1.35,p.y*1.35,p.z),False,False)
assert levels.save_current_level()
assert u.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
report['spacing_expanded']=1.35;report['trail']=trail;report['approaches']=approaches
report['waking_clearing']=[9200,1800];report['hunter']=[9090,1790];report['forest_forks']=forest_forks
(SOURCE/'layout.json').write_text(json.dumps(report,indent=2))
u.log('RURAL_FOREST_AND_VILLAGE_SAVED '+json.dumps({'buildings':len(buildings),'farms':len(farm_plots),'trees':report['trees']}))
if not globals().get('KEEP_EDITOR_OPEN',False):u.SystemLibrary.quit_editor()
