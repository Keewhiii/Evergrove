"""True 2.5D trees: one trunk billboard and five complete flat leaf tiers at separate heights."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'E:\UE5 Projects\AdventureRPG\ContentSource\LayeredWoodland')
scene=bpy.data.scenes.get('StackedLeaf_Studio') or bpy.data.scenes.new('StackedLeaf_Studio');bpy.context.window.scene=scene
for obj in list(scene.objects):
    if obj.get('stacked_leaf'):bpy.data.objects.remove(obj,do_unlink=True)
up=Vector((0,math.sin(math.radians(38)),math.cos(math.radians(38))))
eye=Vector((0,-math.cos(math.radians(38)),math.sin(math.radians(38))))
leaf_v=Vector((0,math.cos(math.radians(20)),math.sin(math.radians(20))))
right=Vector((1,0,0))
leaf_image=bpy.data.images.load(str(ROOT/'T_LeafTier.png'),check_existing=True)
PALETTES=[[(9,58,40),(22,91,51)],[(18,79,38),(40,112,48)],[(30,100,36),(62,133,43)],[(45,118,34),(94,157,39)],[(62,137,27),(142,192,41)]]
def linear(c):
    c=c/255;return c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4
materials=[]
for tier,(low,high) in enumerate(PALETTES):
    mat=bpy.data.materials.get('M_StackedLeaf_'+str(tier)) or bpy.data.materials.new('M_StackedLeaf_'+str(tier));mat.use_nodes=True
    nodes=mat.node_tree.nodes;nodes.clear();out=nodes.new('ShaderNodeOutputMaterial');b=nodes.new('ShaderNodeBsdfPrincipled');tex=nodes.new('ShaderNodeTexImage');tex.image=leaf_image;tex.interpolation='Closest'
    sep=nodes.new('ShaderNodeSeparateColor');ramp=nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color=tuple(linear(c) for c in low)+(1,);ramp.color_ramp.elements[1].color=tuple(linear(c) for c in high)+(1,)
    mat.node_tree.links.new(tex.outputs['Color'],sep.inputs['Color']);mat.node_tree.links.new(sep.outputs['Green'],ramp.inputs[0]);mat.node_tree.links.new(ramp.outputs['Color'],b.inputs['Base Color']);mat.node_tree.links.new(tex.outputs['Alpha'],b.inputs['Alpha']);mat.node_tree.links.new(b.outputs[0],out.inputs['Surface']);b.inputs['Roughness'].default_value=1
    materials.append(mat)
trunk_mat=bpy.data.materials['M_Layered_Trunk'];trunk_image=bpy.data.images.load(str(ROOT/'T_FlatTrunk.png'),check_existing=True)
pix=list(trunk_image.pixels);w,h=trunk_image.size;opaque=[(i%w,i//w) for i in range(w*h) if pix[i*4+3]>.6]
uvbox=(min(x for x,y in opaque)/w,min(y for x,y in opaque)/h,(max(x for x,y in opaque)+1)/w,(max(y for x,y in opaque)+1)/h)
palette_mat=bpy.data.materials.get('M_LayeredFlowerPixels') or bpy.data.materials['M_PixelWoodland'].copy();palette_mat.name='M_LayeredFlowerPixels';palette_image=bpy.data.images.load(str(ROOT/'T_LayeredPalette.png'),check_existing=True)
next(n for n in palette_mat.node_tree.nodes if n.type=='TEX_IMAGE').image=palette_image
def quad(name,points,uvs,mat):
    me=bpy.data.meshes.new(name);me.from_pydata([tuple(p) for p in points],[],[(0,1,2,3)]);me.update();uv=me.uv_layers.new()
    for li,co in zip(me.polygons[0].loop_indices,uvs):uv.data[li].uv=co
    ob=bpy.data.objects.new(name,me);scene.collection.objects.link(ob);me.materials.append(mat);ob['stacked_leaf']=True;return ob
manifest=[]
for variant in range(3):
    letter=chr(65+variant);parts=[];x0,y0,x1,y1=uvbox
    parts.append(quad(letter+'_FlatTrunk',[-right*.7,right*.7,right*.7+up*1.52,-right*.7+up*1.52],[(x0,y0),(x1,y0),(x1,y1),(x0,y1)],trunk_mat))
    tiers=[(2.4,1.5),(2.85,1.5),(3.3,1.3),(3.75,1.08),(4.2,.82)]
    for tier,(height,radius) in enumerate(tiers):
        radius*=1+variant*.025;origin=Vector((0,0,height))
        points=[origin-right*radius-leaf_v*radius,origin+right*radius-leaf_v*radius,origin+right*radius+leaf_v*radius,origin-right*radius+leaf_v*radius]
        ob=quad(letter+'_LeafTier_'+str(tier+1),points,[(0,0),(1,0),(1,1),(0,1)],materials[tier]);ob['height_m']=height;ob['complete_leaf_sprite']=True;parts.append(ob)
    if variant==1:
        for flower,(x,t,tier,color) in enumerate([(-.8,-.85,1,23),(-.7,-.7,2,21),(.8,-.82,1,15),(-.48,-.65,3,23),(.55,-.72,2,21)]):
            center=Vector((x,0,tiers[tier][0]))+leaf_v*t+eye*.04;s=.10
            for petal,(dx,dy,c) in enumerate([(-1,0,color),(1,0,color),(0,1,color),(0,-1,color),(0,0,16)]):
                origin=center+right*dx*s+up*dy*s;uv=((c%8+.5)/8,(c//8+.5)/8)
                parts.append(quad(letter+'_Flower_'+str(flower)+'_'+str(petal),[origin-right*s/2-up*s/2,origin+right*s/2-up*s/2,origin+right*s/2+up*s/2,origin-right*s/2+up*s/2],[uv]*4,palette_mat))
    bpy.ops.object.select_all(action='DESELECT')
    for ob in parts:ob.select_set(True)
    bpy.context.view_layer.objects.active=parts[0];name='SM_Stacked2D_Tree_'+letter;file=ROOT/'FBX'/(name+'.fbx')
    bpy.ops.export_scene.fbx(filepath=str(file),use_selection=True,object_types={'MESH'},apply_unit_scale=True,axis_forward='-Y',axis_up='Z',bake_anim=False,path_mode='COPY')
    group=bpy.data.objects.new('Stacked2D_Tree_'+letter,None);scene.collection.objects.link(group);group['stacked_leaf']=True
    for ob in parts:ob.parent=group
    group.location.x=variant*4.5
    manifest.append({'name':name,'file':str(file),'core_planes':6,'trunk_planes':1,'complete_canopy_planes':5,'tier_heights_m':[t[0] for t in tiers],'triangles':len(parts)*2,'objects':[o.name for o in parts]})
(ROOT/'stacked_manifest.json').write_text(json.dumps(manifest,indent=2));(ROOT/'tier_palette.json').write_text(json.dumps(PALETTES))
cam_data=bpy.data.cameras.new('StackedPreview');cam_data.type='ORTHO';cam_data.ortho_scale=13.5
cam=bpy.data.objects.new('StackedPreview',cam_data);scene.collection.objects.link(cam);cam['stacked_leaf']=True;target=Vector((4.5,0,2.2));cam.location=target+eye*15;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();scene.camera=cam
scene.world=bpy.data.worlds.get('LayeredStudio');scene.render.resolution_x=1500;scene.render.resolution_y=800;scene.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'AdventureRPG_LayeredWoodland.blend'))
print('STACKED_2D '+json.dumps(manifest))
