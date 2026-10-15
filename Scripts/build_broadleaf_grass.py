"""Three flat sprite layers with enough footprint to merge adjacent tall-grass tiles."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'E:\UE5 Projects\AdventureRPG\ContentSource\BroadleafGrass')
scene=bpy.data.scenes.get('BroadleafGrass_Studio') or bpy.data.scenes.new('BroadleafGrass_Studio');bpy.context.window.scene=scene
for o in list(scene.objects):bpy.data.objects.remove(o,do_unlink=True)
image=bpy.data.images.load(str(ROOT/'T_BroadleafGrass.png'),check_existing=True);w,h=image.size;p=list(image.pixels);xy=[(i%w,i//w) for i in range(w*h) if p[i*4+3]>.5]
box=(min(x for x,y in xy)/w,min(y for x,y in xy)/h,(max(x for x,y in xy)+1)/w,(max(y for x,y in xy)+1)/h)
mat=bpy.data.materials.get('M_BroadleafGrass') or bpy.data.materials.new('M_BroadleafGrass');mat.use_nodes=True
n=mat.node_tree.nodes;n.clear();out=n.new('ShaderNodeOutputMaterial');b=n.new('ShaderNodeBsdfPrincipled');tex=n.new('ShaderNodeTexImage');tex.image=image;tex.interpolation='Closest'
mat.node_tree.links.new(tex.outputs['Color'],b.inputs['Base Color']);mat.node_tree.links.new(tex.outputs['Color'],b.inputs['Emission Color']);b.inputs['Emission Strength'].default_value=1
def linear(c):
 c=c/255;return c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4
sep=n.new('ShaderNodeSeparateColor');gain=n.new('ShaderNodeMath');gain.operation=next(e.identifier for e in gain.bl_rna.properties['operation'].enum_items if e.identifier=='MULTIPLY');gain.inputs[1].default_value=1.9;ramp=n.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].color=tuple(linear(c) for c in (9,58,40))+(1,);ramp.color_ramp.elements[1].color=tuple(linear(c) for c in (117,172,47))+(1,)
mat.node_tree.links.new(tex.outputs['Color'],sep.inputs['Color']);mat.node_tree.links.new(sep.outputs['Green'],gain.inputs[0]);mat.node_tree.links.new(gain.outputs[0],ramp.inputs[0]);mat.node_tree.links.new(ramp.outputs['Color'],b.inputs['Base Color']);mat.node_tree.links.new(ramp.outputs['Color'],b.inputs['Emission Color'])
cut=n.new('ShaderNodeMath');cut.operation=next(e.identifier for e in cut.bl_rna.properties['operation'].enum_items if e.identifier=='GREATER_THAN');cut.inputs[1].default_value=.5
mat.node_tree.links.new(tex.outputs['Alpha'],cut.inputs[0]);mat.node_tree.links.new(cut.outputs[0],b.inputs['Alpha']);mat.node_tree.links.new(b.outputs[0],out.inputs['Surface'])
parts=[];right=Vector((1,0,0));up=Vector((0,.8,.6));a,b,c,d=box
for i,(y,z,width,height) in enumerate([(.17,.25,.76,.47),(0,.12,.84,.50),(-.19,.02,.88,.46)]):
 base=Vector((0,y,z));pts=[base-right*width/2,base+right*width/2,base+right*width/2+up*height,base-right*width/2+up*height]
 me=bpy.data.meshes.new('GrassLayer_'+str(i));me.from_pydata(pts,[],[(0,1,2,3)]);me.materials.append(mat);uv=me.uv_layers.new()
 for li,co in zip(me.polygons[0].loop_indices,[(a,b),(c,b),(c,d),(a,d)]):uv.data[li].uv=co
 ob=bpy.data.objects.new('GrassLayer_'+str(i),me);scene.collection.objects.link(ob);parts.append(ob)
bpy.ops.object.select_all(action='DESELECT')
for ob in parts:ob.select_set(True)
bpy.context.view_layer.objects.active=parts[0]
file=ROOT/'FBX/SM_BroadleafGrass.fbx';bpy.ops.export_scene.fbx(filepath=str(file),use_selection=True,object_types={'MESH'},apply_unit_scale=True,axis_forward='-Y',axis_up='Z',bake_anim=False,path_mode='COPY')
# A repeated patch preview uses linked copies of the editable layers.
for row in range(3):
 for col in range(5):
  if row==col==0:continue
  for ob in parts:
   copy=ob.copy();copy.data=ob.data;scene.collection.objects.link(copy);copy.location=Vector((col*1.28,row*1.20,0));copy.scale=(1.6,1.6,1.6)
for ob in parts:ob.scale=(1.6,1.6,1.6)
camdata=bpy.data.cameras.new('GrassPreview');camdata.type='ORTHO';camdata.ortho_scale=7.2
cam=bpy.data.objects.new('GrassPreview',camdata);scene.collection.objects.link(cam);target=Vector((2.56,1.2,.3));cam.location=target+Vector((0,-math.cos(math.radians(34)),math.sin(math.radians(34))))*10;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();scene.camera=cam
scene.world=bpy.data.worlds.get('LayeredStudio');scene.render.resolution_x=1400;scene.render.resolution_y=850;scene.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'AdventureRPG_BroadleafGrass.blend'))
print(json.dumps({'file':str(file),'flat_planes':3,'triangles':6,'width_m':.88,'height_m':.532}))
