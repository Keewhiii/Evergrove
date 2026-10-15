"""Blender mesh trees with original pixel-art foliage cards for the fixed RPG camera."""
import bpy, math, random, json
from pathlib import Path
ROOT=Path(r'E:\UE5 Projects\AdventureRPG\ContentSource\PixelWoodland')
scene=bpy.data.scenes.get('PixelLeaf_Studio') or bpy.data.scenes.new('PixelLeaf_Studio');bpy.context.window.scene=scene
for obj in list(scene.objects):
    if obj.get('pixel_card'):bpy.data.objects.remove(obj,do_unlink=True)
colors=[(13,58,39),(21,77,42),(31,99,44),(47,119,43),(70,141,40),(100,160,43),(134,179,51)]
materials=[]
for variant in range(2):
    W,H=96,128;canvas={};rng=random.Random(925)
    def ellipse(cx,cy,rx,ry,c):
        for y in range(max(0,int(cy-ry)),min(H,int(cy+ry+1))):
            for x in range(max(0,int(cx-rx)),min(W,int(cx+rx+1))):
                if ((x-cx)/rx)**2+((y-cy)/ry)**2<=1:canvas[x,y]=c
    # Overlapping clusters have drooping, scalloped tips rather than circular rings.
    clusters=[]
    for row,(cy,width,shade) in enumerate([(22,34,1),(43,35,2),(66,32,3),(88,25,3),(107,12,4)]):
        count=4 if row<3 else 3 if row==3 else 2
        for i in range(count):
            cx=48-width+2*width*(i+.5)/count;yy=cy+rng.randint(-4,4);rx=18 if row<3 else 19 if row==3 else 18;ry=23 if row<4 else 20
            clusters.append((cx,yy,rx,ry,shade))
            ellipse(cx,yy,rx,ry,colors[max(0,shade-1)])
            ellipse(cx,yy+3,rx-2,ry-3,colors[shade])
            # Individually drawn large leaves, with a highlight curving around one edge.
            for leaf in range(15):
                a=rng.random()*math.tau;rr=rng.random()**.5
                lx=cx+math.cos(a)*rr*(rx-3);ly=yy+math.sin(a)*rr*(ry-5)
                lr=rng.randint(3,6);lh=rng.randint(5,9);s=max(0,min(5,shade+rng.choice([-1,0,0,1])))
                ellipse(lx,ly,lr,lh,colors[max(0,s-1)])
                ellipse(lx,ly+1,lr-1,lh-2,colors[s])
                for k in range(10):
                    ang=.15+k*.18;px=int(lx+math.cos(ang)*(lr-1));py=int(ly+math.sin(ang)*(lh-2))
                    if (px,py) in canvas:canvas[px,py]=colors[min(6,s+1)]
    if variant:
        for j,(x,y) in enumerate([(20,23),(24,45),(70,33),(60,15),(16,66),(73,64),(33,87)]):
            petal=(240,228,158) if j%3==0 else (204,80,157) if j%3==1 else (60,118,183)
            for dx,dy in [(-3,0),(3,0),(0,3),(0,-3)]:ellipse(x+dx,y+dy,2,3,petal)
            ellipse(x,y,2,2,(237,194,31))
    pixels=[]
    for y in range(H):
        for x in range(W):
            c=canvas.get((x,y));pixels.extend([k/255 for k in c]+[1] if c else [0,0,0,0])
    name='T_PixelLeaf_Flower' if variant else 'T_PixelLeaf_Crown'
    painted=ROOT/('T_ScallopedFlower.png' if variant else 'T_ScallopedCrown.png')
    if painted.exists():
        im=bpy.data.images.load(str(painted),check_existing=True)
    else:
        im=bpy.data.images.get(name) or bpy.data.images.new(name,W,H,alpha=True);im.pixels.foreach_set(pixels);im.filepath_raw=str(ROOT/(name+'.png'));im.file_format='PNG';im.save()
    name='M_PixelLeaf_Flower' if variant else 'M_PixelLeaf_Crown'
    mat=bpy.data.materials.get(name) or bpy.data.materials.new(name);mat.use_nodes=True
    b=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');t=next((n for n in mat.node_tree.nodes if n.type=='TEX_IMAGE'),None) or mat.node_tree.nodes.new('ShaderNodeTexImage');t.image=im;t.interpolation='Closest'
    mat.node_tree.links.new(t.outputs['Color'],b.inputs['Base Color']);mat.node_tree.links.new(t.outputs['Alpha'],b.inputs['Alpha']);b.inputs['Roughness'].default_value=1
    materials.append(mat)
