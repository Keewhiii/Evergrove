import unreal as u,json,math,random
from pathlib import Path
ROOT=Path('E:/UE5 Projects/AdventureRPG');F='/Game/Environment/ForestAtmosphere'
levels=u.get_editor_subsystem(u.LevelEditorSubsystem);actors=u.get_editor_subsystem(u.EditorActorSubsystem);assets=u.EditorAssetLibrary
assert levels.load_level('/Game/Maps/L_EvergroveForest')
exec(compile((ROOT/'Scripts/forest_terrain_height.py').read_text(),'forest_terrain_height.py','exec'))
task=u.AssetImportTask();task.filename=str(ROOT/'ContentSource/ForestAtmosphere/SM_ForestRollingTerrain.obj');task.destination_path=F;task.destination_name='SM_ForestRollingTerrain';task.automated=True;task.save=True;task.replace_existing=True
options=u.FbxImportUI();options.import_materials=False;options.import_textures=False;options.import_mesh=True;options.mesh_type_to_import=u.FBXImportType.FBXIT_STATIC_MESH;options.static_mesh_import_data.combine_meshes=True;options.static_mesh_import_data.auto_generate_collision=False;task.options=options
u.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task]);mesh=u.load_asset(F+'/SM_ForestRollingTerrain');assert mesh
mesh.set_material(0,u.load_asset('/Game/Environment/CartoonGround/M_PaintedGrass'))
body=mesh.get_editor_property('body_setup');body.set_editor_property('collision_trace_flag',u.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);assets.save_loaded_asset(mesh)
for actor in actors.get_all_level_actors():
 label=actor.get_actor_label()
 if label=='Forest_RollingTerrain' or label.startswith(('Forest_BankBoulder','Forest_RiverBoulder','Forest_ScatteredRock')):actors.destroy_actor(actor)
terrain=actors.spawn_actor_from_class(u.StaticMeshActor,u.Vector(0,0,0));terrain.set_actor_label('Forest_RollingTerrain');terrain.set_folder_path('Forest Terrain');terrain.set_editor_property('is_spatially_loaded',False)
c=terrain.static_mesh_component;c.set_static_mesh(mesh);c.set_collision_profile_name('BlockAll');c.set_collision_enabled(u.CollisionEnabled.QUERY_AND_PHYSICS);c.set_editor_property('can_ever_affect_navigation',True)
raised=0
for actor in actors.get_all_level_actors():
 label=actor.get_actor_label();folder=str(actor.get_folder_path());pos=actor.get_actor_location()
 eligible=(label.startswith(('Forest_','Hunter_','Village_Rein')) or isinstance(actor,u.PlayerStart))
 if not eligible or label in ['Forest_GrassGround','Forest_RollingTerrain','Forest_CanopyLeaves'] or label.startswith(('Forest_WindTile','Forest_River','Forest_Lake','Forest_Pond','Forest_Bridge')) or 'Water' in folder:continue
 if label.startswith('Forest_Riverbank'):eligible=True
 if not eligible:continue
 tags=[str(t) for t in actor.tags];base=next((float(t.split('=')[1]) for t in tags if t.startswith('TerrainBaseZ=')),pos.z)
 tags=[t for t in tags if not t.startswith('TerrainBaseZ=')];tags.append('TerrainBaseZ='+str(base));actor.modify();actor.tags=tags
 actor.set_actor_location(u.Vector(pos.x,pos.y,base+terrain_height(pos.x,pos.y)),False,False);raised+=1
helper=(ROOT/'Scripts/author_rural_map_unreal.py').read_text();exec(helper[helper.index('mesh_cache={}'):helper.index('# A single continuous ground')])
layout=json.loads((ROOT/'ContentSource/RuralVillage/forest_layout.json').read_text());segments=[(a,b) for points in [layout['route']]+layout['forks'] for a,b in zip(points,points[1:])]
def distance(x,y):
 result=1e9
 for a,b in segments:
  dx=b[0]-a[0];dy=b[1]-a[1];t=max(0,min(1,((x-a[0])*dx+(y-a[1])*dy)/(dx*dx+dy*dy)));result=min(result,math.hypot(x-a[0]-t*dx,y-a[1]-t*dy))
 return result
rng=random.Random(171016);placed=[];tries=0
while len(placed)<38 and tries<1500:
 tries+=1;a,b=rng.choice(segments);t=rng.random();x=a[0]+t*(b[0]-a[0])+rng.uniform(-650,650);y=a[1]+t*(b[1]-a[1])+rng.uniform(-650,650)
 if distance(x,y)<175 or abs(x-(5750+180*math.sin(y/1200)+90*math.sin(y/470)))<500:continue
 if any(math.hypot((x-cx)/rx,(y-cy)/ry)<1.7 for cx,cy,rx,ry in WATER):continue
 if any(math.hypot(x-px,y-py)<230 for px,py in placed):continue
 size=rng.uniform(.35,.85);place('Forest_ScatteredRock','/Game/Environment/ForestFeatures/SM_ForestCartoonRock_'+str(rng.randrange(2)),(x,y,terrain_height(x,y)-2),(size*rng.uniform(.8,1.2),size,size*rng.uniform(.7,1.0)),yaw=rng.uniform(0,360),folder='Forest Natural Rocks');placed.append((x,y))
assert levels.save_current_level();assert u.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
(ROOT/'Saved/SeparateForestAudit/terrain.json').write_text(json.dumps({'raised_actors':raised,'scattered_rocks':placed,'maximum_height_cm':max(terrain_height(x,y) for x in range(1800,12000,200) for y in range(-5800,4700,200))},indent=2))
u.log('ROLLING_FOREST_TERRAIN_AND_RANDOM_ROCKS_SAVED '+str(raised))
