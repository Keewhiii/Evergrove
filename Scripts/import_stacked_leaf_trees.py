"""Import complete flat leaf tiers, build palette shaders, and update the existing trees."""
from build_companion_combat import call,ref,ROOT,ASSET,OBJ
import json
F='/Game/Environment/LayeredWoodland';SM='editor_toolset.toolsets.static_mesh.StaticMeshTools';MAT='editor_toolset.toolsets.material.MaterialTools';TEX='editor_toolset.toolsets.texture.TextureTools';PROG='editor_toolset.toolsets.programmatic.ProgrammaticToolset'
SOURCE=ROOT/'ContentSource/LayeredWoodland';AUDIT=ROOT/'Saved/LayeredWoodlandAudit';AUDIT.mkdir(exist_ok=True)
meshes=[]
for item in json.loads((SOURCE/'stacked_manifest.json').read_text()):
    mesh=ref(F+'/'+item['name']+'.'+item['name'])
    if not call('exists',{'path':F+'/'+item['name']},ASSET):call('import_file',{'folder_path':F,'asset_name':item['name'],'source_file':item['file'],'import_materials':True,'import_textures':True,'combine_meshes':True},SM)
    call('remove_collisions',{'mesh':mesh},SM)
    actual=call('get_triangle_count',{'mesh':mesh,'lod_index':0},SM)
    if actual!=item['triangles']:raise RuntimeError('Unexpected geometry in '+item['name'])
    meshes.append({'name':item['name'],'triangles':actual,'core_planes':6});print(item['name'],actual,flush=True)
for name in ['T_LeafTier','T_FlatTrunk','T_LayeredPalette']:
    if not call('exists',{'path':F+'/'+name},ASSET):call('import_file',{'folder_path':F,'asset_name':name,'source_file':str(SOURCE/(name+'.png'))},TEX)
    call('set_properties',{'instance':ref(F+'/'+name+'.'+name),'values':json.dumps({'Filter':'TF_Nearest','LODGroup':'TEXTUREGROUP_Pixels2D','NeverStream':True,'MipGenSettings':'TMGS_NoMipmaps'})},OBJ)
def node(mat,typ):return call('add_expression',{'material_or_function':mat,'expression_class':ref('/Script/Engine.MaterialExpression'+typ)},MAT)
def props(o,p):call('set_properties',{'instance':o,'values':json.dumps(p)},OBJ)
def wire(a,out,b,pin):call('connect_expressions',{'from_expression':a,'from_output_name':out,'to_expression':b,'to_input_name':pin},MAT)
def output(a,out,prop):call('connect_to_output',{'expression':a,'output_name':out,'material_property':prop},MAT)
def linear(v):
    v=v/255;return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
for tier,(low,high) in enumerate(json.loads((SOURCE/'tier_palette.json').read_text())):
    name='M_StackedLeaf_'+str(tier);mat=ref(F+'/'+name+'.'+name)
    if not call('exists',{'path':F+'/'+name},ASSET):call('create_material',{'folder_path':F,'asset_name':name},MAT)
    for e in call('get_expressions',{'material_or_function':mat},MAT):call('delete_expression',{'material_or_function':mat,'expression':e},MAT)
    tex=node(mat,'TextureSample');props(tex,{'Texture':F+'/T_LeafTier.T_LeafTier'})
    a=node(mat,'VectorParameter');b=node(mat,'VectorParameter');lerp=node(mat,'LinearInterpolate')
    for n,c,label in [(a,low,'Shadow'),(b,high,'Highlight')]:props(n,{'ParameterName':label,'DefaultValue':{'R':linear(c[0]),'G':linear(c[1]),'B':linear(c[2]),'A':1}})
    wire(a,'RGB',lerp,'A');wire(b,'RGB',lerp,'B');wire(tex,'G',lerp,'Alpha');output(lerp,'','MP_EmissiveColor');output(tex,'A','MP_OpacityMask')
    props(mat,{'BlendMode':'BLEND_Masked','TwoSided':True,'ShadingModel':'MSM_Unlit','OpacityMaskClipValue':.5});call('recompile',{'material_or_function':mat},MAT)
for name,texture,clip in [('M_Layered_Trunk','T_FlatTrunk',.6),('M_LayeredFlowerPixels','T_LayeredPalette',.5)]:
    mat=ref(F+'/'+name+'.'+name);props(mat,{'BlendMode':'BLEND_Masked','TwoSided':True,'ShadingModel':'MSM_Unlit','OpacityMaskClipValue':clip})
    expressions=call('get_expressions',{'material_or_function':mat},MAT)
    samples=[e for e in expressions if 'TextureSample' in str(call('get_class',{'instance':e},OBJ))]
    if not samples:samples=[node(mat,'TextureSample')]
    for tex in samples:
        props(tex,{'Texture':F+'/'+texture+'.'+texture});output(tex,'RGB','MP_EmissiveColor');output(tex,'A','MP_OpacityMask')
    call('recompile',{'material_or_function':mat},MAT)

script='''import json
def find():
    return execute_tool('editor_toolset.toolsets.scene.SceneTools.find_actors',json.dumps({'name':'','tag':'WoodlandBlenderArt','collision_channels':[]}))['returnValue']
def component(a):
    return execute_tool('editor_toolset.toolsets.actor.ActorTools.get_components',json.dumps({'actor':a,'component_type':{'refPath':'/Script/Engine.StaticMeshComponent'}}))['returnValue'][0]
def props(c,keys):
    return json.loads(execute_tool('editor_toolset.toolsets.object.ObjectTools.get_properties',json.dumps({'instance':c,'properties':keys}))['returnValue'])
def setmesh(c,name):
    execute_tool('editor_toolset.toolsets.object.ObjectTools.set_properties',json.dumps({'instance':c,'values':json.dumps({'StaticMesh':'/Game/Environment/LayeredWoodland/'+name+'.'+name,'OverrideMaterials':[]})}))
def transform(a):
    return execute_tool('editor_toolset.toolsets.actor.ActorTools.get_actor_transform',json.dumps({'actor':a}))['returnValue']
def move(a,xf):
    execute_tool('editor_toolset.toolsets.actor.ActorTools.set_actor_transform',json.dumps({'actor':a,'xform':xf,'worldspace':True}))
def run():
    count=0;errors=[];placements=[]
    for a in find():
        c=component(a);path=props(c,['StaticMesh'])['StaticMesh']['refPath']
        if 'SM_Layered_Tree_' in path or 'SM_Stacked2D_Tree_' in path:
            variant=path.split('.')[-1][-1];name='SM_Stacked2D_Tree_'+variant;setmesh(c,name)
            xf=transform(a);xf['rotation']={'pitch':0,'yaw':0,'roll':0};move(a,xf)
            p=props(c,['BodyInstance','bCanEverAffectNavigation'])
            if p['BodyInstance']['collisionEnabled']!='NoCollision' or p['bCanEverAffectNavigation']:errors.append(a)
            placements.append({'actor':a,'mesh':name,'transform':xf});count+=1
    execute_tool('editor_toolset.toolsets.asset.AssetTools.save_assets',json.dumps({'asset_paths':[]}))
    return {'stacked_trees':count,'collision_navigation_errors':errors,'placements':placements}
'''
report=json.loads(call('execute_tool_script',{'script':script},PROG));report['meshes']=meshes
(AUDIT/'stacked_validation.json').write_text(json.dumps(report,indent=2))
if report['collision_navigation_errors'] or report['stacked_trees']!=87:raise RuntimeError('Stacked tree validation failed')
print('STACKED_TREES_VALIDATED='+str(report['stacked_trees']),flush=True)
