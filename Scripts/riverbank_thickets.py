"""Dense, impassable riverbanks; the timber bridge is the only river approach."""
import math,random,json
from pathlib import Path
import unreal as u

def fill_riverbanks(place,collider,existing):
 layout=json.loads(Path('E:/UE5 Projects/AdventureRPG/ContentSource/RuralVillage/forest_layout.json').read_text())
 segments=[(a,b) for points in [layout['route']]+layout['forks'] for a,b in zip(points,points[1:])]
 def route_distance(x,y):
  best=1e9
  for a,b in segments:
   dx=b[0]-a[0];dy=b[1]-a[1];t=max(0,min(1,((x-a[0])*dx+(y-a[1])*dy)/(dx*dx+dy*dy)))
   best=min(best,math.hypot(x-a[0]-t*dx,y-a[1]-t*dy))
  return best
 def center(y):return 5750+180*math.sin(y/1200)+90*math.sin(y/470)
 def width(y):return 130+25*math.sin(y/700+.4)
 rng=random.Random(16217);count=0
 tree_positions=[a.get_actor_location() for a in existing if a.get_actor_label().startswith(('Forest_CanopyTree','Forest_RiverbankTree'))]
 for x in range(4740,7040,300):
  for y in range(-5800,4700,300):
   d=abs(x-center(y))
   if d<width(y)+185 or d>1100 or route_distance(x,y)<390:continue
   if any(math.hypot(x-p.x,y-p.y)<170 for p in tree_positions):continue
   scale=rng.uniform(.88,1.06)
   a=place('Forest_RiverbankTree','/Game/Environment/BreezeWoodland/SM_BreezeTree_'+rng.choice(['A','B','C']),(x,y,0),(scale,scale,scale),folder='Forest Riverbank Thickets')
   a.static_mesh_component.set_cast_shadow(False)
   collider('Forest_RiverbankThicket',(x,y,0),0,(0,0,120),(300,300,240));count+=1
 barriers=0
 # Continuous collision closes narrow strips between the tree bundles and water.
 for y in range(-5800,4400,100):
  if abs(y+3150)<330:continue
  for side in [-1,1]:
   x=center(y)+side*(width(y)+195)
   collider('Forest_RiverbankClosed',(x,y,0),0,(0,0,140),(390,110,280));barriers+=1
 return {'added_trees':count,'riverbank_barriers':barriers,'bridge_open_half_width':330}
