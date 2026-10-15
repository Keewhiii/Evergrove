"""Flat leaf artwork in true 3D positions, with per-leaf pivot and flight data for tumbling."""
import bpy,math,json,random
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'E:\UE5 Projects\AdventureRPG\ContentSource\WoodlandWindFX');scene=bpy.data.scenes.get('SpatialLeaves_Studio') or bpy.data.scenes.new('SpatialLeaves_Studio');bpy.context.window.scene=scene
for ob in list(scene.objects):bpy.data.objects.remove(ob,do_unlink=True)
outline=[(-3,0),(-2,-1),(-1,-1),(-1,-2),(1,-2),(1,-1),(2,-1),(3,0),(2,1),(1,1),(1,2),(-1,2),(-1,1),(-2,1)]
right=Vector((1,0,0));up=Vector((0,math.sin(math.radians(34)),math.cos(math.radians(34))));manifest=[]
for burst in [False,True]:
 rng=random.Random(424 if burst else 731);verts=[];faces=[];data=[]
 for leaf in range(8 if burst else 220):
  if burst:center=Vector((rng.uniform(-.07,.07),rng.uniform(-.07,.07),0));size=rng.uniform(.022,.029)
  else:
   center=Vector((rng.uniform(-11,47),rng.uniform(-11,11),rng.uniform(.9,5.8)))
   size=(.020+.025*(11-center.y)/22)*rng.uniform(.85,1.15)
  phase=rng.random();seed=rng.random();angle=rng.uniform(-math.pi,math.pi);u=right*math.cos(angle)+up*math.sin(angle);v=up*math.cos(angle)-right*math.sin(angle)
  offsets=[u*x*size+v*y*size for x,y in outline]+[Vector((0,0,0))];start=len(verts)
  for delta in offsets:verts.append(tuple(center+delta));data.append(((phase,center.z*100),(delta.x*100,-delta.y*100),(delta.z*100,seed)))
  mid=start+len(outline)
  for j in range(len(outline)):faces.append((mid,start+j,start+(j+1)%len(outline)))
 name='SM_SpatialRunLeafBurst' if burst else 'SM_SpatialWindLeaves';me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.materials.append(bpy.data.materials['M_LayeredFlowerPixels']);uvs=[me.uv_layers.new(name='Flight'),me.uv_layers.new(name='PivotXY'),me.uv_layers.new(name='PivotZSeed')]
 for face in me.polygons:
  for li in face.loop_indices:
   vi=me.loops[li].vertex_index
   for channel in range(3):uvs[channel].data[li].uv=data[vi][channel]
 ob=bpy.data.objects.new(name,me);scene.collection.objects.link(ob);bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;file=ROOT/'FBX'/(name+'.fbx')
 bpy.ops.export_scene.fbx(filepath=str(file),use_selection=True,object_types={'MESH'},apply_unit_scale=True,axis_forward='-Y',axis_up='Z',bake_anim=False,path_mode='COPY');manifest.append({'name':name,'file':str(file),'leaves':8 if burst else 220,'uv_channels':3,'triangles':len(faces)})
(ROOT/'spatial_leaves_manifest.json').write_text(json.dumps(manifest,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'AdventureRPG_SpatialLeaves.blend'));print(json.dumps(manifest))
