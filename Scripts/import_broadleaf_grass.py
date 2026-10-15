"""Install the layered broadleaf tile while retaining the existing intermittent gust shader."""
from build_companion_combat import call,ref,ROOT,ASSET,OBJ
import json
F='/Game/Environment/BroadleafGrass';SM='editor_toolset.toolsets.static_mesh.StaticMeshTools';TEX='editor_toolset.toolsets.texture.TextureTools';MAT='editor_toolset.toolsets.material.MaterialTools';PROG='editor_toolset.toolsets.programmatic.ProgrammaticToolset'
def props(o,p):return call('set_properties',{'instance':o,'values':json.dumps(p)},OBJ)
props(ref('/Script/UnrealEd.Default__EditorPerformanceSettings'),{'bThrottleCPUWhenNotForeground':False})
mesh=ref(F+'/SM_BroadleafGrass.SM_BroadleafGrass')
if not call('exists',{'path':F+'/SM_BroadleafGrass'},ASSET):call('import_file',{'folder_path':F,'asset_name':'SM_BroadleafGrass','source_file':str(ROOT/'ContentSource/BroadleafGrass/FBX/SM_BroadleafGrass.fbx'),'import_materials':False,'import_textures':False,'combine_meshes':True},SM)
call('remove_collisions',{'mesh':mesh},SM);assert call('get_triangle_count',{'mesh':mesh,'lod_index':0},SM)==6
tex=ref(F+'/T_BroadleafGrass.T_BroadleafGrass')
if not call('exists',{'path':F+'/T_BroadleafGrass'},ASSET):call('import_file',{'folder_path':F,'asset_name':'T_BroadleafGrass','source_file':str(ROOT/'ContentSource/BroadleafGrass/T_BroadleafGrass.png')},TEX)
props(tex,{'Filter':'TF_Nearest','LODGroup':'TEXTUREGROUP_Pixels2D','NeverStream':True,'MipGenSettings':'TMGS_NoMipmaps'})
mat=ref(F+'/M_BroadleafGrass.M_BroadleafGrass')
if not call('exists',{'path':F+'/M_BroadleafGrass'},ASSET):assert call('duplicate',{'path':'/Game/Environment/PixelProps/M_Prop_Grass','new_path':F+'/M_BroadleafGrass'},ASSET)
for e in call('get_expressions',{'material_or_function':mat},MAT):
 if 'TextureSample' in str(call('get_class',{'instance':e},OBJ)):props(e,{'Texture':tex['refPath']})
call('recompile',{'material_or_function':mat},MAT)
assert call('get_property_input',{'material':mat,'material_property':'MP_WorldPositionOffset'},MAT)['expression']
for slot in call('get_material_slots',{'mesh':mesh},SM):call('set_material',{'mesh':mesh,'slot_name':slot,'material':mat},SM)
script='''import json
def tool(n,a):return execute_tool(n,json.dumps(a))['returnValue']
def run():
 count=0;visible=0;errors=[]
 for tag in ['WoodlandBlenderArt','PixelWoodland']:
  for a in tool('editor_toolset.toolsets.scene.SceneTools.find_actors',{'name':'','tag':tag,'collision_channels':[]}):
   cs=tool('editor_toolset.toolsets.actor.ActorTools.get_components',{'actor':a,'component_type':{'refPath':'/Script/Engine.StaticMeshComponent'}})
   if not cs:continue
   c=cs[0];p=json.loads(tool('editor_toolset.toolsets.object.ObjectTools.get_properties',{'instance':c,'properties':['StaticMesh','bVisible']}))
   if not any(name in p['StaticMesh']['refPath'] for name in ['SM_Prop_Grass','SM_BroadleafGrass']):continue
   tool('editor_toolset.toolsets.object.ObjectTools.set_properties',{'instance':c,'values':json.dumps({'StaticMesh':'/Game/Environment/BroadleafGrass/SM_BroadleafGrass.SM_BroadleafGrass','OverrideMaterials':[]})})
   count+=1;visible+=int(p['bVisible'])
   check=json.loads(tool('editor_toolset.toolsets.object.ObjectTools.get_properties',{'instance':c,'properties':['BodyInstance','bCanEverAffectNavigation']}))
   if check['BodyInstance']['collisionEnabled']!='NoCollision' or check['bCanEverAffectNavigation']:errors.append(a)
 tool('editor_toolset.toolsets.asset.AssetTools.save_assets',{'asset_paths':[]})
 return {'grass_instances':count,'visible_components':visible,'collision_errors':errors,'flat_planes_per_tile':3,'triangles_per_tile':6}
'''
report=json.loads(call('execute_tool_script',{'script':script},PROG));assert report['grass_instances']==576 and not report['collision_errors'];out=ROOT/'Saved/BroadleafGrassAudit';out.mkdir(exist_ok=True);(out/'migration.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
