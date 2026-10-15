"""Executed in the Blender builder's namespace before exports."""
# Guild rug, bordered with a compass motif, stopping well clear of both stairs.
box('EntranceRug',(0,5.3,.042),(3.35,5.0,.025),'Teal','Details')
for x in [-1.56,1.56]:box('RugBorder',(x,5.3,.06),(.035,4.7,.006),'Gold','Details')
for y in [2.95,7.65]:box('RugBorder',(0,y,.06),(3.12,.035,.006),'Gold','Details')
for i in range(16):
 a=i*math.pi/8;r=.73 if i%2==0 else .30
 b=(i+1)*math.pi/8;s=.73 if (i+1)%2==0 else .30
 poly('RugCompass',[(0,5.3,.066),(math.sin(a)*r,5.3+math.cos(a)*r,.066),(math.sin(b)*s,5.3+math.cos(b)*s,.066)],'Gold')
# Upholstery seams and cushions give the lounge a finished miniature appearance.
for side in [-1,1]:
 x=side*6.9
 for dx in [-.65,.65]:
  box('SofaSeatPad',(x+dx,2.42,.67),(1.18,.66,.16),'Teal','Details')
  box('SofaPillow',(x+dx,2.64,.98),(.44,.18,.44),'Cushion','Details')
  box('PillowButton',(x+dx,2.535,.98),(.045,.025,.045),'Gold','Details')
 # Small side table with pottery, leaving the entry route and stairs clear.
 box('LoungeEndTable',(side*5.25,2.55,.50),(.55,.65,.09),'FloorB','Furniture')
 box('LoungeEndTableLeg',(side*5.25,2.55,.25),(.10,.12,.50),'Trim','Furniture')
 box('LoungeVase',(side*5.25,2.55,.69),(.18,.18,.28),'Cream','Details')
 for j in range(3):
  box('VaseStem',(side*5.25+(j-1)*.065,2.55,.95),(.018,.018,.30),'Leaf','Details')
  box('VaseFlower',(side*5.25+(j-1)*.065,2.55,1.10),(.10,.05,.10),'Gold','Details')
# Reception work area: side panels, drawers, ink, a quill and an open ledger.
for side in [-1,1]:
 box('StationSidePanel',(side*2.52,11.0,.43),(.12,1.9,.86),'Trim','Furniture')
 box('PanelInset',(side*2.44,11.0,.45),(.03,1.55,.52),'FloorC','Details')
for x in [-1.05,1.05]:
 for z in [.25,.49,.73]:
  box('ReceptionDrawer',(x,11.45,z),(.64,.035,.18),'FloorC','Details')
  box('DrawerPull',(x,11.42,z),(.13,.055,.035),'Gold','Details')
box('InkBottle',(.65,9.99,1.20),(.13,.13,.19),'BookBlue','Details')
poly('DeskQuill',[(.65,9.97,1.27),(.84,9.97,1.58),(.93,9.97,1.64),(.91,9.97,1.49)],'Paper')
for x in [-1.35,1.25]:
 for j in range(5):box('LedgerWriting',(x,9.80+j*.055,1.165),(.33 if j%2 else .43,.012,.004),'FloorC','Details')
