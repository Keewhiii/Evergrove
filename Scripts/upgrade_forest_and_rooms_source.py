from pathlib import Path
import re
root=Path(__file__).resolve().parents[1];p=root/'Scripts/author_rural_map_unreal.py';s=p.read_text()
s=s.replace("for index,(name,asset,origin,yaw) in enumerate(buildings):","exec(compile((ROOT/'Scripts/rural_interior_details.py').read_text(),'rural_interior_details.py','exec'))\nfor index,(name,asset,origin,yaw) in enumerate(buildings):")
s=s.replace("room=(0,-8600,0) if guild else ((index-1)*1550,-10600,0)","room=(index*12000,-22000 if guild else -34000,0)")
s=s.replace("rw,rd=(1120,1000) if guild else (740,650)","rw,rd=(2600,2100) if guild else ((2600,2200) if name=='FarmBarn' else ((2500,1900) if asset=='SM_RuralCottage_B' else (2200,1800)))")
start=s.index(' if guild:\n  cube(\'Guild_ReceptionDesk\'');end=s.index(' portal(name+\'_Entrance\'',start)
s=s[:start]+" furnish_room(name,room,rw,rd,guild,name=='FarmBarn',index)\n if guild:text('VillageGuildSign','GUILD',local(origin,yaw,(0,d/2+50,370)),31,90)\n"+s[end:]
s=s.replace("(18000,14000,44)","(26000,16000,44)")
s=s.replace("trail=[[4400", "trail=[[9200,1800],[9800,1800],[9800,900],[8700,900],[8700,-350],[7600,-350],[7600,-1500],[6400,-1500],[6400,-300],[5600,-300],[5600,1000],[4700,1000],[4700,360],[4400")
s=s.replace("for i,(a,b) in enumerate(zip(trail,trail[1:])):path_segment(a,b,260,'Footpath_'+str(i))", "for i,(a,b) in enumerate(zip(trail,trail[1:])):path_segment(a,b,260,'Footpath_'+str(i))\nforest_forks=[[(8700,900),(7900,900),(7900,1800)],[(7600,-1500),(8100,-1500),(8100,-2350)],[(5600,1000),(6100,1000),(6100,2100)]]\nfor fi,points in enumerate(forest_forks):\n for ai,(a,b) in enumerate(zip(points,points[1:])):path_segment(a,b,220,'ForestFork_'+str(fi)+'_'+str(ai))")
s=s.replace('x-3550,y-470','x-9200,y-1800')
marker="# A loose, deep woodland surround beyond the walking bounds."
extra='''# Dense forest surrounds a winding route with optional side trails and dead ends.
for tx in range(4600,10800,360):
 for ty in range(-3000,3100,360):
  nearest=1e9
  for a,b,width in path_segments:
   dx=b[0]-a[0];dy=b[1]-a[1];t=max(0,min(1,((tx-a[0])*dx+(ty-a[1])*dy)/(dx*dx+dy*dy)))
   nearest=min(nearest,math.hypot(tx-a[0]-t*dx,ty-a[1]-t*dy))
  if nearest<470 or math.hypot(tx-9200,ty-1800)<500:continue
  tree(tx,ty,rng.uniform(.85,1.15))
  collider('Forest_ThicketBarrier',(tx,ty,0),0,(0,0,120),(350,350,240))
for mx,my in [(9550,1800),(8700,100),(6400,-900),(4800,1000)]:
 cube('Forest_TrailMarkerPost',(mx,my,95),(18,18,190),materials['Timber'],folder='Forest Trail Details')
 cube('Forest_TrailMarkerBoard',(mx,my,160),(160,22,60),materials['PlankLight'],folder='Forest Trail Details')
 text('Forest_TrailMarker','OLD TRAIL',(mx,my+14,175),18)
place('Hunter_Pack',F+'/SM_RuralBench',(9000,1890,0),(.45,.45,.6),folder='Forest Trail Details')
'''
s=s.replace(marker,extra+'\n'+marker)
s=s.replace('(200,-3300,9000,40),(200,3300,9000,40),(-4300,0,40,6600),(4680,0,40,6600)','(3250,-3300,15100,40),(3250,3300,15100,40),(-4300,0,40,6600),(10800,0,40,6600)')
s=s.replace('u.Vector(95,70,6)','u.Vector(160,70,6)').replace('u.Vector(200,0,280)','u.Vector(3250,0,280)')
s=s.replace("if isinstance(a,u.PlayerStart):a.set_actor_location(u.Vector(0,300,110)","if isinstance(a,u.PlayerStart):a.set_actor_location(u.Vector(9200,1800,110)")
s=s.replace("('Luna',(-210,-8690,100)","('Luna',(-580,-22450,100)")
s=s.replace("('Rein',(640,120,100),\"Easy there. I found you out by the old forest trail. The village is just west of here.\"", "('Rein',(9090,1790,100),\"I'm Rein, a hunter from Evergrove. I found you unconscious here. Follow the old trail markers west; explore carefully and you'll reach the village.\"")
s=s.replace("(SOURCE/'layout.json').write_text", "report['waking_clearing']=[9200,1800];report['hunter']=[9090,1790];report['forest_forks']=forest_forks\n(SOURCE/'layout.json').write_text")
p.write_text(s)
print('LARGE_ISOLATED_INTERIORS_AND_FOREST_SOURCE_READY')
