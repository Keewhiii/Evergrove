"""Run in Blender to render the three final flat-layer trees from the game angle."""
import bpy
from pathlib import Path
root=Path(r'E:\UE5 Projects\AdventureRPG')
scene=bpy.data.scenes['StackedLeaf_Studio'];bpy.context.window.scene=scene
for name in ['M_Layered_Trunk','M_LayeredFlowerPixels']+['M_StackedLeaf_'+str(i) for i in range(5)]:
    m=bpy.data.materials[name];nodes=m.node_tree.nodes;b=next(n for n in nodes if n.type=='BSDF_PRINCIPLED');t=next(n for n in nodes if n.type=='TEX_IMAGE')
    source=next((n for n in nodes if n.type=='VALTORGB'),t)
    m.node_tree.links.new(source.outputs['Color'],b.inputs['Emission Color']);b.inputs['Emission Strength'].default_value=1
    clip=next((n for n in nodes if n.type=='MATH'),None) or nodes.new('ShaderNodeMath')
    clip.operation=next(i.identifier for i in clip.bl_rna.properties['operation'].enum_items if i.identifier=='GREATER_THAN')
    clip.inputs[1].default_value=.6 if name=='M_Layered_Trunk' else .5;m.node_tree.links.new(t.outputs['Alpha'],clip.inputs[0]);m.node_tree.links.new(clip.outputs[0],b.inputs['Alpha'])
scene.camera.data.ortho_scale=13.5
scene.render.resolution_x=1500;scene.render.resolution_y=800;scene.render.resolution_percentage=100
scene.render.image_settings.file_format=next(i.identifier for i in scene.render.image_settings.bl_rna.properties['file_format'].enum_items if i.identifier=='PNG')
scene.render.film_transparent=True
transforms=[i.identifier for i in scene.view_settings.bl_rna.properties['view_transform'].enum_items]
if 'Standard' in transforms:scene.view_settings.view_transform='Standard'
scene.render.filepath=str(root/'Saved/LayeredWoodlandAudit/LayeredTrees_Front.png')
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(root/'ContentSource/LayeredWoodland/AdventureRPG_LayeredWoodland.blend'))
print('LayeredTrees_Front.png rendered')
