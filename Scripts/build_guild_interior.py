"""Editable Blender cutaway guild: central reception, twin stairs and walkable gallery."""
import bpy, math, json, random
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'E:\UE5 Projects\AdventureRPG\ContentSource\GuildInterior');ROOT.mkdir(exist_ok=True);(ROOT/'FBX').mkdir(exist_ok=True)
scene=bpy.data.scenes.get('GuildInterior_Studio') or bpy.data.scenes.new('GuildInterior_Studio');bpy.context.window.scene=scene
for ob in list(scene.objects):bpy.data.objects.remove(ob,do_unlink=True)
colors={'FloorA':(181,124,63),'FloorB':(194,139,73),'FloorC':(165,109,55),'Trim':(83,46,33),'Cream':(225,202,148),'Red':(134,46,43),'Teal':(46,119,117),'Gold':(226,177,81),'Iron':(42,49,51),'Glass':(168,225,218),'Paper':(238,218,170),'BookBlue':(49,85,112),'BookGreen':(69,105,67),'BookRed':(149,63,54),'Leaf':(63,123,59),'LeafLight':(119,171,70),'Pot':(165,99,66),'Cushion':(183,80,57)}
materials={}
colors['LampGlass']=(255,209,121)
def lin(c):
 c/=255;return c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4
for k,col in colors.items():
 m=bpy.data.materials.get('M_Interior_'+k) or bpy.data.materials.new('M_Interior_'+k);m.use_nodes=True;b=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');b.inputs['Base Color'].default_value=tuple(lin(c) for c in col)+(1,);b.inputs['Roughness'].default_value=.95
 if k in ['Glass','LampGlass']:b.inputs['Emission Color'].default_value=tuple(lin(c) for c in col)+(1,);b.inputs['Emission Strength'].default_value=2
 materials[k]=m
groups={k:[] for k in ['Architecture','Furniture','Details','DoorLeft','DoorRight','FacadeOpen']};colliders=[]
def poly(name,points,mat,group='Details'):
 me=bpy.data.meshes.new(name);me.from_pydata(points,[],[tuple(range(len(points)))]);me.materials.append(materials[mat]);ob=bpy.data.objects.new(name,me);scene.collection.objects.link(ob);groups[group].append(ob);return ob
def box(name,p,s,mat='Trim',group='Furniture',collision=False):
 x,y,z=p;a,b,c=[v/2 for v in s];v=[(x-a,y-b,z-c),(x+a,y-b,z-c),(x+a,y+b,z-c),(x-a,y+b,z-c),(x-a,y-b,z+c),(x+a,y-b,z+c),(x+a,y+b,z+c),(x-a,y+b,z+c)]
 me=bpy.data.meshes.new(name);me.from_pydata(v,[],[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)]);me.materials.append(materials[mat]);ob=bpy.data.objects.new(name,me);scene.collection.objects.link(ob);groups[group].append(ob)
 if group not in ['DoorLeft','DoorRight']:
  bevel=ob.modifiers.new('PaintedEdgeBevel','BEVEL');bevel.width=min(.025,min(s)*.10);bevel.segments=1
 if collision:colliders.append({'name':name,'center':p,'size':s})
def text(name,body,p,size=.35,mat='Gold'):
 cu=bpy.data.curves.new(name,'FONT');cu.body=body;cu.align_x='CENTER';cu.size=size;cu.extrude=.002
 fp=Path(r'C:\Windows\Fonts\georgiab.ttf')
 if fp.exists():cu.font=bpy.data.fonts.load(str(fp))
 ob=bpy.data.objects.new(name,cu);scene.collection.objects.link(ob);ob.location=p;ob.rotation_euler=(math.pi/2,0,0);cu.materials.append(materials[mat]);bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.object.convert(target='MESH');bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);groups['Details'].append(ob)
def rail(name,x0,x1,y,z):
 box(name+'Top',((x0+x1)/2,y,z+.85),(x1-x0,.13,.13),'Trim','Architecture')
 box(name+'Gold',((x0+x1)/2,y-.015,z+.91),(x1-x0,.14,.035),'Gold','Details')
 n=max(1,int((x1-x0)/.8))
 for i in range(n+1):box(name+'Post',(x0+(x1-x0)*i/n,y,z+.43),(.11,.13,.85),'Trim','Architecture',True)
