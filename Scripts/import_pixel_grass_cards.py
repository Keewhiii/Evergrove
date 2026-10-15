from build_companion_combat import call,ref,ROOT,ASSET,OBJ
import json
F='/Game/Environment/PixelWoodland'
SM='editor_toolset.toolsets.static_mesh.StaticMeshTools';MAT='editor_toolset.toolsets.material.MaterialTools'
if not call('exists',{'path':F+'/SM_Pixel_CardGrass'},ASSET):
    call('import_file',{'folder_path':F,'asset_name':'SM_Pixel_CardGrass','source_file':str(ROOT/'ContentSource/PixelWoodland/FBX/SM_Pixel_CardGrass.fbx'),'import_materials':True,'import_textures':True,'combine_meshes':True},SM)
m=ref(F+'/M_PixelLeaf_Grass.M_PixelLeaf_Grass');t=ref(F+'/T_PixelLeaf_Grass.T_PixelLeaf_Grass')
call('set_properties',{'instance':t,'values':json.dumps({'Filter':'TF_Nearest','LODGroup':'TEXTUREGROUP_Pixels2D','NeverStream':True})},OBJ)
call('set_properties',{'instance':m,'values':json.dumps({'BlendMode':'BLEND_Masked','TwoSided':True,'ShadingModel':'MSM_Unlit'})},OBJ)
for e in call('get_expressions',{'material_or_function':m},MAT):
    if 'TextureSample' in str(call('get_class',{'instance':e},OBJ)):
        call('connect_to_output',{'expression':e,'output_name':'A','material_property':'MP_OpacityMask'},MAT)
        call('connect_to_output',{'expression':e,'output_name':'RGB','material_property':'MP_EmissiveColor'},MAT)
call('recompile',{'material_or_function':m},MAT)
script='''import json
def find():
    return execute_tool('editor_toolset.toolsets.scene.SceneTools.find_actors',json.dumps({'name':'','tag':'PixelWoodland','collision_channels':[]}))['returnValue']
def comp(a):
    return execute_tool('editor_toolset.toolsets.actor.ActorTools.get_components',json.dumps({'actor':a,'component_type':{'refPath':'/Script/Engine.StaticMeshComponent'}}))['returnValue'][0]
def props(c):
    return json.loads(execute_tool('editor_toolset.toolsets.object.ObjectTools.get_properties',json.dumps({'instance':c,'properties':['StaticMesh']}))['returnValue'])
def run():
    count=0
    for a in find():
        c=comp(a)
        if 'SM_Pixel_TallGrass' in str(props(c)['StaticMesh']):
            execute_tool('editor_toolset.toolsets.object.ObjectTools.set_properties',json.dumps({'instance':c,'values':json.dumps({'StaticMesh':'/Game/Environment/PixelWoodland/SM_Pixel_CardGrass.SM_Pixel_CardGrass','OverrideMaterials':[]})}));count+=1
    execute_tool('editor_toolset.toolsets.asset.AssetTools.save_assets',json.dumps({'asset_paths':[]}))
    return {'chunky_pixel_grass_clumps':count}
'''
print(call('execute_tool_script',{'script':script},'editor_toolset.toolsets.programmatic.ProgrammaticToolset'))
