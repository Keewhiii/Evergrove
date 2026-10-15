from build_companion_combat import call, ref, ROOT, ASSET, OBJ
import json
SM='editor_toolset.toolsets.static_mesh.StaticMeshTools'
MAT='editor_toolset.toolsets.material.MaterialTools'
FOLDER='/Game/Environment/PixelWoodland'
for item in json.loads((ROOT/'ContentSource/PixelWoodland/card_manifest.json').read_text()):
    item['name']+='_Front' if 'CardTree_' in item['name'] else ''
    if not call('exists',{'path':FOLDER+'/'+item['name']},ASSET):call('import_file',{'folder_path':FOLDER,'asset_name':item['name'],'source_file':item['file'],'import_materials':True,'import_textures':True,'combine_meshes':True},SM)
    call('remove_collisions',{'mesh':ref(FOLDER+'/'+item['name']+'.'+item['name'])},SM)
for suffix in ['Crown','Flower']:
    painted='T_ScallopedCrown' if suffix=='Crown' else 'T_ScallopedFlower'
    name=painted if call('exists',{'path':FOLDER+'/'+painted},ASSET) else 'T_PixelLeaf_'+suffix
    texture=ref(FOLDER+'/'+name+'.'+name)
    call('set_properties',{'instance':texture,'values':json.dumps({'Filter':'TF_Nearest','LODGroup':'TEXTUREGROUP_Pixels2D','NeverStream':True})},OBJ)
    mat=ref(FOLDER+'/M_PixelLeaf_'+suffix+'.M_PixelLeaf_'+suffix)
    call('set_properties',{'instance':mat,'values':json.dumps({'BlendMode':'BLEND_Masked','TwoSided':True,'OpacityMaskClipValue':.5,'ShadingModel':'MSM_Unlit'})},OBJ)
    for e in call('get_expressions',{'material_or_function':mat},MAT):
        cls=call('get_class',{'instance':e},OBJ)
        if 'TextureSample' in str(cls):
            call('set_properties',{'instance':e,'values':json.dumps({'Texture':texture['refPath']})},OBJ)
            call('connect_to_output',{'expression':e,'output_name':'A','material_property':'MP_OpacityMask'},MAT)
            call('connect_to_output',{'expression':e,'output_name':'RGB','material_property':'MP_EmissiveColor'},MAT)
    call('recompile',{'material_or_function':mat},MAT)
script='''import json
def find():
    return execute_tool('editor_toolset.toolsets.scene.SceneTools.find_actors',json.dumps({'name':'','tag':'WoodlandBlenderArt','collision_channels':[]}))['returnValue']
def comp(a):
    return execute_tool('editor_toolset.toolsets.actor.ActorTools.get_components',json.dumps({'actor':a,'component_type':{'refPath':'/Script/Engine.StaticMeshComponent'}}))['returnValue'][0]
def mesh(c):
    return json.loads(execute_tool('editor_toolset.toolsets.object.ObjectTools.get_properties',json.dumps({'instance':c,'properties':['StaticMesh']}))['returnValue'])['StaticMesh']['refPath']
def setprops(c,p):
    execute_tool('editor_toolset.toolsets.object.ObjectTools.set_properties',json.dumps({'instance':c,'values':json.dumps(p)}))
def run():
    count=0
    for a in find():
        c=comp(a);p=mesh(c)
        if '/PixelWoodland/' in p and 'SM_Pixel_Tree_' in p:
            variant=p.split('SM_Pixel_Tree_')[-1][0];name='SM_Pixel_CardTree_'+variant+'_Front'
            setprops(c,{'StaticMesh':'/Game/Environment/PixelWoodland/'+name+'.'+name,'OverrideMaterials':[]});count+=1
        if 'SM_Pixel_Bush' in p:setprops(c,{'StaticMesh':'/Game/Environment/PixelWoodland/SM_Pixel_CardBush.SM_Pixel_CardBush','OverrideMaterials':[]})
        if 'SM_Woodland_TrailSkin' in p:setprops(c,{'StaticMesh':'/Game/Environment/PixelWoodland/SM_Pixel_Trail.SM_Pixel_Trail','OverrideMaterials':[]})
    execute_tool('editor_toolset.toolsets.asset.AssetTools.save_assets',json.dumps({'asset_paths':[]}))
    return {'pixel_leaf_card_trees':count}
'''
print(call('execute_tool_script',{'script':script},'editor_toolset.toolsets.programmatic.ProgrammaticToolset'))
