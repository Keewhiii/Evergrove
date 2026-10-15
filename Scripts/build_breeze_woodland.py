"""Blender source: reference-shaped layered trees, pixel daisies and flat falling leaves."""
import bpy,math,json,random
from pathlib import Path
from mathutils import Vector
PROJECT=Path(r'E:\UE5 Projects\AdventureRPG');ROOT=PROJECT/'ContentSource/BreezeWoodland';(ROOT/'FBX').mkdir(parents=True,exist_ok=True)
# Reuse the existing editable tree construction helpers and sprite materials.
prefix=(PROJECT/'Scripts/build_stacked_leaf_trees.py').read_text().split('manifest=[]')[0]
prefix=prefix.replace("'StackedLeaf_Studio'","'BreezeWoodland_Studio'")
exec(compile(prefix,'tree_helpers','exec'))
ROOT=PROJECT/'ContentSource/BreezeWoodland';scene=bpy.context.scene
manifest=[]
def export(name,parts):
 bpy.ops.object.select_all(action='DESELECT')
 for o in parts:o.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];file=ROOT/'FBX'/(name+'.fbx')
 bpy.ops.export_scene.fbx(filepath=str(file),use_selection=True,object_types={'MESH'},apply_unit_scale=True,axis_forward='-Y',axis_up='Z',bake_anim=False,path_mode='COPY')
 manifest.append({'name':name,'file':str(file),'triangles':sum(len(o.data.polygons)*2 for o in parts)})
 group=bpy.data.objects.new(name,None);scene.collection.objects.link(group)
 for o in parts:o.parent=group
 return group
for variant in range(3):
 letter=chr(65+variant);x0,y0,x1,y1=uvbox
 parts=[quad(letter+'_Trunk',[-right*.73,right*.73,right*.73+up*1.18,-right*.73+up*1.18],[(x0,y0),(x1,y0),(x1,y1),(x0,y1)],trunk_mat)]
 tiers=[(1.97,1.64),(2.43,1.56),(2.91,1.34),(3.39,1.10),(3.86,.83)]
 for i,(height,radius) in enumerate(tiers):
  origin=Vector((0,0,height));parts.append(quad(letter+'_LeafTier_'+str(i),[origin-right*radius-leaf_v*radius,origin+right*radius-leaf_v*radius,origin+right*radius+leaf_v*radius,origin-right*radius+leaf_v*radius],[(0,0),(1,0),(1,1),(0,1)],materials[i]))
 if variant==1:
  for j,(x,t,tier,color) in enumerate([(-.9,-.9,1,21),(.86,-.8,1,23),(-.6,-.76,2,15),(.55,-.75,2,21)]):
   center=Vector((x,0,tiers[tier][0]))+leaf_v*t+eye*.04;s=.12
   for k,(dx,dy,c) in enumerate([(-1,0,color),(1,0,color),(0,1,color),(0,-1,color),(0,0,16)]):
    p=center+right*dx*s+up*dy*s;uv=((c%8+.5)/8,(c//8+.5)/8)
    parts.append(quad(letter+'_Petal_'+str(j)+'_'+str(k),[p-right*s/2-up*s/2,p+right*s/2-up*s/2,p+right*s/2+up*s/2,p-right*s/2+up*s/2],[uv]*4,palette_mat))
 export('SM_BreezeTree_'+letter,parts).location.x=variant*4.5
# Native flat pixel tiles: short stems and three five-petal daisies, no solid petals.
for yellow in [False,True]:
 parts=[]
 for j,(x,y,z) in enumerate([(-.26,0,.18),(.03,.10,.33),(.30,-.02,.14)]):
  center=Vector((x,y,z));s=.035
  cells={}
  for k in range(5):
   a=math.tau*k/5+math.pi/2;cx,cy=round(math.cos(a)*3),round(math.sin(a)*3)
   for dx in range(-1,2):
    for dy in range(-1,2):cells[(cx+dx,cy+dy)]=16 if yellow else 15
  for dx,dy in [(-1,0),(0,0),(1,0),(0,1),(0,-1)]:cells[(dx,dy)]=14 if yellow else 16
  for (ix,iy),color in cells.items():
   p=center+right*ix*s+up*iy*s;uv=((color%8+.5)/8,(color//8+.5)/8)
   parts.append(quad('DaisyPixel', [p-right*s/2-up*s/2,p+right*s/2-up*s/2,p+right*s/2+up*s/2,p-right*s/2+up*s/2],[uv]*4,palette_mat))
  uv=((2+.5)/8,(0+.5)/8);base=Vector((x,y,0))
  parts.append(quad('Stem',[base-right*.015,base+right*.015,center+right*.015,center-right*.015],[uv]*4,palette_mat))
 export('SM_BreezeFlowers_'+('Yellow' if yellow else 'White'),parts).location=Vector((yellow*1.3,-3,0))
# A lightweight field of flat stepped leaves. UV.x stores an independent fall phase.
rng=random.Random(101);verts=[];faces=[];uvs=[];colors=[]
outline=[(-3,-1),(-2,-2),(0,-2),(0,-1),(2,-1),(3,0),(2,1),(0,1),(0,2),(-2,2),(-2,1),(-3,1)]
for i in range(220):
 center=Vector((rng.uniform(-10,43),rng.uniform(-11,11),rng.uniform(4.5,5.5)));size=rng.uniform(.027,.042);phase=rng.random();a=rng.uniform(-.7,.7)
 u=right*math.cos(a)+up*math.sin(a);v=up*math.cos(a)-right*math.sin(a);start=len(verts)
 for x,y in outline:verts.append(tuple(center+u*x*size+v*y*size))
 # Triangulate via a center fan so concave outlines remain clean.
 mid=len(verts);verts.append(tuple(center))
 for j in range(len(outline)):faces.append((mid,start+j,start+(j+1)%len(outline)));uvs.append((phase,0));colors.append((.18+rng.random()*.12,.40+rng.random()*.15,.06,1))
me=bpy.data.meshes.new('FallingLeafField');me.from_pydata(verts,[],faces);uv=me.uv_layers.new();col=me.color_attributes.new(name='LeafColor',type='FLOAT_COLOR',domain='CORNER')
for f,phase,color in zip(me.polygons,uvs,colors):
 for li in f.loop_indices:uv.data[li].uv=phase;col.data[li].color=color
ob=bpy.data.objects.new('FallingLeafField',me);scene.collection.objects.link(ob);me.materials.append(palette_mat)
export('SM_DirectionalLeafField',[ob]);manifest[-1]['triangles']=len(faces);ob['larger_directional_leaves']=True;ob.hide_render=True;ob.hide_set(True)
(ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2))
camdata=bpy.data.cameras.new('BreezePreview');camdata.type='ORTHO';camdata.ortho_scale=13
cam=bpy.data.objects.new('BreezePreview',camdata);scene.collection.objects.link(cam);target=Vector((4.5,0,2));cam.location=target+eye*15;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();scene.camera=cam
scene.world=bpy.data.worlds.get('LayeredStudio');scene.render.resolution_x=1500;scene.render.resolution_y=800;scene.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'AdventureRPG_BreezeWoodland.blend'))
print(json.dumps(manifest))
