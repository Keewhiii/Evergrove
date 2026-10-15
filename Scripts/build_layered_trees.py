"""Blender: six flat sprite planes per tree, aligned to the orthographic RPG camera."""
import bpy, math, json
from mathutils import Vector
from pathlib import Path
ROOT=Path(r'E:\UE5 Projects\AdventureRPG\ContentSource\LayeredWoodland')
(ROOT/'FBX').mkdir(parents=True,exist_ok=True)
scene=bpy.data.scenes.get('LayeredWoodland_Studio') or bpy.data.scenes.new('LayeredWoodland_Studio');bpy.context.window.scene=scene
for obj in list(scene.objects):
    if obj.get('layered_tree'):bpy.data.objects.remove(obj,do_unlink=True)
scene.unit_settings.system='METRIC'
up=Vector((0,math.sin(math.radians(38)),math.cos(math.radians(38))))
normal=Vector((0,-math.cos(math.radians(38)),math.sin(math.radians(38))))
right=Vector((1,0,0))
materials={};images={}
for kind,file in [('Trunk','T_FlatTrunk.png'),('Crown','T_LayeredCrown.png'),('Flower','T_LayeredFlower.png')]:
    im=bpy.data.images.load(str(ROOT/file),check_existing=True);images[kind]=im
    mat=bpy.data.materials.get('M_Layered_'+kind) or bpy.data.materials.new('M_Layered_'+kind);mat.use_nodes=True
    nodes=mat.node_tree.nodes;bsdf=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
    tex=next((n for n in nodes if n.type=='TEX_IMAGE'),None) or nodes.new('ShaderNodeTexImage');tex.image=im;tex.interpolation='Closest'
    mat.node_tree.links.new(tex.outputs['Color'],bsdf.inputs['Base Color']);mat.node_tree.links.new(tex.outputs['Alpha'],bsdf.inputs['Alpha']);bsdf.inputs['Roughness'].default_value=1
    materials[kind]=mat

# Crop the trunk by UVs, preserving the generated PNG and its alpha untouched.
im=images['Trunk'];w,h=im.size;pixels=list(im.pixels);xs=[];ys=[]
for y in range(h):
    for x in range(w):
        if pixels[(y*w+x)*4+3]>.6:xs.append(x);ys.append(y)
trunk_uv=(min(xs)/w,min(ys)/h,(max(xs)+1)/w,(max(ys)+1)/h)

def quad(name,points,coords,mat):
    mesh=bpy.data.meshes.new(name);mesh.from_pydata([tuple(p) for p in points],[],[(0,1,2,3)]);mesh.update();uv=mesh.uv_layers.new()
    for li,co in zip(mesh.polygons[0].loop_indices,coords):uv.data[li].uv=co
    ob=bpy.data.objects.new(name,mesh);scene.collection.objects.link(ob);mesh.materials.append(mat);ob['layered_tree']=True
    return ob

manifest=[]
for variant in range(3):
    letter=chr(65+variant);parts=[]
    x0,y0,x1,y1=trunk_uv
    parts.append(quad(letter+'_Trunk_2D',[-right*.70,right*.70,right*.70+up*1.52,-right*.70+up*1.52],[(x0,y0),(x1,y0),(x1,y1),(x0,y1)],materials['Trunk']))
    width=3.3*(1+variant*.035);height=3.7
    bands=[(0,.31,-.24),(.22,.49,-.12),(.40,.65,0),(.55,.80,.12),(.64,1,.24)]
    for layer,(bottom,top,depth) in enumerate(bands):
        origin=up*.88+normal*depth
        points=[origin-right*width/2+up*bottom*height,origin+right*width/2+up*bottom*height,origin+right*width/2+up*top*height,origin-right*width/2+up*top*height]
        ob=quad(letter+'_Canopy_Layer_'+str(layer+1),points,[(0,bottom),(1,bottom),(1,top),(0,top)],materials['Flower' if variant==1 else 'Crown'])
        ob['layer_depth_m']=depth;ob['uv_band']=[bottom,top];parts.append(ob)
    bpy.ops.object.select_all(action='DESELECT')
    for ob in parts:ob.select_set(True)
    bpy.context.view_layer.objects.active=parts[0]
    name='SM_Layered_Tree_'+letter;file=ROOT/'FBX'/(name+'.fbx')
    bpy.ops.export_scene.fbx(filepath=str(file),use_selection=True,object_types={'MESH'},apply_unit_scale=True,axis_forward='-Y',axis_up='Z',bake_anim=False,path_mode='COPY')
    manifest.append({'name':name,'file':str(file),'planes':6,'triangles':12,'canopy_depth_m':.48,'objects':[o.name for o in parts]})
    group=bpy.data.objects.new('LayeredTree_'+letter,None);scene.collection.objects.link(group);group['layered_tree']=True;group['construction']='One flat trunk sprite plus five overlapping canopy sprite planes'
    for ob in parts:ob.parent=group
    group.location.x=variant*4.5
(ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2))
# Orthographic studio camera matches the gameplay view, so parallel trunks stay upright.
camera_data=bpy.data.cameras.new('LayeredPreview');camera_data.type='ORTHO';camera_data.ortho_scale=12
camera=bpy.data.objects.new('LayeredPreview',camera_data);scene.collection.objects.link(camera);camera['layered_tree']=True
target=Vector((4.5,0,1.9));camera.location=target+normal*15;camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();scene.camera=camera
world=bpy.data.worlds.new('LayeredStudio');world.use_nodes=True
bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs[0].default_value=(.18,.23,.20,1);bg.inputs[1].default_value=.8;scene.world=world
scene.render.resolution_x=1400;scene.render.resolution_y=700;scene.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'AdventureRPG_LayeredWoodland.blend'))
print('LAYERED_TREES '+json.dumps(manifest))
