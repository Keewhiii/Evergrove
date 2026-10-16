"""Native feature import and placement, executed by the forest level builder."""
FEATURES=ROOT/'ContentSource/ForestFeatures';FF='/Game/Environment/ForestFeatures'
feature_mats={k:materials[k] for k in ['Timber','Plank','PlankLight','Cream','Moss','Stone','StoneLight']}
for key,rgb in {'DeepWater':(.018,.11,.16),'MidWater':(.025,.19,.24),'ShallowWater':(.05,.28,.29),'Shore':(.13,.23,.105)}.items():
 path=FF+'/M_'+key
 if assets.does_asset_exist(path):feature_mats[key]=u.load_asset(path);continue
 mat=u.AssetToolsHelpers.get_asset_tools().create_asset('M_'+key,FF,u.Material,u.MaterialFactoryNew());mel=u.MaterialEditingLibrary
 def expr(cls,**props):
  n=mel.create_material_expression(mat,getattr(u,'MaterialExpression'+cls))
  for k,v in props.items():n.set_editor_property(k,v)
  return n
 def wire(a,b,pin):
  assert mel.connect_material_expressions(a,'',b,'' if pin=='Input' else pin),(a,b,pin)
 base=expr('Constant3Vector',constant=u.LinearColor(*rgb,1));mel.connect_material_property(base,'',u.MaterialProperty.MP_BASE_COLOR)
 rough=expr('Constant',r=.24 if key!='Shore' else .95);mel.connect_material_property(rough,'',u.MaterialProperty.MP_ROUGHNESS)
 spec=expr('Constant',r=.7 if key!='Shore' else .1);mel.connect_material_property(spec,'',u.MaterialProperty.MP_SPECULAR)
 if key!='Shore':
  world_pos=expr('WorldPosition');time_node=expr('Time');normals=[]
  for axis,freq,speed in [('r',.025,.42),('g',.037,-.31)]:
   mask=expr('ComponentMask',r=axis=='r',g=axis=='g',b=False,a=False);wire(world_pos,mask,'Input')
   scale=expr('Multiply',const_b=freq);wire(mask,scale,'A');motion=expr('Multiply',const_b=speed);wire(time_node,motion,'A')
   phase=expr('Add');wire(scale,phase,'A');wire(motion,phase,'B');sine=expr('Sine',period=6.283185);wire(phase,sine,'Input');amp=expr('Multiply',const_b=.07);wire(sine,amp,'A');normals.append(amp)
  xy=expr('AppendVector');wire(normals[0],xy,'A');wire(normals[1],xy,'B');xyz=expr('AppendVector');wire(xy,xyz,'A');wire(expr('Constant',r=1),xyz,'B');norm=expr('Normalize');wire(xyz,norm,'VectorInput');mel.connect_material_property(norm,'',u.MaterialProperty.MP_NORMAL)
 mat.set_editor_property('two_sided',True);mat.set_editor_property('tangent_space_normal',False);mel.recompile_material(mat);assets.save_loaded_asset(mat);feature_mats[key]=mat
for item in json.loads((FEATURES/'manifest.json').read_text()):
 path=FF+'/'+item['name']
 if not assets.does_asset_exist(path):
  task=u.AssetImportTask();task.filename=item['file'];task.destination_path=FF;task.destination_name=item['name'];task.automated=True;task.save=True
  options=u.FbxImportUI();options.import_materials=False;options.import_textures=False;options.import_mesh=True;options.mesh_type_to_import=u.FBXImportType.FBXIT_STATIC_MESH;options.static_mesh_import_data.combine_meshes=True;options.static_mesh_import_data.auto_generate_collision=False;task.options=options
  u.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
 mesh_asset=u.load_asset(path)
 for i,slot in enumerate(mesh_asset.get_editor_property('static_materials')):
  mesh_asset.set_material(i,feature_mats[str(slot.get_editor_property('material_slot_name'))])
 u.get_editor_subsystem(u.StaticMeshEditorSubsystem).remove_collisions(mesh_asset);assets.save_loaded_asset(mesh_asset)
