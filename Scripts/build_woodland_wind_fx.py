"""Native Blender flat leaf bursts and thin curved wind ribbons."""
import bpy,math,json,random
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'E:\UE5 Projects\AdventureRPG\ContentSource\WoodlandWindFX');(ROOT/'FBX').mkdir(parents=True,exist_ok=True)
scene=bpy.data.scenes.get('WoodlandWindFX_Studio') or bpy.data.scenes.new('WoodlandWindFX_Studio');bpy.context.window.scene=scene
for ob in list(scene.objects):bpy.data.objects.remove(ob,do_unlink=True)
mat=bpy.data.materials['M_LayeredFlowerPixels'];up=Vector((0,math.sin(math.radians(34)),math.cos(math.radians(34))));right=Vector((1,0,0))
verts=[];faces=[];uvs=[]
outline=[(-3,0),(-2,-1),(-1,-1),(-1,-2),(1,-2),(1,-1),(2,-1),(3,0),(2,1),(1,1),(1,2),(-1,2),(-1,1),(-2,1)]
for leaf in range(8):
 phase=(leaf+.35)/8;angle=leaf*2.4;u=right*math.cos(angle)+up*math.sin(angle);v=up*math.cos(angle)-right*math.sin(angle);size=.022+(leaf%3)*.003
 origin=right*math.sin(leaf*2)*.06+up*math.cos(leaf*2)*.04;start=len(verts)
 for x,y in outline:verts.append(tuple(origin+u*x*size+v*y*size))
 mid=len(verts);verts.append(tuple(origin))
 for j in range(len(outline)):faces.append((mid,start+j,start+(j+1)%len(outline)));uvs.append([(phase,0)]*3)
def mesh(name,verts,faces,uvs):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.materials.append(mat);uv=me.uv_layers.new()
 for face,coords in zip(me.polygons,uvs):
  for li,co in zip(face.loop_indices,coords):uv.data[li].uv=co
 ob=bpy.data.objects.new(name,me);scene.collection.objects.link(ob);return ob
burst=mesh('SM_RunLeafBurst',verts,faces,uvs)
verts=[];faces=[];uvs=[]
for ribbon,(x,y,z) in enumerate([(-8,-3,1.4),(-2,1,1.8),(4,3,2.0),(10,-2,1.6),(16,2,1.9),(22,-1,1.7)]):
 points=[]
 for i in range(193):
  t=i/192;bulge=math.sin(math.pi*t)**6
  points.append(Vector((x-4+8*t+.55*math.sin(t*math.tau*2)*bulge,y+.18*math.sin(t*math.tau)+.55*math.cos(t*math.tau*2)*bulge,z+.08*math.sin(t*math.tau))))
 for i in range(192):
  p,q=points[i],points[i+1];t=(i+.5)/192;width=.025*math.sin(math.pi*t)**.45
  start=len(verts);verts.extend([tuple(p-up*width),tuple(q-up*width),tuple(q+up*width),tuple(p+up*width)]);faces.append((start,start+1,start+2,start+3));uvs.append([(0,i/192),(0,(i+1)/192),(0,(i+1)/192),(0,i/192)])
streaks=mesh('SM_FluidWindRibbonLocal',verts,faces,uvs)
manifest=[]
for ob in [burst,streaks]:
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;file=ROOT/'FBX'/(ob.name+'.fbx')
 bpy.ops.export_scene.fbx(filepath=str(file),use_selection=True,object_types={'MESH'},apply_unit_scale=True,axis_forward='-Y',axis_up='Z',bake_anim=False,path_mode='COPY');manifest.append({'name':ob.name,'file':str(file)})
(ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'AdventureRPG_WoodlandWindFX.blend'));print(json.dumps(manifest))