# Handwritten requests, pinned corners and a stylized map beside reception.
for i in range(8):
 x=4.45+(i%4)*.61;z=1.2+(i//4)*.73
 box('NoticePin',(x,12.46,z+.22),(.06,.02,.06),'BookRed','Details')
 for j in range(4):box('NoticeInk',(x,12.46,z+.12-j*.07),(.24 if j%2 else .30,.015,.015),'Trim','Details')
box('GuildMapFrame',(-4.8,13.42,2.65),(2.4,.14,1.3),'Trim','Details')
box('GuildMapPaper',(-4.8,13.32,2.65),(2.18,.04,1.09),'Paper','Details')
for j in range(8):
 x=-5.65+j*.23;z=2.58+math.sin(j*.9)*.21
 box('MapRoute',(x,13.29,z),(.25,.02,.028),'Teal','Details')
for x,z in [(-5.6,2.5),(-4.6,2.75),(-3.95,2.7)]:box('MapTown',(x,13.265,z),(.09,.025,.09),'Red','Details')
# Curtained upper windows, wall panelling, a clock and brass wall lamps.
for x in [-7.4,-2.7,2.7,7.4]:
 box('CurtainRod',(x,17.58,7.05),(1.82,.10,.10),'Gold','Details')
 for side in [-1,1]:
  for j in range(3):box('CurtainFold',(x+side*(.73+j*.085),17.55-j*.018,6.10),(.105,.06,1.75),'Teal' if j%2 else 'BookBlue','Details')
  box('CurtainTie',(x+side*.82,17.46,5.70),(.28,.04,.055),'Gold','Details')
for x in [-7.5,-4.5,-1.5,1.5,4.5,7.5]:
 for z in [.45,3.72]:box('WallDadoCap',(x,17.70,z),(2.95,.12,.12),'Trim','Architecture')
# Clock face drawn as crisp flat shapes, mounted high on the rear wall.
cx,cy,cz=0,17.66,7.30
poly('ClockRim',[(cx+math.sin(i*math.tau/32)*.50,cy,cz+math.cos(i*math.tau/32)*.50) for i in range(32)],'Trim')
poly('ClockFace',[(cx+math.sin(i*math.tau/32)*.43,cy-.025,cz+math.cos(i*math.tau/32)*.43) for i in range(32)],'Paper')
for i in range(12):
 a=i*math.tau/12;box('ClockTick',(math.sin(a)*.35,cy-.05,cz+math.cos(a)*.35),(.045,.02,.055),'Trim','Details')
box('ClockMinute',(0,cy-.07,cz+.12),(.025,.03,.26),'Iron','Details');box('ClockHour',(.095,cy-.075,cz),(.20,.03,.025),'Iron','Details')
for x,y,z in [(-5.6,13.65,2.4),(5.6,13.65,2.4),(-8.5,17.2,5.0),(8.5,17.2,5.0)]:
 box('LanternBracket',(x,y+.12,z+.25),(.08,.35,.08),'Iron','Details')
 box('LanternBody',(x,y,z),(.25,.20,.38),'Iron','Details')
 box('LanternWarmPane',(x,y-.11,z),(.19,.025,.27),'LampGlass','Details')
 for dx in [-.11,.11]:box('LanternMullion',(x+dx,y-.13,z),(.025,.03,.34),'Iron','Details')
 box('LanternCap',(x,y,z+.23),(.32,.26,.07),'Iron','Details')
# Books get visible spine bindings and volume labels.
for group in ['Furniture','Details']:
 for ob in list(groups[group]):
  if ob.name.startswith('Book.') or ob.name=='Book':
   # Boxes use baked world vertices; world-space bounds are stable before export.
   vs=[Vector(v.co) for v in ob.data.vertices];mx=[sum(v[k] for v in vs)/len(vs) for k in range(3)]
   for dz in [-.11,.11]:box('SpineBand',(mx[0],mx[1]-.09,mx[2]+dz),(.11,.015,.017),'Gold','Details')
# Planar UVs with consistent real-world scale; flooring grain runs along each plank.
for group,parts in groups.items():
 for ob in parts:
  if ob.type!='MESH':continue
  layer=ob.data.uv_layers.active or ob.data.uv_layers.new(name='PaintedUV')
  for face in ob.data.polygons:
   n=face.normal;axis=max(range(3),key=lambda k:abs(n[k]))
   for li in face.loop_indices:
    p=ob.matrix_world@ob.data.vertices[ob.data.loops[li].vertex_index].co
    uv=(p.y/1.8,p.x/5.6) if axis==2 else ((p.x/3,p.z/3) if axis==1 else (p.y/3,p.z/3))
    layer.data[li].uv=uv
for name in ['FloorA','FloorB','FloorC','Trim','Cream']:
 texture=ROOT/('T_Interior_Plaster.png' if name=='Cream' else 'T_Interior_Oak.png')
 if not texture.exists():continue
 m=materials[name];b=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(texture),check_existing=True);tex.interpolation='Closest'
 mix=m.node_tree.nodes.new('ShaderNodeMixRGB');mix.blend_type='MIX';mix.inputs[0].default_value=.6 if name=='Cream' else (.2 if name=='Trim' else .35);mix.inputs[1].default_value=b.inputs['Base Color'].default_value;m.node_tree.links.new(tex.outputs['Color'],mix.inputs[2]);m.node_tree.links.new(mix.outputs[0],b.inputs['Base Color'])
