"""Apply the reference-matched painted crown textures to the Blender-exported trees."""
from build_companion_combat import call,ref,ROOT,ASSET,OBJ
import json
F='/Game/Environment/PixelWoodland'
TEX='editor_toolset.toolsets.texture.TextureTools';MAT='editor_toolset.toolsets.material.MaterialTools'
for suffix,name in [('Crown','T_ScallopedCrown'),('Flower','T_ScallopedFlower')]:
    t=ref(F+'/'+name+'.'+name)
    if not call('exists',{'path':F+'/'+name},ASSET):
        call('import_file',{'folder_path':F,'asset_name':name,'source_file':str(ROOT/'ContentSource/PixelWoodland'/(name+'.png'))},TEX)
    call('set_properties',{'instance':t,'values':json.dumps({'Filter':'TF_Nearest','LODGroup':'TEXTUREGROUP_Pixels2D','NeverStream':True,'MipGenSettings':'TMGS_NoMipmaps'})},OBJ)
    m=ref(F+'/M_PixelLeaf_'+suffix+'.M_PixelLeaf_'+suffix)
    for e in call('get_expressions',{'material_or_function':m},MAT):
        if 'TextureSample' in str(call('get_class',{'instance':e},OBJ)):
            call('set_properties',{'instance':e,'values':json.dumps({'Texture':t['refPath']})},OBJ)
            call('connect_to_output',{'expression':e,'output_name':'RGB','material_property':'MP_EmissiveColor'},MAT)
            call('connect_to_output',{'expression':e,'output_name':'A','material_property':'MP_OpacityMask'},MAT)
    call('recompile',{'material_or_function':m},MAT)
    print('Applied '+name,flush=True)
call('save_assets',{'asset_paths':[]},ASSET)
