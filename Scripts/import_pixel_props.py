from build_companion_combat import call,ref,ROOT,ASSET,OBJ
import json
F='/Game/Environment/PixelProps';SM='editor_toolset.toolsets.static_mesh.StaticMeshTools';MAT='editor_toolset.toolsets.material.MaterialTools';TEX='editor_toolset.toolsets.texture.TextureTools';PROG='editor_toolset.toolsets.programmatic.ProgrammaticToolset'
SOURCE=ROOT/'ContentSource/PixelProps';OUT=ROOT/'Saved/PixelPropsAudit';OUT.mkdir(exist_ok=True)
def props(o,p):return call('set_properties',{'instance':o,'values':json.dumps(p)},OBJ)
props(ref('/Script/UnrealEd.Default__EditorPerformanceSettings'),{'bThrottleCPUWhenNotForeground':False})
for item in json.loads((SOURCE/'manifest.json').read_text()):
 name=item['name'];mesh=ref(F+'/'+name+'.'+name)
 if not call('exists',{'path':F+'/'+name},ASSET):call('import_file',{'folder_path':F,'asset_name':name,'source_file':item['file'],'import_materials':True,'import_textures':True,'combine_meshes':True},SM)
 call('remove_collisions',{'mesh':mesh},SM)
 assert call('get_triangle_count',{'mesh':mesh,'lod_index':0},SM)==item['triangles']
 print('IMPORTED',name,flush=True)
for name in ['Grass','Rock','Lantern']:
 texname='T_'+name;tex=ref(F+'/'+texname+'.'+texname)
 if not call('exists',{'path':F+'/'+texname},ASSET):call('import_file',{'folder_path':F,'asset_name':texname,'source_file':str(SOURCE/(texname+'.png'))},TEX)
 props(tex,{'Filter':'TF_Nearest','LODGroup':'TEXTUREGROUP_Pixels2D','NeverStream':True,'MipGenSettings':'TMGS_NoMipmaps'})
 mn='M_Prop_'+name;mat=ref(F+'/'+mn+'.'+mn)
 if not call('exists',{'path':F+'/'+mn},ASSET):call('create_material',{'folder_path':F,'asset_name':mn},MAT)
 for e in call('get_expressions',{'material_or_function':mat},MAT):call('delete_expression',{'material_or_function':mat,'expression':e},MAT)
 sample=call('add_expression',{'material_or_function':mat,'expression_class':ref('/Script/Engine.MaterialExpressionTextureSample')},MAT);props(sample,{'Texture':tex['refPath']})
 call('connect_to_output',{'expression':sample,'output_name':'RGB','material_property':'MP_EmissiveColor'},MAT)
 call('connect_to_output',{'expression':sample,'output_name':'A','material_property':'MP_OpacityMask'},MAT)
 props(mat,{'BlendMode':'BLEND_Masked','TwoSided':True,'ShadingModel':'MSM_Unlit','OpacityMaskClipValue':.6})
 call('recompile',{'material_or_function':mat},MAT)
 mesh=ref(F+'/SM_Prop_'+name+'.SM_Prop_'+name)
 for slot in call('get_material_slots',{'mesh':mesh},SM):call('set_material',{'mesh':mesh,'slot_name':slot,'material':mat},SM)
mesh=ref(F+'/SM_Prop_Bush.SM_Prop_Bush')
for slot in call('get_material_slots',{'mesh':mesh},SM):
 tier=slot[-1];call('set_material',{'mesh':mesh,'slot_name':slot,'material':ref('/Game/Environment/LayeredWoodland/M_StackedLeaf_'+tier+'.M_StackedLeaf_'+tier)},SM)
script='''import json
def tool(n,a):return execute_tool(n,json.dumps(a))['returnValue']
def run():
 counts={};errors=[]
 for tag in ['WoodlandBlenderArt','PixelWoodland']:
  actors=tool('editor_toolset.toolsets.scene.SceneTools.find_actors',{'name':'','tag':tag,'collision_channels':[]})
  for a in actors:
   cs=tool('editor_toolset.toolsets.actor.ActorTools.get_components',{'actor':a,'component_type':{'refPath':'/Script/Engine.StaticMeshComponent'}})
   if not cs:continue
   c=cs[0];p=json.loads(tool('editor_toolset.toolsets.object.ObjectTools.get_properties',{'instance':c,'properties':['StaticMesh','bVisible']}));path=p['StaticMesh']['refPath'];kind=None
   if 'Bush' in path:kind='Bush'
   elif 'Fern' in path or 'Grass' in path:kind='Grass'
   elif 'MossRock' in path:kind='Rock'
   if not kind:continue
   xf=tool('editor_toolset.toolsets.actor.ActorTools.get_actor_transform',{'actor':a});xf['rotation']={'pitch':0,'yaw':0,'roll':0}
   if kind=='Rock':xf['scale']={'x':1,'y':1,'z':1}
   tool('editor_toolset.toolsets.actor.ActorTools.set_actor_transform',{'actor':a,'xform':xf,'worldspace':True})
   tool('editor_toolset.toolsets.object.ObjectTools.set_properties',{'instance':c,'values':json.dumps({'StaticMesh':'/Game/Environment/PixelProps/SM_Prop_'+kind+'.SM_Prop_'+kind,'OverrideMaterials':[],'bUseDefaultCollision':False,'BodyInstance':{'CollisionProfileName':'NoCollision','CollisionEnabled':'NoCollision'},'bCanEverAffectNavigation':False})})
   counts[kind]=counts.get(kind,0)+1
   check=json.loads(tool('editor_toolset.toolsets.object.ObjectTools.get_properties',{'instance':c,'properties':['BodyInstance','bCanEverAffectNavigation']}))
   if check['BodyInstance']['collisionEnabled']!='NoCollision' or check['bCanEverAffectNavigation']:errors.append(a)
 cameras=tool('editor_toolset.toolsets.scene.SceneTools.find_actors',{'name':'Woodland_FollowCamera','tag':'','collision_channels':[]})
 cc=tool('editor_toolset.toolsets.actor.ActorTools.get_components',{'actor':cameras[0],'component_type':{'refPath':'/Script/Engine.CameraComponent'}})[0]
 tool('editor_toolset.toolsets.object.ObjectTools.set_properties',{'instance':cc,'values':json.dumps({'OrthoWidth':1450})})
 tool('editor_toolset.toolsets.asset.AssetTools.save_assets',{'asset_paths':[]})
 return {'replacements':counts,'collision_errors':errors,'ortho_width':1450}
'''
report=json.loads(call('execute_tool_script',{'script':script},PROG));(OUT/'migration.json').write_text(json.dumps(report,indent=2));assert not report['collision_errors'];print(report,flush=True)