exec(compile((ROOT/'Scripts/forest_water_surface.py').read_text(),'forest_water_surface.py','exec'))
water_bodies=[{'name':'Lake','position':[8500,2500],'radii':[700,500],'mesh':'SM_ForestLake'}, {'name':'Pond_A','position':[4100,2600],'radii':[230,170],'mesh':'SM_ForestPond_A'}, {'name':'Pond_B','position':[7950,-4300],'radii':[260,190],'mesh':'SM_ForestPond_B'}]
def river_center(y):return 5750+180*math.sin(y/1200)+90*math.sin(y/470)
def river_width(y):return 130+25*math.sin(y/700+.4)
def is_water(x,y):
 if abs(x-river_center(y))<river_width(y)*1.08:return True
 return any(((x-b['position'][0])/b['radii'][0])**2+((y-b['position'][1])/b['radii'][1])**2<1.1 for b in water_bodies)
def water_clearance(x,y):
 if abs(x-river_center(y))<river_width(y)+420:return True
 for body in water_bodies:
  bx,by=body['position'];rx,ry=body['radii'];margin=200 if body['name']=='Lake' else 180
  if ((x-bx)/(rx+margin))**2+((y-by)/(ry+margin))**2<1:return True
  if abs(x-bx)<rx+200 and by<y<by+ry+900:return True
 return False
def place_forest_features():
 for body in water_bodies:
  x,y=body['position'];rx,ry=body['radii'];name=body['name']
  place('Forest_'+name,FF+'/'+body['mesh'],(x,y,4),(rx/100,ry/100,1),folder='Forest Water')
  barrier=place('Forest_'+name+'_DeepWater','/Engine/BasicShapes/Cylinder',(x,y,100),(rx*.83/50,ry*.83/50,2.4),collision=True,folder='Collision');barrier.static_mesh_component.set_visibility(False);barrier.set_actor_hidden_in_game(True)
  for i in range(7 if name=='Lake' else 3):
   angle=i*math.tau/(7 if name=='Lake' else 3)
   place('Forest_BankBoulder',FF+'/SM_ForestCartoonRock_'+str(i%2),(x+math.cos(angle)*rx*1.18,y+math.sin(angle)*ry*1.18,0),(.65,.65,.65),folder='Forest Landmarks')
 place('Forest_River',FF+'/SM_ForestRiver',(5750,0,4),folder='Forest Water')
 bridge_y=-3150;bridge_x=river_center(bridge_y)
 for lo in range(-5800,4400,160):
  hi=lo+160;pieces=[(lo,min(hi,bridge_y-215)),(max(lo,bridge_y+215),hi)]
  for a,b in pieces:
   if b<=a:continue
   dx=river_center(b)-river_center(a);dy=b-a;mid=(a+b)/2
   collider('Forest_RiverBank',((river_center(a)+river_center(b))/2,mid,0),-math.degrees(math.atan2(dx,dy)),(0,0,110),(river_width(mid)*1.8,math.hypot(dx,dy)+6,220))
 for i in range(-14,15):cube('Forest_BridgePlank',(bridge_x+i*40,bridge_y,13),(37,420,22),materials['PlankLight'],True,folder='Forest Bridge')
 for y in [bridge_y-225,bridge_y+225]:
  cube('Forest_BridgeRail',(bridge_x,y,95),(1190,18,22),materials['Timber'],folder='Forest Bridge')
  for x in [bridge_x-560,bridge_x,bridge_x+560]:cube('Forest_BridgePost',(x,y,55),(22,22,110),materials['Timber'],folder='Forest Bridge')
 for y in range(-5000,4000,900):
  if abs(y-bridge_y)<450:continue
  for side in [-1,1]:place('Forest_RiverBoulder',FF+'/SM_ForestCartoonRock_'+str((y//900)%2),(river_center(y)+side*(river_width(y)+190),y,0),(.7,.7,.7),folder='Forest Landmarks')
 for x,y in [(7300,1800),(7700,-4500),(4550,2250),(3750,-1200)]:place('Forest_FallenLog',FF+'/SM_ForestCartoonLog',(x,y,0),(.9,.9,.9),folder='Forest Landmarks')
 for x,y in [(9725,2145),(8795,-750),(5345,-2250),(2600,945)]:
  cube('Forest_OldMarker',(x,y,75),(18,18,150),materials['Timber'],folder='Forest Landmarks');cube('Forest_OldMarkerTop',(x,y,125),(95,22,35),materials['Plank'],folder='Forest Landmarks')