def plant(x,y,z=0):
 box('Planter',(x,y,z+.28),(.55,.55,.55),'Pot')
 for j,(dx,dz,w) in enumerate([(-.25,.75,.65),(.18,.96,.75),(0,1.2,.6)]):
  # Layered angular 2D foliage cards, matching the woodland's stylization.
  pts=[(-.5,0),(-.6,.3),(-.4,.6),(-.25,.75),(0,.8),(.3,.7),(.52,.45),(.6,.2),(.4,0)]
  poly('PlantLeaf',[(x+dx+a*w,y-j*.05,z+dz+b*w) for a,b in pts],'LeafLight' if j==2 else 'Leaf')
def shelf(x,y,z=0,w=2.0):
 box('Bookcase',(x,y,z+1.05),(w,.48,2.1),'Trim')
 rng=random.Random(int((x+20)*31+y*7))
 for level in range(3):
  zz=z+.18+level*.62;box('Shelf',(x,y-.28,zz),(w,.12,.10),'Gold')
  for j in range(int(w/.18)-1):
   h=rng.uniform(.32,.49);box('Book',(x-w/2+.2+j*.18,y-.29,zz+h/2+.07),(.13,.17,h),rng.choice(['BookBlue','BookGreen','BookRed','Paper']))
def desk(x,y,z=0,w=2.5):
 box('Desk',(x,y,z+.88),(w,.85,.15),'FloorB',collision=True)
 for dx in [-w/2+.2,w/2-.2]:box('DeskPedestal',(x+dx,y,z+.42),(.35,.65,.84),'Trim')
 box('Ledger',(x-.2,y-.08,z+.99),(.55,.40,.04),'Paper','Details');box('Inkpot',(x+.4,y+.12,z+1.02),(.12,.12,.13),'BookBlue','Details')
def bench(x,y,z=0,w=2.0):
 box('Bench',(x,y,z+.47),(w,.43,.13),'FloorA',collision=True)
 for dx in [-w/2+.2,w/2-.2]:box('BenchLeg',(x+dx,y,z+.23),(.14,.35,.46),'Trim')
# Warm plank floor; board seams and occasional short painted grain clusters.
box('FloorSupport',(0,9,-.15),(18,18,.30),'Trim','Architecture',True)
rng=random.Random(441)
for row in range(45):
 y=.2+row*.4
 for col in range(9):
  x=-8+col*2;mat=rng.choice(['FloorA','FloorB','FloorA','FloorC']);box('Plank',(x,y,.012),(1.98,.382,.024),mat,'Architecture')
  if rng.random()<.42:box('PlankGrain',(x+rng.uniform(-.55,.5),y+rng.uniform(-.1,.1),.027),(rng.uniform(.2,.65),.018,.005),'FloorC','Details')
# Open front cutaway; tall rear wall and stepped side walls do not cover the player.
box('RearWall',(0,18.12,4.0),(18.4,.24,8),'Cream','Architecture',True)
for side in [-1,1]:
 box('SideWall',(side*9.12,9,2.7),(.24,18,5.4),'Cream','Architecture',True)
 box('WallSkirting',(side*8.96,9,.22),(.08,18,.44),'Red','Architecture')
 for y in [0,4.5,9,13.5,18]:box('WallPost',(side*8.9,y,2.7),(.22,.22,5.4),'Trim','Architecture')
box('RearSkirting',(0,17.95,.24),(18,.1,.48),'Red','Architecture')
for x in [-9,-6,-3,0,3,6,9]:box('RearTimber',(x,17.92,4),(.22,.2,8),'Trim','Architecture')
for z in [3.5,7.8]:box('RearTie',(0,17.90,z),(18,.20,.22),'Trim','Architecture')
# Full-width second floor at rear, reached by symmetrical real staircases.
box('UpperGallery',(0,16,3.48),(18,4,.24),'FloorB','Architecture',True)
for side in [-1,1]:
 x=side*7.5
 for i in range(24):
  y=6.32+i*.32;h=(i+1)*.15;box('Stair_'+str(side)+'_'+str(i),(x,y,h/2),(2.15,.32,h),'FloorA','Architecture',True)
  box('StairNosing',(x,y-.145,h+.018),(2.19,.055,.035),'Gold','Details')
  for edge in [-1,1]:
   if i%4==0:box('StairPost',(x+edge*1.04,y,h+.43),(.09,.09,.86),'Trim','Details')
   # Sloping handrail segmented along the steps; no solid side-wall obstruction.
   a=Vector((x+edge*1.04,y-.16,h+.85));b=Vector((x+edge*1.04,y+.16,h+1.0));d=b-a
   ob=None
   bpy.ops.mesh.primitive_cube_add(size=1,location=(a+b)/2);ob=bpy.context.object;ob.name='StairHandrail';ob.dimensions=(.10,.10,d.length);ob.rotation_euler=d.to_track_quat('Z','Y').to_euler();ob.data.materials.append(materials['Trim']);bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);groups['Architecture'].append(ob)
 if side==-1:
  rail('GalleryRail',-6.35,6.35,13.96,3.6)
  colliders.append({'name':'GallerySafetyRail','center':(0,13.96,4.05),'size':(12.7,.13,.9)})
 # Tall pillars support the balcony, leaving center circulation open.
 box('GalleryPillar',(side*5.9,14.3,1.75),(.32,.32,3.5),'Trim','Architecture',True)
