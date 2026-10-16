"""Original layered animated water: directional river current and quiet standing water."""
import unreal as u,json
from pathlib import Path
ROOT=Path('E:/UE5 Projects/AdventureRPG');FF='/Game/Environment/ForestFeatures';assets=u.EditorAssetLibrary;mel=u.MaterialEditingLibrary
collection=u.load_asset(FF+'/MPC_WaterInteraction')
if not collection:
 collection=u.AssetToolsHelpers.get_asset_tools().create_asset('MPC_WaterInteraction',FF,u.MaterialParameterCollection,u.MaterialParameterCollectionFactoryNew())
 parameter=u.CollectionVectorParameter();parameter.set_editor_property('parameter_name','Contact');parameter.set_editor_property('default_value',u.LinearColor(0,0,10000,0));collection.set_editor_property('vector_parameters',[parameter]);assets.save_loaded_asset(collection)
mat=None
def expr(cls,**props):
 n=mel.create_material_expression(mat,getattr(u,'MaterialExpression'+cls))
 for k,v in props.items():n.set_editor_property(k,v)
 return n
def wire(a,b,pin):assert mel.connect_material_expressions(a,'',b,'' if pin=='Input' else pin)
def c(v):return expr('Constant',r=v)
def mult(a,v):
 n=expr('Multiply',const_b=v);wire(a,n,'A');return n
def add(a,b):
 n=expr('Add');wire(a,n,'A');wire(b,n,'B');return n
def mul(a,b):
 n=expr('Multiply');wire(a,n,'A');wire(b,n,'B');return n
def powr(a,p):
 n=expr('Power',const_exponent=p);wire(a,n,'Base');return n
def saturate(a):
 n=expr('Clamp',min_default=0,max_default=1);wire(a,n,'Input');return n
def wave(a):
 n=expr('Sine',period=6.283185);wire(a,n,'Input');return n
def build_surface(river):
 global mat
 name='M_ForestRiverSurface' if river else 'M_DeepWater'
 mat=u.load_asset(FF+'/'+name)
 if not mat:mat=u.AssetToolsHelpers.get_asset_tools().create_asset(name,FF,u.Material,u.MaterialFactoryNew())
 mat.modify();mel.delete_all_material_expressions(mat)
 uv=expr('TextureCoordinate');depth=expr('ComponentMask',r=True,g=False,b=False,a=False);wire(uv,depth,'Input')
 world=expr('WorldPosition');clock=expr('Time');coords=[]
 for axis in ['r','g']:
  mask=expr('ComponentMask',r=axis=='r',g=axis=='g',b=False,a=False);wire(world,mask,'Input');coords.append(mask)
 x,y=coords
 # Southward current in the river; slower intersecting ripples in still water.
 phase=add(mult(y,.052 if river else .034),mult(clock,2.4 if river else .48))
 bend=wave(add(mult(x,.027),mult(clock,-.62 if river else -.21)))
 w0=wave(add(phase,mult(bend,.8)))
 w1=wave(add(add(mult(x,.061),mult(y,.018)),mult(clock,-1.1 if river else -.32)))
 # Animated cellular caustics: rounded blue pools separated by fine luminous seams.
 # Cellular ripples belong to standing water only. The river uses open flow streaks.
 shader=(ROOT/'Scripts'/('forest_river_current.hlsl' if river else 'forest_water_caustics.hlsl')).read_text().replace('RIVER_MODE','0.0')
 contact=expr('CollectionParameter',collection=collection,parameter_name='Contact')
 contact_code="""float2 p=Contact.xy;float wet=0.0;
 wet=max(wet,1.0-step(1.0,length((p-float2(8500,2500))/float2(700,500))));
 wet=max(wet,1.0-step(1.0,length((p-float2(4100,2600))/float2(230,170))));
 wet=max(wet,1.0-step(1.0,length((p-float2(7950,-4300))/float2(260,190))));
 return wet*saturate(Contact.a)* (1.0-step(135.0,Contact.z))*exp(-length(Position.xy-p)/95.0);"""
 contact_inputs=[]
 for input_name in ['Position','Contact']:
  item=u.CustomInput();item.set_editor_property('input_name',input_name);contact_inputs.append(item)
 interaction=expr('Custom',code=contact_code,output_type=u.CustomMaterialOutputType.CMOT_FLOAT1,inputs=contact_inputs,description='Moving water contact only')
 wire(world,interaction,'Position');wire(contact,interaction,'Contact')
 inputs=[]
 for name in (['Position','Clock','Depth'] if river else ['Position','Clock','Depth','Contact','Interaction']):
  item=u.CustomInput();item.set_editor_property('input_name',name);inputs.append(item)
 tinted=expr('Custom',code=shader,output_type=u.CustomMaterialOutputType.CMOT_FLOAT3,inputs=inputs,description='Directional open river current' if river else 'Calm water with local contact ripples')
 wire(world,tinted,'Position');wire(clock,tinted,'Clock');wire(depth,tinted,'Depth')
 if not river:wire(contact,tinted,'Contact');wire(interaction,tinted,'Interaction')
 mel.connect_material_property(tinted,'',u.MaterialProperty.MP_BASE_COLOR)
 xy=expr('AppendVector');wire(mult(w1,.095) if river else add(mult(w1,.010),mult(mul(w1,interaction),.055)),xy,'A');wire(mult(w0,.075) if river else add(mult(w0,.008),mult(mul(w0,interaction),.045)),xy,'B')
 xyz=expr('AppendVector');wire(xy,xyz,'A');wire(c(1),xyz,'B');normal=expr('Normalize');wire(xyz,normal,'VectorInput');mel.connect_material_property(normal,'',u.MaterialProperty.MP_NORMAL)
 mel.connect_material_property(c(.24 if river else .2),'',u.MaterialProperty.MP_ROUGHNESS);mel.connect_material_property(c(.6),'',u.MaterialProperty.MP_SPECULAR)
 mat.set_editor_property('tangent_space_normal',False);mat.set_editor_property('two_sided',True);mel.recompile_material(mat);assets.save_loaded_asset(mat)
 return mat
lake_mat=build_surface(False)
river_mat=None if globals().get('STANDING_WATER_ONLY',False) else build_surface(True)

for item in json.loads((ROOT/'ContentSource/ForestFeatures/manifest.json').read_text()):
 if not any(t in item['name'] for t in ['Lake','Pond','River']):continue
 if globals().get('STANDING_WATER_ONLY',False) and 'River' in item['name']:continue
 path=FF+'/'+item['name']
 if globals().get('REIMPORT_WATER',False):
  task=u.AssetImportTask();task.filename=item['file'];task.destination_path=FF;task.destination_name=item['name'];task.automated=True;task.save=True;task.replace_existing=True
  options=u.FbxImportUI();options.import_materials=False;options.import_textures=False;options.import_mesh=True;options.mesh_type_to_import=u.FBXImportType.FBXIT_STATIC_MESH;options.static_mesh_import_data.combine_meshes=True;options.static_mesh_import_data.auto_generate_collision=False;task.options=options
  u.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
 water_mesh_asset=u.load_asset(path)
 for i,slot in enumerate(water_mesh_asset.get_editor_property('static_materials')):water_mesh_asset.set_material(i,u.load_asset(FF+'/M_Shore') if str(slot.get_editor_property('material_slot_name'))=='Shore' else (river_mat if 'River' in item['name'] else lake_mat))
 u.get_editor_subsystem(u.StaticMeshEditorSubsystem).remove_collisions(water_mesh_asset);assets.save_loaded_asset(water_mesh_asset)
u.log('SMOOTH_ANIMATED_FOREST_WATER_SAVED')
