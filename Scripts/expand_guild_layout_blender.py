"""Expand the shell and circulation, preserving human-scale furniture assemblies."""
from mathutils import Matrix
ROOM_SCALE=26/18
def anchor_for(name,p):
 x,y,z=p
 # Architecture, stairs, railings and the broad rug expand with the room.
 if name.startswith(('PlankGrain','Stair','GalleryRail','Rug','EntranceRug','Curtain','WarmWindow','Window','HangingBanner','BannerDiamond','Lantern','WallDado')):return None
 if name.startswith(('Clock','UpperTitle')):return (0,17.66)
 if z>=3.6:
  if abs(x)>7.6 and y>15:return (-8 if x<0 else 8,16.8)
  return (min([-5.8,0,5.8],key=lambda a:abs(a-x)),16.4)
 if y>9.2:
  if x<-3.7:return (-5.2,12.8)
  if x>3.7:return (5.4,12.7)
  return (0,11.1)
 if abs(x)>5.05 and y<3.6:
  if y<1.8:return (-8 if x<0 else 8,1)
  return (-6.9 if x<0 else 6.9,2.5)
 if abs(x)>2.5:return (-3.85 if x<0 else 3.85,4.6 if y<6.15 else 7.65)
 return None
def relocate(p,anchor):
 x,y,z=p
 if anchor is None:return Vector((x*ROOM_SCALE,y*ROOM_SCALE,z))
 return Vector((x+anchor[0]*(ROOM_SCALE-1),y+anchor[1]*(ROOM_SCALE-1),z))
for group in ['Architecture','Furniture','Details']:
 for ob in groups[group]:
  pts=[ob.matrix_world@v.co for v in ob.data.vertices]
  center=sum(pts,Vector())/len(pts)
  anchor=None if group=='Architecture' else anchor_for(ob.name,center)
  # Keep the small entrance marker aligned with the unchanged linked exit.
  if ob.name.startswith('ExitThreshold'):anchor=(0,0)
  for vert,p in zip(ob.data.vertices,pts):vert.co=relocate(p,anchor)
  ob.matrix_world=Matrix.Identity(4);ob.data.update()
  layer=ob.data.uv_layers.active or ob.data.uv_layers.new(name='PaintedUV')
  for face in ob.data.polygons:
   axis=max(range(3),key=lambda k:abs(face.normal[k]))
   for li in face.loop_indices:
    p=ob.data.vertices[ob.data.loops[li].vertex_index].co
    layer.data[li].uv=(p.y/1.8,p.x/5.6) if axis==2 else ((p.x/3,p.z/3) if axis==1 else (p.y/3,p.z/3))
for item in colliders:
 name=item['name'];p=Vector(item['center']);s=list(item['size'])
 structural=name.startswith(('FloorSupport','RearWall','SideWall','UpperGallery','Stair_','GalleryRail','GallerySafetyRail','GalleryPillar'))
 anchor=None if structural else anchor_for(name,p)
 item['center']=list(relocate(p,anchor))
 if structural:s[0]*=ROOM_SCALE;s[1]*=ROOM_SCALE
 # Solid, simple footprints avoid catching the capsule under tabletop/bench edges.
 if name in ['Desk','Bench','SofaSeat']:
  top=p.z+s[2]/2;floor=3.6 if p.z>3.6 else 0
  item['center'][2]=(top+floor)/2;s[2]=top-floor
 item['size']=s
spawn_points=[{'name':name,'position_m':[x,y,z]} for name,x,y,z in [
 ('WestLounge',-11.8,6.2,1),('EastLounge',11.8,6.2,1),
 ('WestHall',-3.8,12.8,1),('EastHall',3.8,12.8,1),
 ('WestReceptionWaiting',-4.3,18.2,1),('EastReceptionWaiting',4.3,18.2,1),
 ('WestGallery',-4.2,24.5,4.6),('EastGallery',4.2,24.5,4.6)]]
(ROOT/'npc_spawn_points.json').write_text(json.dumps(spawn_points,indent=2))
(ROOT/'room_layout.json').write_text(json.dumps({'width_m':26,'depth_m':26,'previous_width_m':18,'previous_depth_m':18,'furniture_scale':1,'stairs_x_m':7.5*ROOM_SCALE,'stair_start_y_m':6.16*ROOM_SCALE,'gallery_front_y_m':14*ROOM_SCALE,'reception_anchor_y_m':11.1*ROOM_SCALE,'reception_approach_y_m':9.2+11.1*(ROOM_SCALE-1),'npc_spawn_slots':8},indent=2))
