"""Blender authoring: stepped pixel foliage based on the user's woodland reference."""
import bpy, bmesh, math, random, json
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'E:\UE5 Projects\AdventureRPG\ContentSource\PixelWoodland')
(ROOT/'FBX').mkdir(parents=True,exist_ok=True)
scene=bpy.data.scenes.get('PixelWoodland_Studio') or bpy.data.scenes.new('PixelWoodland_Studio')
bpy.context.window.scene=scene
for obj in list(scene.objects):
    if obj.get('pixel_woodland'):bpy.data.objects.remove(obj,do_unlink=True)
scene.unit_settings.system='METRIC'
colors=[(17,65,42),(29,92,46),(47,125,49),(77,151,48),(117,172,47),
        (43,81,40),(74,108,43),(97,133,45),(58,108,43),(69,121,44),
        (83,130,47),(94,70,42),(123,93,53),(153,121,68),(236,219,147),
        (247,238,198),(224,185,37),(151,108,62),(86,104,81),(115,130,93),
        (86,59,35),(204,88,157),(107,69,154),(74,124,187)]
image=bpy.data.images.get('T_PixelWoodland_Palette') or bpy.data.images.new('T_PixelWoodland_Palette',32,32)
pixels=[]
for y in range(32):
    for x in range(32):
        color=colors[min((y//4)*8+x//4,len(colors)-1)]
        pixels.extend([c/255 for c in color]+[1])
image.pixels.foreach_set(pixels);image.filepath_raw=str(ROOT/'T_PixelWoodland_Palette.png');image.file_format='PNG';image.save()
material=bpy.data.materials.get('M_PixelWoodland') or bpy.data.materials.new('M_PixelWoodland');material.use_nodes=True
bsdf=next(n for n in material.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
tex=next((n for n in material.node_tree.nodes if n.type=='TEX_IMAGE'),None) or material.node_tree.nodes.new('ShaderNodeTexImage')
tex.image=image;tex.interpolation='Closest';material.node_tree.links.new(tex.outputs['Color'],bsdf.inputs['Base Color']);bsdf.inputs['Roughness'].default_value=1

class Mesh:
    def __init__(self):self.vertices=[];self.faces=[];self.colors=[]
    def face(self,points,color):
        n=len(self.vertices);self.vertices.extend(points);self.faces.append(tuple(range(n,n+len(points))));self.colors.append(color)
    def cylinder(self,z0,z1,r0,r1,n=10):
        for i in range(n):
            a,b=i*math.tau/n,(i+1)*math.tau/n
            # Broad vertical bark bands, without fine noisy bark textures.
            color=[11,12,12,13,12,11,20,11,12,13][i%10]
            self.face([(math.cos(a)*r0,math.sin(a)*r0,z0),(math.cos(b)*r0,math.sin(b)*r0,z0),(math.cos(b)*r1,math.sin(b)*r1,z1),(math.cos(a)*r1,math.sin(a)*r1,z1)],color)
        self.face([(math.cos(i*math.tau/n)*r1,math.sin(i*math.tau/n)*r1,z1) for i in range(n)],13)
    def disc(self,z,radius,seed,tier=0):
        rng=random.Random(seed);N=36;cells={};centers=[]
        for j in range(10):
            a=j*math.tau/10;centers.append((18+12*math.cos(a),18+12*math.sin(a),rng.uniform(4.5,6)))
        for x in range(N):
            for y in range(N):
                if (x-18)**2+(y-18)**2<13**2 or any((x-cx)**2+(y-cy)**2<rr**2 for cx,cy,rr in centers):cells[x,y]=1 if tier<2 else 2
        # Large, legible individual leaf clumps, with pixel-stepped highlight arcs.
        for j in range(29):
            cx,cy=rng.randrange(4,32),rng.randrange(4,32);rx,ry=rng.randrange(3,6),rng.randrange(3,6)
            shade=2+(j%3==0)+(tier>2 and j%4==0)
            for x in range(cx-rx,cx+rx+1):
                for y in range(cy-ry,cy+ry+1):
                    if (x,y) in cells and ((x-cx)/rx)**2+((y-cy)/ry)**2<1:
                        cells[x,y]=shade if y>cy-ry+1 else max(0,shade-1)
                        d=((x-cx)/rx)**2+((y-cy)/ry)**2
                        if .55<d<.95 and y>cy and x<cx+2:cells[x,y]=min(4,shade+1)
        step=radius/18
        for (x,y),color in cells.items():
            x0=(x-18)*step;y0=(y-18)*step
            # Shallow stepped dome gives each tier volume, with a dark underside.
            radial=math.hypot(x-18,y-18)/18
            zz=z+max(0,3-int(radial*4))*.055;depth=.45 if radius>.8 else .26
            self.face([(x0,y0,zz),(x0+step,y0,zz),(x0+step,y0+step,zz),(x0,y0+step,zz)],color)
            self.face([(x0,y0+step,zz-depth),(x0+step,y0+step,zz-depth),(x0+step,y0,zz-depth),(x0,y0,zz-depth)],0)
            for dx,dy,points in [(-1,0,[(x0,y0,zz-depth),(x0,y0,zz),(x0,y0+step,zz),(x0,y0+step,zz-depth)]),(1,0,[(x0+step,y0+step,zz-depth),(x0+step,y0+step,zz),(x0+step,y0,zz),(x0+step,y0,zz-depth)]),(0,-1,[(x0+step,y0,zz-depth),(x0+step,y0,zz),(x0,y0,zz),(x0,y0,zz-depth)]),(0,1,[(x0,y0+step,zz-depth),(x0,y0+step,zz),(x0+step,y0+step,zz),(x0+step,y0+step,zz-depth)])]:
                if (x+dx,y+dy) not in cells:self.face(points,max(0,color-1))
    def flower(self,x,y,z,scale=1,petal=15):
        s=.045*scale
        for ix,iy,c in [(-1,0,petal),(1,0,petal),(0,-1,petal),(0,1,petal),(0,0,16)]:
            xx=x+ix*s;yy=y+iy*s
            self.face([(xx-s*.5,yy-s*.5,z),(xx+s*.5,yy-s*.5,z),(xx+s*.5,yy+s*.5,z),(xx-s*.5,yy+s*.5,z)],c)
    def blade(self,angle,length=.82,offset=(0,0),seed=0):
        rng=random.Random(seed);u=Vector((math.cos(angle),math.sin(angle)*.35,0));v=Vector((1,0,0))
        origin=Vector((offset[0],offset[1],.02));N=14
        for row in range(N):
            t=row/N;tn=(row+1)/N
            half=(3 if row<9 else 2 if row<11 else 1 if row<13 else 0)
            for col in range(-half,half+1):
                width=.045;side=col*width
                def pos(tt,ss):return tuple(origin+u*(tt*tt*.38)+v*ss+Vector((0,0,tt*length)))
                color=5 if col<0 else 6 if col==0 else 7
                if (row//2+col)%4==0:color=min(7,color+1)
                if row>10:color=7 if col>=0 else 6
                self.face([pos(t,side),pos(t,side+width),pos(tn,side+width),pos(tn,side)],color)
    def finish(self,name):
        mesh=bpy.data.meshes.new(name);mesh.from_pydata(self.vertices,[],self.faces);mesh.update();uv=mesh.uv_layers.new()
        for p,c in zip(mesh.polygons,self.colors):
            for li in p.loop_indices:uv.data[li].uv=((c%8+.5)/8,(c//8+.5)/8)
        bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001);bm.to_mesh(mesh);bm.free();mesh.update()
        obj=bpy.data.objects.new(name,mesh);scene.collection.objects.link(obj);obj.data.materials.append(material);obj['pixel_woodland']=True
        return obj

assets=[]
for variant in range(3):
    m=Mesh();m.cylinder(0,.3,.58,.43);m.cylinder(.3,1.7,.43,.34)
    for tier,(z,radius) in enumerate([(1.5,1.3),(1.95,1.5),(2.4,1.5),(2.85,1.4),(3.3,1.18),(3.7,.78),(4,.4)]):m.disc(z,radius*(1+variant*.035),31+variant*51+tier,tier)
    if variant==1:
        for j in range(18):
            a=j*2.4;r=.9 if j%2 else 1.3
            m.flower(math.cos(a)*r,math.sin(a)*r,2.18 if j%2 else 1.65,2,15 if j%3==0 else 21 if j%3==1 else 23)
    assets.append(m.finish('SM_Pixel_Tree_'+chr(65+variant)))
m=Mesh()
for i,a in enumerate([0,math.pi/2,math.pi,math.pi*1.5,.65]):m.blade(a,.72+(i%2)*.12,seed=i)
assets.append(m.finish('SM_Pixel_TallGrass'))
m=Mesh();m.disc(.18,.72,222,0);m.disc(.45,.55,225,2);m.disc(.68,.32,227,3)
assets.append(m.finish('SM_Pixel_Bush'))
m=Mesh()
for j in range(8):m.blade(j*math.tau/8,.28,seed=j)
assets.append(m.finish('SM_Pixel_Fern'))
m=Mesh()
for j in range(8):
    rng=random.Random(j*33);x,y=rng.uniform(-.4,.4),rng.uniform(-.3,.3);z=rng.uniform(.08,.15)
    m.flower(x,y,z,2.4,15 if j%3 else 16)
assets.append(m.finish('SM_Pixel_Flowers'))
# Simple grass floor: broad connected patches, sparse small accents.
m=Mesh();rng=random.Random(533)
for ix in range(122):
    for iy in range(68):
        x=-31+ix*.5;y=-17+iy*.5
        value=math.sin(x*.6)+math.sin(y*.9)+.6*math.sin(x*.3+y*.7)
        c=8 if value<-.8 else 9 if value<1.1 else 10
        m.face([(x,y,0),(x+.5,y,0),(x+.5,y+.5,0),(x,y+.5,0)],c)
        if rng.random()<.025:
            s=.055
            m.face([(x+.2,y+.1,.002),(x+.2+s,y+.1,.002),(x+.2+s,y+.1+s,.002),(x+.2,y+.1+s,.002)],7)
assets.append(m.finish('SM_Pixel_Ground'))
manifest=[]
for i,obj in enumerate(assets):
    bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
    bpy.ops.export_scene.fbx(filepath=str(ROOT/'FBX'/(obj.name+'.fbx')),use_selection=True,object_types={'MESH'},apply_unit_scale=True,axis_forward='-Y',axis_up='Z',bake_anim=False,path_mode='COPY')
    manifest.append({'name':obj.name,'file':str(ROOT/'FBX'/(obj.name+'.fbx')),'size_m':list(obj.dimensions),'triangles':sum(len(p.vertices)-2 for p in obj.data.polygons)})
    obj.location=((i%4)*4.5,(i//4)*5,0)
    if 'Ground' in obj.name:obj.hide_set(True)
(ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2))
world=bpy.data.worlds.new('PixelWoodland_Studio');world.use_nodes=True
bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs[0].default_value=(.18,.23,.20,1);bg.inputs[1].default_value=.6;scene.world=world
ld=bpy.data.lights.new('PixelWoodland_Sun','SUN');lo=bpy.data.objects.new('PixelWoodland_Sun',ld);scene.collection.objects.link(lo);lo['pixel_woodland']=True;lo.rotation_euler=(.35,-.3,-.6);ld.energy=2
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':area.spaces.active.shading.type='MATERIAL'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'AdventureRPG_PixelWoodland.blend'))
print('PIXEL_KIT '+json.dumps(manifest))