# Reception station in the middle, with a distinct rear workspace and open side access.
box('ReceptionDais',(0,11.1,.065),(5.8,3,.13),'Red','Furniture')
box('ReceptionCounter',(0,10.05,.48),(5.1,.75,.96),'Trim','Furniture',True)
box('CounterInlay',(0,9.66,.46),(4.6,.04,.52),'Teal','Details')
box('CounterLip',(0,10.05,1.02),(5.35,.94,.16),'FloorB','Furniture')
for x in [-2.3,0,2.3]:box('CounterGold',(x,9.62,.46),(.05,.05,.52),'Gold','Details')
desk(0,11.9,0,3.4)
shelf(-2.35,12.4,0,1.0);shelf(2.35,12.4,0,1.0)
box('ReceptionSignBack',(0,12.8,2.1),(4.2,.16,.75),'Teal','Furniture')
text('ReceptionSign','GUILD RECEPTION',(0,12.70,1.99),.31)
for x in [-1.35,1.25]:box('ReceptionLedger',(x,9.93,1.13),(.60,.42,.06),'Paper','Details')
box('DeskBell',(0,9.86,1.17),(.15,.15,.15),'Gold','Details')
for x in [-3.25,3.25]:plant(x,11.8)
# Main hall communal tables, lounge and quest board, with broad clear walkways.
for x,y in [(-3.85,4.6),(3.85,4.6),(-3.85,7.65),(3.85,7.65)]:
 desk(x,y,0,2.1);bench(x,y-1.0,w=1.9);bench(x,y+1.0,w=1.9)
 box('TableRunner',(x,y,.976),(.55,.75,.025),'Teal','Details')
 box('Mug',(x+.52,y,1.05),(.13,.13,.13),'Cream','Details')
for side in [-1,1]:
 box('SofaSeat',(side*6.9,2.5,.38),(2.6,.85,.50),'Teal','Furniture',True)
 box('SofaBack',(side*6.9,2.85,.85),(2.6,.20,.85),'Teal','Furniture')
 for dx in [-1.2,1.2]:box('SofaArm',(side*6.9+dx,2.5,.65),(.20,.9,.45),'Gold','Furniture')
 plant(side*8.0,1)