palette=bpy.data.materials['M_PixelWoodland']
manifest=[]
for variant in range(3):
    verts=[];faces=[];uvs=[];slots=[]
    def face(points,uv,slot):
        n=len(verts);verts.extend(points);faces.append(tuple(range(n,n+len(points))));uvs.append(uv);slots.append(slot)
    def color_uv(c,n):return [((c%8+.5)/8,(c//8+.5)/8)]*n
    for z0,z1,r0,r1 in [(0,.28,.57,.40),(.28,1.8,.40,.31)]:
        for j in range(10):
            a,b=j*math.tau/10,(j+1)*math.tau/10;c=[11,12,13,12,11,20,11,12,13,12][j]
            face([(math.cos(a)*r0,math.sin(a)*r0,z0),(math.cos(b)*r0,math.sin(b)*r0,z0),(math.cos(b)*r1,math.sin(b)*r1,z1),(math.cos(a)*r1,math.sin(a)*r1,z1)],color_uv(c,4),0)
    # The card normal faces the fixed gameplay camera. The angled plane gives real
    # ground depth while preserving the painted scalloped silhouette.
    width=3.3*(1+variant*.035);height=3.7
    # FBX conversion flips Blender Y for Unreal; lean away from the UE camera.
    def p(x,t):return (x,t*height*.55,1.18+t*height*.835)
    face([p(-width/2,0),p(width/2,0),p(width/2,1),p(-width/2,1)],[(0,0),(1,0),(1,1),(0,1)],1)
    mesh=bpy.data.meshes.new('PixelCardTree');mesh.from_pydata(verts,[],faces);mesh.update();uv=mesh.uv_layers.new()
    for poly,coords,slot in zip(mesh.polygons,uvs,slots):
        poly.material_index=slot
        for li,coord in zip(poly.loop_indices,coords):uv.data[li].uv=coord
    name='SM_Pixel_CardTree_'+chr(65+variant);obj=bpy.data.objects.new(name,mesh);scene.collection.objects.link(obj);obj['pixel_card']=True;mesh.materials.append(palette);mesh.materials.append(materials[variant==1])
    bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
    file=ROOT/'FBX'/(name+'.fbx');bpy.ops.export_scene.fbx(filepath=str(file),use_selection=True,object_types={'MESH'},apply_unit_scale=True,axis_forward='-Y',axis_up='Z',bake_anim=False,path_mode='COPY')
    manifest.append({'name':name,'file':str(file)});obj.location.x=variant*4.5
# Matching low shrub and simple, flat-color dirt trail.
me=bpy.data.meshes.new('PixelShrubCard');me.from_pydata([(-.75,0,.03),(.75,0,.03),(.75,.65,.95),(-.75,.65,.95)],[],[(0,1,2,3)]);me.update();uv=me.uv_layers.new()
for li,co in zip(me.polygons[0].loop_indices,[(0,0),(1,0),(1,1),(0,1)]):uv.data[li].uv=co
shrub=bpy.data.objects.new('SM_Pixel_CardBush',me);scene.collection.objects.link(shrub);me.materials.append(materials[0])
me=bpy.data.objects['SM_Woodland_TrailSkin'].data.copy();me.materials.clear();me.materials.append(palette)
for poly in me.polygons:
    poly.material_index=0
    for li in poly.loop_indices:me.uv_layers.active.data[li].uv=((13%8+.5)/8,(13//8+.5)/8)
trail=bpy.data.objects.new('SM_Pixel_Trail',me);scene.collection.objects.link(trail)
for ob in [shrub,trail]:
    ob['pixel_card']=True;bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
    file=ROOT/'FBX'/(ob.name+'.fbx');bpy.ops.export_scene.fbx(filepath=str(file),use_selection=True,object_types={'MESH'},apply_unit_scale=True,axis_forward='-Y',axis_up='Z',bake_anim=False,path_mode='COPY')
    manifest.append({'name':ob.name,'file':str(file)});ob.hide_set(True)
(ROOT/'card_manifest.json').write_text(json.dumps(manifest,indent=2))
scene.world=bpy.data.worlds.get('PixelWoodland_Studio')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'AdventureRPG_PixelWoodland.blend'))
print('Pixel leaf mesh trees exported: '+json.dumps(manifest))
