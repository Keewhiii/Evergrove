"""Flat sprite props authored in the connected Blender, exported for Unreal."""
import bpy, math, json
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'E:\UE5 Projects\AdventureRPG\ContentSource\PixelProps')
scene=bpy.data.scenes.get('PixelProps_Studio') or bpy.data.scenes.new('PixelProps_Studio')
bpy.context.window.scene=scene
for o in list(scene.objects):bpy.data.objects.remove(o,do_unlink=True)
up=Vector((0,math.sin(math.radians(38)),math.cos(math.radians(38))))
right=Vector((1,0,0)); leaf=Vector((0,math.cos(math.radians(20)),math.sin(math.radians(20))))
def mat(name,path):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True
 n=m.node_tree.nodes;n.clear();out=n.new('ShaderNodeOutputMaterial');b=n.new('ShaderNodeBsdfPrincipled');t=n.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(path),check_existing=True);t.interpolation='Closest'
 m.node_tree.links.new(t.outputs['Color'],b.inputs['Base Color']);m.node_tree.links.new(t.outputs['Color'],b.inputs['Emission Color']);b.inputs['Emission Strength'].default_value=1
 cut=n.new('ShaderNodeMath');cut.operation=next(e.identifier for e in cut.bl_rna.properties['operation'].enum_items if e.identifier=='GREATER_THAN');cut.inputs[1].default_value=.5
 m.node_tree.links.new(t.outputs['Alpha'],cut.inputs[0]);m.node_tree.links.new(cut.outputs[0],b.inputs['Alpha']);m.node_tree.links.new(b.outputs[0],out.inputs['Surface'])
 return m
def crop(m):
 im=next(n for n in m.node_tree.nodes if n.type=='TEX_IMAGE').image;w,h=im.size;p=list(im.pixels);xy=[(i%w,i//w) for i in range(w*h) if p[4*i+3]>.5]
 return (min(x for x,y in xy)/w,min(y for x,y in xy)/h,(max(x for x,y in xy)+1)/w,(max(y for x,y in xy)+1)/h)
def quad(name,center,w,h,v,m,uvbox=None):
 c=Vector(center);pts=[c-right*w/2,c+right*w/2,c+right*w/2+v*h,c-right*w/2+v*h]
 me=bpy.data.meshes.new(name);me.from_pydata(pts,[],[(0,1,2,3)]);me.materials.append(m);uv=me.uv_layers.new();a,b,c,d=uvbox or (0,0,1,1)
 for li,co in zip(me.polygons[0].loop_indices,[(a,b),(c,b),(c,d),(a,d)]):uv.data[li].uv=co
 ob=bpy.data.objects.new(name,me);scene.collection.objects.link(ob);return ob
grass=mat('M_Prop_Grass',ROOT/'T_Grass.png');rock=mat('M_Prop_Rock',ROOT/'T_Rock.png');lamp=mat('M_Prop_Lantern',ROOT/'T_Lantern.png')
groups=[]
groups.append(('Grass',[quad('Grass_Back',(0,.12,.08),.58,.64,up,grass,crop(grass)),quad('Grass_Front',(.06,-.12,.02),.48,.48,up,grass,crop(grass))]))
groups.append(('Rock',[quad('Rock',(0,0,0),1.05,.48,up,rock,crop(rock))]))
groups.append(('Lantern',[quad('Lantern',(0,0,0),.85,2.8,up,lamp,crop(lamp))]))
bushparts=[]
for i,(z,r) in enumerate([(.20,.65),(.40,.56),(.60,.42)]):
 m=bpy.data.materials['M_StackedLeaf_'+str(i+1)]
 bushparts.append(quad('Bush_Tier_'+str(i),(0,-math.cos(math.radians(20))*r,z-math.sin(math.radians(20))*r),r*2,r*2,leaf,m))
groups.append(('Bush',bushparts))
manifest=[]
for i,(name,parts) in enumerate(groups):
 bpy.ops.object.select_all(action='DESELECT')
 for o in parts:o.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];asset='SM_Prop_'+name;file=ROOT/'FBX'/(asset+'.fbx')
 bpy.ops.export_scene.fbx(filepath=str(file),use_selection=True,object_types={'MESH'},apply_unit_scale=True,axis_forward='-Y',axis_up='Z',bake_anim=False,path_mode='COPY')
 group=bpy.data.objects.new(name,None);scene.collection.objects.link(group)
 for o in parts:o.parent=group
 group.location.x=i*2
 manifest.append({'name':asset,'file':str(file),'triangles':len(parts)*2})
(ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2))
camdata=bpy.data.cameras.new('PropsCamera');camdata.type='ORTHO';camdata.ortho_scale=9
cam=bpy.data.objects.new('PropsCamera',camdata);scene.collection.objects.link(cam);target=Vector((3,0,1.2));cam.location=target+Vector((0,-.788,.616))*15;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();scene.camera=cam
scene.world=bpy.data.worlds.get('LayeredStudio');scene.render.resolution_x=1400;scene.render.resolution_y=650;scene.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'AdventureRPG_PixelProps.blend'))
print(json.dumps(manifest))
