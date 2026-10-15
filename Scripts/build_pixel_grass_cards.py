"""Original chunky tall-grass sprite on a Blender mesh, for the fixed RPG camera."""
import bpy,math,json
from pathlib import Path
root=Path(r'E:\UE5 Projects\AdventureRPG\ContentSource\PixelWoodland')
W,H=32,40;cells={}
pal=[(25,57,33),(43,78,35),(67,101,36),(97,124,36),(125,145,39),(86,73,37)]
for index,(lean,h) in enumerate([(-12,30),(12,28),(2,38)]):
    for y in range(h):
        t=y/h;cx=16+int(lean*t);width=int(1+4.6*math.sin(t*math.pi)**.6)
        for x in range(cx-width,cx+width+1):
            if not 0<=x<W:continue
            side=x-cx
            c=1 if side<-2 else 2 if side<1 else 3 if side<3 else 4
            if (x//2+y//2)%4==0:c=max(0,c-1)
            if abs(side)<1 and y<h*.72:c=5 if y%6<3 else 1
            cells[x,y]=pal[c]
pixels=[]
for y in range(H):
    for x in range(W):
        color=cells.get((x,y));pixels.extend([v/255 for v in color]+[1] if color else [0,0,0,0])
im=bpy.data.images.get('T_PixelLeaf_Grass') or bpy.data.images.new('T_PixelLeaf_Grass',W,H,alpha=True);im.pixels.foreach_set(pixels);im.filepath_raw=str(root/'T_PixelLeaf_Grass.png');im.file_format='PNG';im.save()
mat=bpy.data.materials.get('M_PixelLeaf_Grass') or bpy.data.materials.new('M_PixelLeaf_Grass');mat.use_nodes=True
bsdf=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');tex=next((n for n in mat.node_tree.nodes if n.type=='TEX_IMAGE'),None) or mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;tex.interpolation='Closest'
mat.node_tree.links.new(tex.outputs['Color'],bsdf.inputs['Base Color']);mat.node_tree.links.new(tex.outputs['Alpha'],bsdf.inputs['Alpha'])
me=bpy.data.meshes.new('PixelGrassCard');me.from_pydata([(-.4,0,.02),(.4,0,.02),(.4,.5,.85),(-.4,.5,.85)],[],[(0,1,2,3)]);me.update();uv=me.uv_layers.new()
for li,co in zip(me.polygons[0].loop_indices,[(0,0),(1,0),(1,1),(0,1)]):uv.data[li].uv=co
obj=bpy.data.objects.new('SM_Pixel_CardGrass',me);bpy.context.scene.collection.objects.link(obj);obj['pixel_card']=True;me.materials.append(mat)
bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
bpy.ops.export_scene.fbx(filepath=str(root/'FBX/SM_Pixel_CardGrass.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,axis_forward='-Y',axis_up='Z',bake_anim=False,path_mode='COPY')
obj.location=(0,4,0)
bpy.ops.wm.save_as_mainfile(filepath=str(root/'AdventureRPG_PixelWoodland.blend'))
print('Chunky grass leaf card exported')
