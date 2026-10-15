"""Run inside Blender: original pixel-textured woodland kit for AdventureRPG."""
import bpy, bmesh, math, random, json
from pathlib import Path
from mathutils import Vector

ROOT = Path(r'E:\UE5 Projects\AdventureRPG\ContentSource\Woodland')
ROOT.mkdir(parents=True, exist_ok=True)
(ROOT/'FBX').mkdir(exist_ok=True)
R = random.Random(104)
# Separate authoring scene preserves the user's starting scene.
scene = bpy.data.scenes.get('Woodland_AssetStudio')
if scene is None:
    scene = bpy.data.scenes.new('Woodland_AssetStudio')
bpy.context.window.scene = scene
for obj in list(scene.objects):
    if obj.get('woodland_generated'):
        bpy.data.objects.remove(obj, do_unlink=True)
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0

palette = [(12,49,22),(25,85,28),(51,123,29),(101,151,30),
           (83,54,32),(116,77,43),(169,124,67),(72,112,47),
           (68,89,75),(105,119,95),(145,152,114),(148,119,72),
           (60,113,49),(99,141,56),(228,202,122),(204,224,185)]
N=256
pixels=[0.0]*(N*N*4)
for y in range(N):
    for x in range(N):
        tile=(y//64)*4+x//64
        tx,ty=x%64,y%64
        c=palette[tile]
        # Broad two-to-four-pixel marks stay crisp at the game camera distance.
        seed=(tx//3)*9187+(ty//2)*2293+tile*11
        noise=random.Random(seed).random()
        v=0.70+noise*.48
        if tile in (0,1,2,3,7,12,13):
            # Chunky irregular leaf patches, rather than fine diagonal streaks.
            patch=random.Random((tx//8)*9187+(ty//7)*2293+tile*37).random()
            v=(.58+patch*.72)*(.92+noise*.13)
            if tx%8<3 and ty%7>3:v*=.79
        elif tile in (4,5):
            v*=.73 if (tx+int(3*math.sin(ty*.13)))%14<3 else 1.04
        elif tile==6:
            rr=math.hypot(tx-32,ty-32)
            if int(rr/4)%3==0:v*=.78
        elif tile==11:
            patch=random.Random((tx//7)*887+(ty//6)*223).random()
            v=.82+patch*.3
            if noise>.94:v*=1.08
        idx=(y*N+x)*4
        pixels[idx:idx+4]=[min(c[k]*v/255,1) for k in range(3)]+[1]
img=bpy.data.images.get('T_Woodland_PixelAtlas') or bpy.data.images.new('T_Woodland_PixelAtlas',N,N)
img.pixels.foreach_set(pixels)
img.filepath_raw=str(ROOT/'T_Woodland_PixelAtlas.png')
img.file_format='PNG'
img.save()
mat=bpy.data.materials.get('M_Woodland_PixelAtlas') or bpy.data.materials.new('M_Woodland_PixelAtlas')
mat.use_nodes=True
nodes=mat.node_tree.nodes
bsdf=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
tex=next((n for n in nodes if n.type=='TEX_IMAGE'),None) or nodes.new('ShaderNodeTexImage')
tex.image=img;tex.interpolation='Closest'
bsdf.inputs['Roughness'].default_value=.87
mat.node_tree.links.new(tex.outputs['Color'],bsdf.inputs['Base Color'])

class Mesh:
    def __init__(self):self.v=[];self.f=[];self.tiles=[];self.smooth=[]
    def face(self,points,tile,smooth=False):
        base=len(self.v);self.v.extend(points);self.f.append(tuple(range(base,base+len(points))))
        self.tiles.append(tile);self.smooth.append(smooth)
    def tube(self,points,radii,tile=4,n=9):
        pts=[Vector(p) for p in points];rings=[]
        for i,p in enumerate(pts):
            tangent=(pts[min(i+1,len(pts)-1)]-pts[max(0,i-1)]).normalized()
            u=tangent.cross(Vector((0,1,0))).normalized();w=tangent.cross(u).normalized()
            rings.append([tuple(p+radii[i]*(u*math.cos(j*math.tau/n)+w*math.sin(j*math.tau/n))) for j in range(n)])
        for i in range(len(rings)-1):
            for j in range(n):self.face([rings[i][j],rings[i][(j+1)%n],rings[i+1][(j+1)%n],rings[i+1][j]],tile+(j%3==0))
        self.face(list(reversed(rings[0])),6)
        self.face(rings[-1],6)
    def crown(self,center,scale,tile=1,seed=0):
        rand=random.Random(seed);cx,cy,cz=center;sx,sy,sz=scale
        n=14;nr=8
        rings=[]
        ripple=[rand.uniform(.88,1.12) for _ in range(n)]
        for i in range(nr+1):
            t=math.pi*i/nr
            ring=[]
            for j in range(n):
                a=math.tau*j/n
                r=math.sin(t)*ripple[j]*(1+.06*math.sin(i*3+j))
                ring.append((cx+sx*r*math.cos(a),cy+sy*r*math.sin(a),cz+sz*math.cos(t)))
            rings.append(ring)
        for i in range(nr):
            for j in range(n):
                shade=min(3,max(0,tile+(1 if i<3 else -1 if i>5 else 0)))
                self.face([rings[i][j],rings[i+1][j],rings[i+1][(j+1)%n],rings[i][(j+1)%n]],shade,True)
        # Jagged leaf silhouettes break up the larger crown masses.
        for j in range(70):
            a=rand.random()*math.tau;t=rand.uniform(.25,2.7)
            direction=Vector((math.sin(t)*math.cos(a),math.sin(t)*math.sin(a),math.cos(t)))
            center=Vector((cx+sx*direction.x,cy+sy*direction.y,cz+sz*direction.z))
            u=direction.cross(Vector((0,0,1))).normalized()
            w=direction.cross(u).normalized()
            size=rand.uniform(.13,.3)
            points=[]
            for k in range(10):
                angle=k*math.tau/10;r=size*(1 if k%2==0 else .55)
                points.append(tuple(center+u*math.cos(angle)*r+w*math.sin(angle)*r*.7+direction*.035))
            shade=min(3,max(0,tile+(1 if direction.z>.4 else -1 if direction.z<-.4 else 0)))
            self.face(points,shade)
    def finish(self,name):
        mesh=bpy.data.meshes.new(name);mesh.from_pydata(self.v,[],self.f);mesh.update()
        uv=mesh.uv_layers.new(name='UVMap')
        for poly,tile,smooth in zip(mesh.polygons,self.tiles,self.smooth):
            poly.use_smooth=smooth
            normal=poly.normal;axis=max(range(3),key=lambda i:abs(normal[i]));axes=[i for i in range(3) if i!=axis]
            # Map a single tile per polygon; inset avoids atlas bleeding.
            coords=[self.v[mesh.loops[k].vertex_index] for k in poly.loop_indices]
            a0=min(p[axes[0]] for p in coords);a1=max(p[axes[0]] for p in coords)
            b0=min(p[axes[1]] for p in coords);b1=max(p[axes[1]] for p in coords)
            for li,p in zip(poly.loop_indices,coords):
                u=(p[axes[0]]-a0)/max(a1-a0,.001);v=(p[axes[1]]-b0)/max(b1-b0,.001)
                uv.data[li].uv=((tile%4+(2+u*59)/64)/4,(tile//4+(2+v*59)/64)/4)
        bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001);bm.to_mesh(mesh);bm.free();mesh.update()
        obj=bpy.data.objects.new(name,mesh);scene.collection.objects.link(obj);obj.data.materials.append(mat)
        obj['woodland_generated']=True;obj['source']='Original AdventureRPG woodland kit; Gamma Emerald visual reference'
        return obj

assets=[]
for variant in range(3):
    m=Mesh();rand=random.Random(530+variant);height=[5.5,4.6,6.3][variant]
    m.tube([(0,0,0),(.04,0,.5),(-.08,.04,1.8),(.08,.1,3.3),(.12,.05,height-.7)],[.29,.24,.18,.14,.035])
    for j in range(6):
        a=j*math.tau/6+.3
        m.tube([(math.cos(a)*.65,math.sin(a)*.65,.035),(math.cos(a)*.3,math.sin(a)*.3,.18),(0,0,.55)],[.04,.13,.15],4,7)
    for j in range(8):
        a=j*2.399+variant;radius=rand.uniform(.7,1.55);z=height-1.2+rand.uniform(-.55,.55)
        pos=(math.cos(a)*radius,math.sin(a)*radius,z)
        m.tube([(0,0,2.1+j*.12),(pos[0]*.6,pos[1]*.6,z-.35),pos],[.13,.08,.025],4,7)
        m.crown(pos,(rand.uniform(.85,1.2),rand.uniform(.85,1.2),rand.uniform(.65,.95)),1+(j%3==0),variant*100+j)
    m.crown((0,0,height-.35),(1.3,1.2,.95),2,81+variant)
    assets.append(m.finish('SM_Woodland_Broadleaf_'+chr(65+variant)))

m=Mesh()
for j in range(7):
    a=j*2.399;r=.45 if j else 0
    m.crown((math.cos(a)*r,math.sin(a)*r,.38+R.random()*.24),(.48,.44,.38),1,j+63)
assets.append(m.finish('SM_Woodland_Bush'))

m=Mesh()
for j in range(9):
    a=j*math.tau/9;length=R.uniform(.55,.9)
    def p(t,side=0):return Vector((math.cos(a)*t*length-math.sin(a)*side,math.sin(a)*t*length+math.cos(a)*side,.06+math.sin(t*math.pi*.85)*length*.55))
    m.tube([p(0),p(.4),p(.75),p(1)],[.015,.012,.008,.002],7,5)
    for k in range(1,9):
        t=k/10;width=.15*(1-t)*length
        for sign in [-1,1]:
            base=p(t);tip=p(min(1,t+.16),width*sign);mid=(base+tip)*.5+Vector((0,0,.035))
            m.face([base,p(t-.045),tip,mid],12+(k%2))
            m.face([mid,tip,p(t+.05),base],13)
assets.append(m.finish('SM_Woodland_Fern'))

m=Mesh()
for j in range(34):
    a=R.random()*math.tau;x=R.uniform(-.42,.42);y=R.uniform(-.36,.36);h=R.uniform(.19,.49);w=R.uniform(.025,.055)
    u=Vector((math.cos(a),math.sin(a),0));base=Vector((x,y,0));bend=Vector((-math.sin(a),math.cos(a),0))*.1
    m.face([base-u*w,base+u*w,base+u*w*.6+bend*.5+Vector((0,0,h*.65)),base+bend+Vector((0,0,h)),base-u*w*.6+bend*.5+Vector((0,0,h*.65))],12+j%2)
assets.append(m.finish('SM_Woodland_Grass'))

for variant in range(2):
    m=Mesh();rand=random.Random(900+variant)
    n=10;rings=[]
    for z,r in [(0,.72),(.22,1),(.6,.78),(.85,.28)]:
        rings.append([(math.cos(j*math.tau/n)*r*rand.uniform(.85,1.14),math.sin(j*math.tau/n)*r*.72*rand.uniform(.85,1.12),z+rand.uniform(-.06,.06)) for j in range(n)])
    for i in range(3):
        for j in range(n):
            a,b,c,d=rings[i][j],rings[i][(j+1)%n],rings[i+1][(j+1)%n],rings[i+1][j]
            m.face([a,b,c],8+i if i<2 else 7);m.face([a,c,d],8+i if i<2 else 7)
    m.face(rings[-1],7)
    assets.append(m.finish('SM_Woodland_MossRock_'+chr(65+variant)))

m=Mesh();m.tube([(-1,0,.27),(0,0,.29),(1,0,.3)],[.25,.28,.23],4,14)
for x in [-.6,.2,.6]:m.crown((x,-.02,.52),(.32,.22,.08),1,int(x*10+20))
m.tube([(.2,0,.38),(.3,.2,.7),(.4,.23,.78)],[.1,.07,.025],4,7)
assets.append(m.finish('SM_Woodland_FallenLog'))
m=Mesh();m.tube([(0,0,0),(0,0,.18),(.025,0,.65)],[.48,.35,.3],4,12)
for j in range(5):
    a=j*math.tau/5;m.tube([(math.cos(a)*.65,math.sin(a)*.65,.04),(math.cos(a)*.3,math.sin(a)*.3,.17),(0,0,.33)],[.025,.12,.16],4,7)
assets.append(m.finish('SM_Woodland_Stump'))
m=Mesh()
for j in range(9):
    x,y=R.uniform(-.45,.45),R.uniform(-.35,.35);h=R.uniform(.17,.31)
    m.tube([(x,y,0),(x,y,h)],[.012,.007],7,5)
    for k in range(5):
        a=k*math.tau/5;c=Vector((x,y,h));u=Vector((math.cos(a),math.sin(a),0));w=Vector((-math.sin(a),math.cos(a),0))
        m.face([c,c+u*.055+w*.025,c+u*.09+Vector((0,0,.025)),c+u*.055-w*.025],15)
    m.face([(x-.018,y-.018,h+.01),(x+.018,y-.018,h+.01),(x+.018,y+.018,h+.01),(x-.018,y+.018,h+.01)],14)
assets.append(m.finish('SM_Woodland_Wildflowers'))

# A continuous ground skin and irregular trail replace the rectangular art overlays.
m=Mesh()
for ix in range(122):
    for iy in range(68):
        x=-31+ix*.5;y=-17+iy*.5
        patch=math.sin(x*.43)+math.sin(y*.7)+math.sin((x+y)*.61)
        tile=7 if patch<-.9 else 12 if patch<1 else 13
        m.face([(x,y,0),(x+.5,y,0),(x+.5,y+.5,0),(x,y+.5,0)],tile)
assets.append(m.finish('SM_Woodland_GroundSkin'))
m=Mesh()
for i in range(79):
    x=4+i*.5;xn=x+.5
    w=1.52+.12*math.sin(i*.8)+.06*math.cos(i*2.3)
    wn=1.52+.12*math.sin((i+1)*.8)+.06*math.cos((i+1)*2.3)
    bend=.14*math.sin(i*.19);bn=.14*math.sin((i+1)*.19)
    m.face([(x,bend-w,0),(xn,bn-wn,0),(xn,bn+wn,0),(x,bend+w,0)],11)
for i in range(36):
    y=-9+i*.5;w=1.5+.09*math.sin(i*1.3);wn=1.5+.09*math.sin((i+1)*1.3)
    m.face([(-w,y,0),(w,y,0),(wn,y+.5,0),(-wn,y+.5,0)],11)
# Connector between the hub lane and the eastbound trail.
m.face([(0,-1.5,0),(4,-1.5,0),(4,1.5,0),(0,1.5,0)],11)
assets.append(m.finish('SM_Woodland_TrailSkin'))

# Asset origins are at the ground and exports are metres converted to UE centimetres.
manifest=[]
for i,obj in enumerate(assets):
    bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
    bpy.ops.export_scene.fbx(filepath=str(ROOT/'FBX'/(obj.name+'.fbx')),use_selection=True,object_types={'MESH'},apply_unit_scale=True,axis_forward='-Y',axis_up='Z',bake_anim=False,path_mode='COPY',embed_textures=False)
    manifest.append({'name':obj.name,'file':str(ROOT/'FBX'/(obj.name+'.fbx')),'vertices':len(obj.data.vertices),'triangles':sum(len(p.vertices)-2 for p in obj.data.polygons),'size_m':list(obj.dimensions)})
    obj.location=((i%4)*6,(i//4)*6,0)
(ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2))
# Studio presentation is saved with the source so the models are easy to inspect.
world=bpy.data.worlds.new('Woodland_StudioWorld');world.use_nodes=True
background=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND')
background.inputs[0].default_value=(.16,.21,.18,1)
background.inputs[1].default_value=.5
scene.world=world
ld=bpy.data.lights.new('Woodland_StudioSun','SUN');lo=bpy.data.objects.new('Woodland_StudioSun',ld);scene.collection.objects.link(lo)
lo['woodland_generated']=True;lo.rotation_euler=(.4,-.5,-.4);ld.energy=2.3;ld.angle=.15
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'AdventureRPG_Woodland.blend'))
print('WOODLAND_KIT_EXPORTED '+json.dumps(manifest))
