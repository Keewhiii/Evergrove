"""A world-scaled anime guild landmark, using planar architecture and crisp pixel materials."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'E:\UE5 Projects\AdventureRPG\ContentSource\GuildHall');scene=bpy.data.scenes.get('GuildHall_Studio') or bpy.data.scenes.new('GuildHall_Studio');bpy.context.window.scene=scene
for ob in list(scene.objects):bpy.data.objects.remove(ob,do_unlink=True)
materials={};groups={k:[] for k in ['Shell','Roof','Ornaments','Porch']}
def linear(c):
 c=c/255;return c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4
for name in ['Roof','Timber','Plaster','Stone']:
 mat=bpy.data.materials.get('M_Guild_'+name) or bpy.data.materials.new('M_Guild_'+name);mat.use_nodes=True;n=mat.node_tree.nodes;n.clear();out=n.new('ShaderNodeOutputMaterial');b=n.new('ShaderNodeBsdfPrincipled');tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(ROOT/('T_Guild_'+name+'.png')),check_existing=True);tex.interpolation='Closest';mat.node_tree.links.new(tex.outputs['Color'],b.inputs['Base Color']);b.inputs['Roughness'].default_value=.95;mat.node_tree.links.new(b.outputs[0],out.inputs['Surface']);materials[name]=mat
COLORS={'Gold':(202,156,61),'Dark':(29,35,35),'Glass':(151,237,229),'Banner':(117,31,37),'Crest':(25,92,91),'Iron':(43,47,43)}
for name,color in COLORS.items():
 mat=bpy.data.materials.get('M_Guild_'+name) or bpy.data.materials.new('M_Guild_'+name);mat.use_nodes=True;b=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');b.inputs['Base Color'].default_value=tuple(linear(c) for c in color)+(1,);b.inputs['Roughness'].default_value=.8
 if name=='Glass':b.inputs['Emission Color'].default_value=tuple(linear(c) for c in color)+(1,);b.inputs['Emission Strength'].default_value=3
 materials[name]=mat
def poly(name,points,mat,group='Shell',uv=None):
 pts=[Vector(p) for p in points];me=bpy.data.meshes.new(name);me.from_pydata(pts,[],[tuple(range(len(pts)))]);me.materials.append(materials[mat]);layer=me.uv_layers.new()
 if uv is None:
  ext=[max(p[a] for p in pts)-min(p[a] for p in pts) for a in range(3)];axes=sorted(range(3),key=lambda a:ext[a],reverse=True)[:2];axes.sort();uv=[(p[axes[0]]/2.8,p[axes[1]]/2.8) for p in pts]
 for li,co in zip(me.polygons[0].loop_indices,uv):layer.data[li].uv=co
 ob=bpy.data.objects.new(name,me);scene.collection.objects.link(ob);groups[group].append(ob);return ob
def box(name,center,size,mat,group='Shell'):
 x,y,z=center;a,b,c=[v/2 for v in size];v=[(x-a,y-b,z-c),(x+a,y-b,z-c),(x+a,y+b,z-c),(x-a,y+b,z-c),(x-a,y-b,z+c),(x+a,y-b,z+c),(x+a,y+b,z+c),(x-a,y+b,z+c)]
 for i,face in enumerate([(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)]):poly(name+'_'+str(i),[v[j] for j in face],mat,group)
def beam(name,a,b,width,mat='Timber',group='Shell'):
 a,b=Vector(a),Vector(b);v=(b-a).normalized();r=v.cross(Vector((0,1,0)))
 if r.length<.1:r=v.cross(Vector((1,0,0)))
 r.normalize();s=v.cross(r).normalized();r*=width/2;s*=width/2
 pts=[a-r-s,a+r-s,a+r+s,a-r+s,b-r-s,b+r-s,b+r+s,b-r+s]
 for i,f in enumerate([(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)]):poly(name+'_'+str(i),[pts[j] for j in f],mat,group)
def pyramid(name,x,y,z,w,d,peak):
 base=[(x-w/2,y-d/2,z),(x+w/2,y-d/2,z),(x+w/2,y+d/2,z),(x-w/2,y+d/2,z)]
 for i in range(4):poly(name+'_'+str(i),[base[i],base[(i+1)%4],(x,y,peak)],'Roof','Roof')
def disc(name,x,y,z,r,mat,group='Ornaments',n=40):return poly(name,[(x+math.cos(i*math.tau/n)*r,y,z+math.sin(i*math.tau/n)*r) for i in range(n)],mat,group)
def ring(name,x,y,z,r0,r1,mat,n=32):
 for i in range(n):
  a,b=i*math.tau/n,(i+1)*math.tau/n;poly(name+'_'+str(i),[(x+math.cos(a)*r0,y,z+math.sin(a)*r0),(x+math.cos(a)*r1,y,z+math.sin(a)*r1),(x+math.cos(b)*r1,y,z+math.sin(b)*r1),(x+math.cos(b)*r0,y,z+math.sin(b)*r0)],mat,'Ornaments')
def window(name,x,y,z,w=1.0,h=1.5):
 box(name+'_Recess',(x,y,z),(w+.26,.08,h+.26),'Dark','Ornaments');box(name+'_Glow',(x,y-.06,z),(w,.025,h),'Glass','Ornaments')
 for dx in [-w/2,0,w/2]:box(name+'_Mullion',(x+dx,y-.09,z),(.075,.08,h+.12),'Timber','Ornaments')
 for dz in [-h/2,0,h/2]:box(name+'_Rail',(x,y-.09,z+dz),(w+.14,.08,.075),'Timber','Ornaments')
 box(name+'_Sill',(x,y-.18,z-h/2-.10),(w+.42,.36,.15),'Stone','Ornaments')
def crest(name,x,y,z,size=1):
 points=[(-.65,.8),(.65,.8),(.62,-.2),(0,-.85),(-.62,-.2)]
 poly(name+'_Shield',[(x+a*size,y,z+b*size) for a,b in points],'Crest','Ornaments')
 for i in range(len(points)):
  a,b=points[i],points[(i+1)%len(points)];beam(name+'_Rim',(x+a[0]*size,y-.025,z+a[1]*size),(x+b[0]*size,y-.025,z+b[1]*size),.065*size,'Gold','Ornaments')
 star=[]
 for i in range(16):
  a=i*math.pi/8;r=(.48 if i%4==0 else .36) if i%2==0 else .15;star.append((x+math.sin(a)*r*size,y-.05,z+math.cos(a)*r*size))
 poly(name+'_Compass',star,'Gold','Ornaments')
 for sign in [-1,1]:poly(name+'_Wing',[(x+sign*a*size,y+.02,z+b*size) for a,b in [(.55,.5),(1.35,.7),(1.12,.28),(.92,.18),(.72,-.02),(.55,-.1)]],'Gold','Ornaments')

# Broad two-storey main hall with a high central gable and lower side wings.
box('CentralHall',(0,7,4.2),(8.8,14,8.0),'Plaster')
for side in [-1,1]:box('SideWing',(side*6.9,6,3.2),(5.0,12,6.0),'Plaster')
box('StoneFoundation',(0,6.9,.48),(19.2,14,.8),'Stone')
for y in [0,14]:poly('Gable', [(-4.4,y,8.2),(4.4,y,8.2),(0,y,13.4)],'Plaster')
for side in [-1,1]:
 poly('MainRoof',[(side*5.05,-.55,8.35),(side*5.05,14.45,8.35),(0,14.45,13.55),(0,-.55,13.55)],'Roof','Roof',[(0,0),(5,0),(5,2.4),(0,2.4)])
 poly('WingRoof',[(side*9.85,-.45,6.65),(side*9.85,12.4,6.65),(side*4.4,12.4,9.05),(side*4.4,-.45,9.05)],'Roof','Roof',[(0,0),(4.3,0),(4.3,2),(0,2)])
 beam('MainRake',(side*5.05,-.6,8.35),(0,-.6,13.55),.23,group='Roof');beam('MainEave',(side*5.05,-.55,8.35),(side*5.05,14.45,8.35),.23,group='Roof')
 beam('WingEave',(side*9.85,-.47,6.65),(side*9.85,12.45,6.65),.23,group='Roof')
 beam('WingRake',(side*6.65,-.5,8.059),(side*4.4,-.5,9.05),.22,group='Roof')
 beam('OuterWingRake',(side*9.85,-.5,6.65),(side*9.43,-.5,6.835),.22,group='Roof')
beam('Ridge',(0,-.65,13.55),(0,14.55,13.55),.26,group='Roof')
for z in [.9,3.9,6.2]:box('FrontTieBeam',(0,-.09,z),(19.0,.22,.23),'Timber')
for x in [-9.25,-6.9,-4.4,-2.3,2.3,4.4,6.9,9.25]:box('FrontUpright',(x,-.10,3.65),(.20,.24,5.7 if abs(x)>4.5 else 7.3),'Timber')
box('CentralUpperTie',(0,-.12,8.2),(9.1,.26,.24),'Timber')
for side in [-1,1]:
 beam('GableBrace',(side*4.4,-.12,8.2),(0,-.12,13.4),.20)
 for y in [2.4,5.6,8.8,12.0]:box('SidePost',(side*9.42,y,3.3),(.18,.20,5.9),'Timber')
 for z in [.9,3.9,6.2]:box('SideTie',(side*9.42,6,z),(.2,12,.2),'Timber')
 for x in [5.5,7.8]:
  beam('PanelDiagonal',(side*x,-.13,4.05),(side*(x+1.0),-.13,5.9),.13)
 for y in [3.4,7.0,10.5]:
  # Flat luminous side panes, laid onto the wall rather than floating cubes.
  x=side*9.54;poly('SideWindow',[(x,y-.55,1.5),(x,y+.55,1.5),(x,y+.55,3.0),(x,y-.55,3.0)],'Glass','Ornaments')
  for yy in [y-.6,y,y+.6]:box('SideWindowBar',(x+side*.025,yy,2.25),(.07,.07,1.65),'Timber','Ornaments')
  for zz in [1.45,2.25,3.05]:box('SideWindowCross',(x+side*.025,y,zz),(.07,1.3,.07),'Timber','Ornaments')

# Corner towers anchor the huge silhouette without widening beyond the 22m hub.
for side in [-1,1]:
 x=side*8.05;box('CornerTower',(x,1.3,4.85),(2.65,3.2,9.3),'Plaster');box('TowerBase',(x,1.3,.6),(2.85,3.4,1.0),'Stone')
 for xx in [x-1.23,x+1.23]:box('TowerTimber',(xx,-.35,4.95),(.2,.22,9.2),'Timber')
 for z in [3.9,6.7,9.4]:box('TowerBand',(x,1.3,z),(2.9,3.4,.22),'Timber')
 pyramid('TowerRoof',x,1.3,9.52,3.5,4.0,12.5)
 beam('TowerFinial',(x,1.3,12.5),(x,1.3,13.1),.10,'Gold','Roof')
 for z in [2.25,5.35,8.05]:window('TowerWindow',x,-.40,z,1.05,1.55)
 for z in [2.25,5.1]:window('WingWindow',side*5.5,-.18,z,1.05,1.55)

# Tall closed double entrance, original guild heraldry, large sign and a glowing rose window.
door=[(-1.5,-.23,.2),(1.5,-.23,.2),(1.5,-.23,3.1)]+[(1.5*math.cos(i*math.pi/24),-.23,3.1+1.5*math.sin(i*math.pi/24)) for i in range(1,25)]
poly('ArchedDoubleDoor',door,'Timber','Ornaments')
for i in range(12):
 a,b=i*math.pi/12,(i+1)*math.pi/12;poly('ArchStone',[(1.58*math.cos(a),-.30,3.1+1.58*math.sin(a)),(1.92*math.cos(a),-.30,3.1+1.92*math.sin(a)),(1.92*math.cos(b),-.30,3.1+1.92*math.sin(b)),(1.58*math.cos(b),-.30,3.1+1.58*math.sin(b))],'Stone','Ornaments')
for x in [-1.74,1.74]:box('DoorJamb',(x,-.27,1.65),(.34,.34,2.9),'Stone','Ornaments')
box('DoorCenter',(0,-.27,1.72),(.07,.08,3.04),'Dark','Ornaments')
for z in [.75,2.55]:box('DoorIronStrap',(0,-.31,z),(2.85,.07,.09),'Iron','Ornaments')
for x in [-.27,.27]:ring('DoorHandle',x,-.36,1.6,.08,.12,'Gold',16)
box('GuildSign',(0,-.33,5.35),(6.6,.20,.8),'Timber','Ornaments')
for z in [4.95,5.75]:box('SignGoldRule',(0,-.46,z),(6.7,.05,.055),'Gold','Ornaments')
font=bpy.data.curves.new('GuildTitle_Editable','FONT');font.body="ADVENTURERS' GUILD";font.align_x='CENTER';font.size=.46;font.extrude=.006
fontpath=Path(r'C:\Windows\Fonts\georgiab.ttf')
if fontpath.exists():font.font=bpy.data.fonts.load(str(fontpath))
title=bpy.data.objects.new('GuildTitle_Editable',font);scene.collection.objects.link(title);title.location=(0,-.48,5.17);title.rotation_euler=(math.pi/2,0,0);font.materials.append(materials['Gold']);bpy.context.view_layer.update()
if title.dimensions.x>6.1:title.scale*=6.1/title.dimensions.x
copy=title.copy();copy.data=title.data.copy();scene.collection.objects.link(copy);bpy.ops.object.select_all(action='DESELECT');copy.select_set(True);bpy.context.view_layer.objects.active=copy;bpy.ops.object.convert(target='MESH');bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);groups['Ornaments'].append(copy);title.hide_render=True;title.hide_set(True)
crest('GuildCrest',0,-.32,6.9,1.05)
disc('RoseGlass',0,-.20,10.1,1.0,'Glass');ring('RoseFrame',0,-.25,10.1,.98,1.16,'Timber');ring('RoseGold',0,-.28,10.1,.90,.95,'Gold')
for i in range(8):
 a=i*math.pi/4;beam('RoseSpoke',(0,-.30,10.1),(.94*math.cos(a),-.30,10.1+.94*math.sin(a)),.075,'Gold','Ornaments')
for x in [-3.35,3.35]:
 box('BannerPole',(x,-.38,7.95),(1.35,.12,.11),'Gold','Ornaments')
 poly('HangingBanner',[(x-.48,-.35,7.88),(x+.48,-.35,7.88),(x+.48,-.35,4.7),(x,-.35,4.4),(x-.48,-.35,4.7)],'Banner','Ornaments',[(0,0),(1,0),(1,1),(.5,1.1),(0,1)])
 crest('BannerCrest',x,-.39,6.7,.43)

# Bell tower above the central roof, with a warm brass bell and small clock.
box('BellTower',(0,8.9,14.15),(2.6,2.8,3.4),'Plaster');box('BellOpening',(0,7.45,14.05),(1.65,.07,1.7),'Dark','Ornaments')
for x in [-1.2,1.2]:box('BelfryPost',(x,7.43,14.15),(.18,.20,3.45),'Timber')
for z in [12.6,15.8]:box('BelfryTie',(0,8.9,z),(2.8,3.0,.2),'Timber')
for i in range(16):
 a,b=i*math.tau/16,(i+1)*math.tau/16
 for r0,z0,r1,z1 in [(.16,14.65,.24,14.2),(.24,14.2,.43,13.95),(.43,13.95,.43,13.88)]:poly('Bell',[(r0*math.cos(a),7.34+r0*math.sin(a),z0),(r0*math.cos(b),7.34+r0*math.sin(b),z0),(r1*math.cos(b),7.34+r1*math.sin(b),z1),(r1*math.cos(a),7.34+r1*math.sin(a),z1)],'Gold','Ornaments')
beam('BellHanger',(0,7.34,14.65),(0,7.34,14.96),.06,'Iron','Ornaments')
disc('ClockFace',0,7.39,15.12,.43,'Dark');ring('ClockRim',0,7.35,15.12,.41,.48,'Gold');beam('ClockMinute',(0,7.31,15.12),(0,7.31,15.47),.035,'Gold','Ornaments');beam('ClockHour',(0,7.30,15.12),(.22,7.30,15.24),.045,'Gold','Ornaments')
pyramid('BellRoof',0,8.9,15.95,3.4,3.6,17.35);beam('BellFinial',(0,8.9,17.35),(0,8.9,18.0),.09,'Gold','Roof')
for side in [-1,1]:
 box('Chimney',(side*5.8,9.6,9.6),(.85,.85,2.2),'Stone');box('ChimneyCap',(side*5.8,9.6,10.8),(1.1,1.1,.18),'Dark')

# Accessible landing and matching benches sit over the existing walkable deck.
box('FrontLanding',(0,-1.65,.19),(12,3.3,.18),'Timber','Porch')
box('LowerStep',(0,-3.65,.045),(7.2,.65,.09),'Stone','Porch');box('UpperStep',(0,-3.22,.105),(7.8,.35,.21),'Stone','Porch')
for side in [-1,1]:
 x=side*4.85;box('BenchSeat',(x,-1.6,.55),(1.6,.6,.12),'Timber','Porch')
 for dx in [-.55,.55]:box('BenchLeg',(x+dx,-1.6,.32),(.14,.45,.55),'Timber','Porch')
 box('BenchBack',(x,-1.88,.83),(1.6,.10,.50),'Timber','Porch')

manifest=[]
for group,parts in groups.items():
 bpy.ops.object.select_all(action='DESELECT')
 for ob in parts:ob.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];name='SM_GuildHall_'+group;file=ROOT/'FBX'/(name+'.fbx')
 bpy.ops.export_scene.fbx(filepath=str(file),use_selection=True,object_types={'MESH'},apply_unit_scale=True,axis_forward='-Y',axis_up='Z',bake_anim=False,path_mode='COPY');manifest.append({'name':name,'file':str(file),'parts':len(parts)})
 parent=bpy.data.objects.new('Guild_'+group,None);scene.collection.objects.link(parent)
 for ob in parts:ob.parent=parent
(ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2));(ROOT/'palette.json').write_text(json.dumps(COLORS,indent=2))
world=bpy.data.worlds.new('GuildStudioWorld');world.use_nodes=True;next(n for n in world.node_tree.nodes if n.type=='BACKGROUND').inputs['Color'].default_value=(.17,.22,.29,1);next(n for n in world.node_tree.nodes if n.type=='BACKGROUND').inputs['Strength'].default_value=.5;scene.world=world
lightdata=bpy.data.lights.new('GuildSun','SUN');lightdata.energy=2.2;light=bpy.data.objects.new('GuildSun',lightdata);scene.collection.objects.link(light);light.rotation_euler=(math.radians(28),math.radians(-25),math.radians(-30))
camdata=bpy.data.cameras.new('GuildPreview');camdata.type='ORTHO';camdata.ortho_scale=35
cam=bpy.data.objects.new('GuildPreview',camdata);scene.collection.objects.link(cam);target=Vector((0,5.0,7.4));cam.location=target+Vector((0,-math.cos(math.radians(34)),math.sin(math.radians(34))))*55;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();scene.camera=cam
scene.render.resolution_x=1500;scene.render.resolution_y=1050;scene.render.resolution_percentage=100;scene.render.film_transparent=True
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'AdventureRPG_GuildHall.blend'));print('GUILD_HALL_BUILT '+json.dumps(manifest))