box('QuestBoard',(5.4,12.7,1.65),(2.8,.22,2.1),'Trim','Furniture')
box('QuestCork',(5.4,12.55,1.65),(2.55,.05,1.85),'FloorC','Details')
text('RequestTitle','REQUESTS',(5.4,12.48,2.8),.28)
for i in range(8):box('QuestNotice',(4.45+(i%4)*.61,12.49,1.2+(i//4)*.73),(.42,.035,.56),'Paper','Details')
shelf(-5.2,12.8,0,2.5)
# Upstairs guild master's desk, library and quiet meeting corners.
for x in [-5.8,0,5.8]:
 desk(x,16.4,3.6,2.3);bench(x,15.3,3.6,w=1.8)
 shelf(x,17.55,3.6,2.6)
for x in [-8.0,8.0]:plant(x,16.8,3.6)
text('UpperTitle','MEMBERS GALLERY',(0,17.72,6.6),.44)
for x in [-4.5,4.5]:
 box('HangingBanner',(x,17.67,5.55),(.8,.04,2.8),'Red','Details')
 poly('BannerDiamond',[(x-.25,17.63,5.6),(x,17.63,6.1),(x+.25,17.63,5.6),(x,17.63,5.1)],'Gold')
for x in [-7.4,-2.7,2.7,7.4]:
 box('WarmWindow',(x,17.80,6.0),(1.25,.04,1.8),'Glass','Details')
 for dx in [-.68,0,.68]:box('WindowMullion',(x+dx,17.74,6.0),(.08,.08,1.96),'Trim','Details')
 for z in [5.06,6.0,6.94]:box('WindowRail',(x,17.73,z),(1.42,.08,.08),'Trim','Details')
# Entrance threshold and two hinged leaves exported with pivot at each jamb.
box('ExitThreshold',(0,.18,.02),(3.4,.5,.04),'Red','Architecture')
for side,group in [(-1,'DoorLeft'),(1,'DoorRight')]:
 # Local door mesh is already relative to its hinge; same model used outside and inside.
 a=0 if side==-1 else -1.5;b=1.5 if side==-1 else 0
 pts=[(a,0,.2),(b,0,.2),(b,0,3.1)]
 for i in range(13):
  angle=(0+i*math.pi/24) if side==1 else (math.pi/2+i*math.pi/24)
  worldx=1.5*math.cos(angle);pts.append((worldx-side*1.5,0,3.1+1.5*math.sin(angle)))
 poly(group,pts,'FloorC',group)
 for z in [.75,2.55]:box('DoorStrap',((a+b)/2,-.04,z),(1.42,.08,.09),'Iron',group)
 box('DoorHandle',((a+b)/2-side*.48,-.09,1.6),(.10,.12,.23),'Gold',group)
# Detailed set dressing and UVs are native Blender geometry and source materials.
exec(compile((Path(r'E:\UE5 Projects\AdventureRPG\Scripts')/'polish_guild_interior_blender.py').read_text(encoding='utf-8'),'polish_guild_interior_blender.py','exec'))
exec(compile((Path(r'E:\UE5 Projects\AdventureRPG\Scripts')/'expand_guild_layout_blender.py').read_text(encoding='utf-8'),'expand_guild_layout_blender.py','exec'))
# Export an open-door facade by omitting the old closed slab and its fittings.
ext=bpy.data.scenes.get('GuildHall_Studio')
if ext:
 original=[ob for ob in ext.objects if ob.type=='MESH' and ob.parent and ob.parent.name=='Guild_Ornaments' and not ob.name.startswith(('ArchedDoubleDoor','DoorCenter','DoorIronStrap','DoorHandle'))]
 bpy.ops.object.select_all(action='DESELECT')
 for ob in original:
  cp=ob.copy();cp.data=ob.data.copy();cp.parent=None;scene.collection.objects.link(cp);cp.select_set(True);groups['FacadeOpen'].append(cp)
 materials['PortalDark']=bpy.data.materials['M_Guild_Dark']
 opening=[(-1.5,-.25,.2),(1.5,-.25,.2),(1.5,-.25,3.1)]+[(1.5*math.cos(i*math.pi/24),-.25,3.1+1.5*math.sin(i*math.pi/24)) for i in range(1,25)]
 poly('DoorwayDarkOpening',opening,'PortalDark','FacadeOpen')
manifest=[]
for group,parts in groups.items():
 if not parts:continue
 bpy.ops.object.select_all(action='DESELECT')
 for ob in parts:ob.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];name='SM_Guild_'+group+('_Roomy' if group in ['Architecture','Furniture','Details'] else '_Detailed');file=ROOT/'FBX'/(name+'.fbx');bpy.ops.export_scene.fbx(filepath=str(file),use_selection=True,object_types={'MESH'},apply_unit_scale=True,axis_forward='-Y',axis_up='Z',bake_anim=False,path_mode='COPY');manifest.append({'name':name,'file':str(file),'parts':len(parts)})
 if group=='FacadeOpen':
  for ob in parts:bpy.data.objects.remove(ob,do_unlink=True)
 if group.startswith('Door'):
  for ob in parts:ob.hide_render=True;ob.hide_set(True)
(ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2));(ROOT/'palette.json').write_text(json.dumps(colors,indent=2));(ROOT/'collision.json').write_text(json.dumps(colliders,indent=2))
world=bpy.data.worlds.new('InteriorWorld');world.use_nodes=True;bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs['Color'].default_value=(.32,.28,.22,1);bg.inputs['Strength'].default_value=.8;scene.world=world
ld=bpy.data.lights.new('InteriorSun','SUN');ld.energy=2.4;lo=bpy.data.objects.new('InteriorSun',ld);scene.collection.objects.link(lo);lo.rotation_euler=(.4,-.35,-.4)
cd=bpy.data.cameras.new('InteriorPreview');cd.type='ORTHO';cd.ortho_scale=37;cam=bpy.data.objects.new('InteriorPreview',cd);scene.collection.objects.link(cam);target=Vector((0,13,3.5));cam.location=target+Vector((0,-.819,.574))*48;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();scene.camera=cam;scene.render.resolution_x=1400;scene.render.resolution_y=1100;scene.render.resolution_percentage=100;scene.render.film_transparent=True
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'AdventureRPG_GuildInterior.blend'));print('GUILD_INTERIOR_BUILT',json.dumps(manifest),'COLLISION',len(colliders))
