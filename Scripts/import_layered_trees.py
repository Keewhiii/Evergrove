"""Replace polygon-trunk trees with six-plane sprite assets and an ortho game camera."""
from build_companion_combat import call,ref,ROOT,ASSET,OBJ,SCENE
import json
F='/Game/Environment/LayeredWoodland'
SM='editor_toolset.toolsets.static_mesh.StaticMeshTools';MAT='editor_toolset.toolsets.material.MaterialTools';ACT='editor_toolset.toolsets.actor.ActorTools';PROG='editor_toolset.toolsets.programmatic.ProgrammaticToolset'
AUDIT=ROOT/'Saved/LayeredWoodlandAudit';AUDIT.mkdir(exist_ok=True)
for item in json.loads((ROOT/'ContentSource/LayeredWoodland/manifest.json').read_text()):
    if not call('exists',{'path':F+'/'+item['name']},ASSET):call('import_file',{'folder_path':F,'asset_name':item['name'],'source_file':item['file'],'import_materials':True,'import_textures':True,'combine_meshes':True},SM)
    mesh=ref(F+'/'+item['name']+'.'+item['name']);call('remove_collisions',{'mesh':mesh},SM)
    print(item['name'],call('get_triangle_count',{'mesh':mesh,'lod_index':0},SM),flush=True)
for suffix,texture_name in [('Trunk','T_FlatTrunk'),('Crown','T_LayeredCrown'),('Flower','T_LayeredFlower')]:
    m=ref(F+'/M_Layered_'+suffix+'.M_Layered_'+suffix);t=ref(F+'/'+texture_name+'.'+texture_name)
    call('set_properties',{'instance':t,'values':json.dumps({'Filter':'TF_Nearest','LODGroup':'TEXTUREGROUP_Pixels2D','NeverStream':True,'MipGenSettings':'TMGS_NoMipmaps'})},OBJ)
    call('set_properties',{'instance':m,'values':json.dumps({'BlendMode':'BLEND_Masked','TwoSided':True,'ShadingModel':'MSM_Unlit','OpacityMaskClipValue':.6 if suffix=='Trunk' else .5})},OBJ)
    for e in call('get_expressions',{'material_or_function':m},MAT):
        if 'TextureSample' in str(call('get_class',{'instance':e},OBJ)):
            call('set_properties',{'instance':e,'values':json.dumps({'Texture':t['refPath']})},OBJ)
            call('connect_to_output',{'expression':e,'output_name':'RGB','material_property':'MP_EmissiveColor'},MAT)
            call('connect_to_output',{'expression':e,'output_name':'A','material_property':'MP_OpacityMask'},MAT)
    call('recompile',{'material_or_function':m},MAT)

script='''import json
def find(name='',tag=''):
    return execute_tool('editor_toolset.toolsets.scene.SceneTools.find_actors',json.dumps({'name':name,'tag':tag,'collision_channels':[]}))['returnValue']
def components(a,kind='/Script/Engine.StaticMeshComponent'):
    return execute_tool('editor_toolset.toolsets.actor.ActorTools.get_components',json.dumps({'actor':a,'component_type':{'refPath':kind}}))['returnValue']
def props(c,keys):
    return json.loads(execute_tool('editor_toolset.toolsets.object.ObjectTools.get_properties',json.dumps({'instance':c,'properties':keys}))['returnValue'])
def setprops(c,p):
    r=execute_tool('editor_toolset.toolsets.object.ObjectTools.set_properties',json.dumps({'instance':c,'values':json.dumps(p)}))['returnValue']
    if not r:raise RuntimeError(str(p))
def transform(a):
    return execute_tool('editor_toolset.toolsets.actor.ActorTools.get_actor_transform',json.dumps({'actor':a}))['returnValue']
def move(a,xf):
    execute_tool('editor_toolset.toolsets.actor.ActorTools.set_actor_transform',json.dumps({'actor':a,'xform':xf,'worldspace':True}))
def run():
    changes=[]
    for a in find(tag='WoodlandBlenderArt'):
        c=components(a)[0];p=props(c,['StaticMesh'])['StaticMesh']['refPath']
        if 'SM_Pixel_CardTree_' in p:
            letter=p.split('SM_Pixel_CardTree_')[-1][0];name='SM_Layered_Tree_'+letter;xf=transform(a)
            changes.append({'actor':a,'old_mesh':p,'old_transform':xf.copy()})
            setprops(c,{'StaticMesh':'/Game/Environment/LayeredWoodland/'+name+'.'+name,'OverrideMaterials':[]})
            xf['rotation']={'pitch':0,'yaw':0,'roll':0};move(a,xf)
    cameras=find(name='Woodland_FollowCamera');c=components(cameras[0],'/Script/Engine.CameraComponent')[0]
    before=props(c,['ProjectionMode','OrthoWidth','FieldOfView'])
    setprops(c,{'ProjectionMode':'Orthographic','OrthoWidth':2400,'bAutoCalculateOrthoPlanes':True,'bUpdateOrthoPlanes':True})
    after=props(c,['ProjectionMode','OrthoWidth'])
    execute_tool('editor_toolset.toolsets.asset.AssetTools.save_assets',json.dumps({'asset_paths':[]}))
    return {'replaced_trees':len(changes),'changes':changes,'camera_before':before,'camera_after':after}
'''
report=call('execute_tool_script',{'script':script},PROG);(AUDIT/'migration.json').write_text(report)
d=json.loads(report);print(json.dumps({'replaced_trees':d['replaced_trees'],'camera':d['camera_after']}),flush=True)
