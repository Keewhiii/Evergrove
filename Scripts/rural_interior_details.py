"""Native room furnishing helpers, executed in the map builder's namespace."""
def furnish_room(name,room,rw,rd,guild,barn,index):
 x,y,_=room
 def box(label,p,size,mat='Timber',solid=False):return cube(name+'_'+label,(x+p[0],y+p[1],p[2]),size,materials[mat],solid,folder='Interiors')
 box('InteriorBackdrop',(0,0,-45),(rw+3500,rd+5000,8),'Iron')
 def table(label,px,py,sx=280,sy=170):
  box(label+'Top',(px,py,105),(sx,sy,22),'PlankLight',True)
  for dx in [-sx/2+18,sx/2-18]:
   for dy in [-sy/2+18,sy/2-18]:box(label+'Leg',(px+dx,py+dy,57),(22,22,95))
 def chair(px,py):
  box('ChairSeat',(px,py,62),(100,100,18),'PlankLight',True)
  box('ChairBack',(px,py-42,115),(100,16,105))
  for dx in [-35,35]:
   for dy in [-35,35]:box('ChairLeg',(px+dx,py+dy,35),(14,14,55))
 def shelf(px,py,width=330):
  box('ShelfBack',(px,py,150),(width,25,280))
  for z in [30,115,200,285]:box('ShelfBoard',(px,py+32,z),(width,80,14),'PlankLight')
  for dx in [-width/2+10,width/2-10]:box('ShelfSide',(px+dx,py+30,150),(20,80,290))
  for row,z in enumerate([65,150,235]):
   for n in range(8):box('Books',(px-width/2+28+n*(width-45)/8,py+45,z),(20,40,50+(n%3)*9),['Moss','Cream','ShingleLight'][((n+row+index)%3)])
 def hearth(px,py):
  box('HearthBase',(px,py,28),(320,180,36),'Stone',True)
  for dx in [-130,130]:box('HearthPillar',(px+dx,py-25,125),(58,120,190),'StoneLight',True)
  box('HearthMantel',(px,py-25,225),(350,150,40),'StoneLight')
  box('HearthDarkOpening',(px,py-70,110),(200,20,140),'Iron')
  for dx in [-55,30]:box('Firewood',(px+dx,py+5,60),(105,65,32),'Timber')
  light(name+'_HearthLight',(x+px,y+py+50,120),100,450)
 def kitchen(px,py):
  box('KitchenCabinet',(px,py,100),(470,150,175),'Plank',True)
  box('KitchenWorktop',(px,py,192),(500,180,20),'StoneLight')
  for dx in [-155,0,155]:
   box('CabinetDoor',(px+dx,py+78,105),(142,10,145),'PlankLight')
   box('CabinetHandle',(px+dx+42,py+90,120),(9,12,32),'Iron')
  box('WashBasin',(px+135,py,209),(115,90,18),'Iron')
  box('CuttingBoard',(px-130,py+10,207),(125,80,10),'Cream')
  for n in range(3):box('KitchenJar',(px-170+n*70,py-40,230),(40,40,65),'StoneLight')
  shelf(px,py-105,480)
 # Detailed shell: skirting, posts, window recesses, frames and curtains.
 for side in [-1,1]:
  box('Skirting',(side*(rw/2-25),0,35),(22,rd,45))
  for py in [-rd/2+100,0,rd/2-140]:box('WallPost',(side*(rw/2-30),py,200),(45,45,370))
 box('BackSkirting',(0,-rd/2+25,35),(rw,25,45))
 for px in [-rw*.28,rw*.28]:
  box('WindowRecess',(px,-rd/2+20,220),(270,15,180),'Iron')
  box('WindowGlass',(px,-rd/2+30,220),(235,12,150),'Cream')
  box('WindowSill',(px,-rd/2+65,125),(300,90,22),'PlankLight')
  for dx in [-130,0,130]:box('WindowFrame',(px+dx,-rd/2+45,220),(17,25,195))
  for dx in [-175,175]:box('Curtain',(px+dx,-rd/2+60,225),(65,18,230),'Moss')
 for px in [-rw*.28,rw*.28]:
  for py in [-rd*.27,rd*.22]:light(name+'_RoomLight',(x+px,y+py,310),500,1100)
 if guild:
  table('Reception',-rw*.22,-rd*.22,620,170)
  for px in [-750,-400]:shelf(px,-rd/2+100,300)
  for px in [350,650]:
   for py in [-250,250]:chair(px,py)
  table('GuildMeeting',500,0,430,340)
  hearth(rw/2-250,-rd/2+120)
  box('NoticeBoard',(-rw/2+50,-200,210),(25,450,260),'PlankLight')
  for n in range(6):box('PostedNotice',(-rw/2+68,-340+n*58,210),(9,42,135),'Cream')
  box('GuildMap',(500,0,122),(300,230,8),'Cream')
  return
 if barn:
  for px in [-rw*.32,rw*.32]:
   for py in [-rd*.32,-rd*.08,rd*.18]:
    box('HayBale',(px,py,85),(240,200,145),'Wheat',True)
    for dx in [-65,65]:box('HayBinding',(px+dx,py,90),(18,207,155),'Timber')
  table('Workbench',0,-rd/2+160,450,160);shelf(0,-rd/2+80,480)
  for px in [-300,0,300]:box('SupplyCrate',(px,rd*.22,90),(180,150,150),'Plank',True)
  return
 # Sleeping alcove and storage nook, with a broad open doorway into the living room.
 partition=-rd*.12;left=-rw/2+30;right=rw*.08;gap=-rw*.22
 for a,b in [(left,gap-130),(gap+130,right)]:
  box('BedroomPartition',((a+b)/2,partition,155),(b-a,26,285),'PlankLight',True)
 box('BedroomPost',(right,partition-210,155),(28,420,285),'Timber',True)
 bx=-rw*.28;by=-rd*.32
 box('BedFrame',(bx,by,55),(270,390,70),'Timber',True)
 for dx in [-120,120]:
  for dy in [-175,175]:box('BedPost',(bx+dx,by+dy,85),(25,25,135),'PlankLight')
 box('Headboard',(bx,by-180,120),(275,30,170),'Plank')
 box('Mattress',(bx,by,102),(250,355,32),'Cream')
 box('Quilt',(bx,by+30,126),(250,285,20),['Moss','ShingleLight','Cream'][index%3])
 for n in range(5):box('QuiltStripe',(bx-100+n*50,by+30,138),(12,275,4),'PlankLight')
 box('Pillow',(bx,by-135,135),(175,65,28),'Cream')
 box('BedsideChest',(bx+230,by-80,65),(140,135,100),'Plank',True)
 box('BedsideBook',(bx+230,by-80,125),(70,90,14),'Moss')
 shelf(-rw/2+230,-rd/2+110,320)
 kitchen(rw*.27,-rd*.37);hearth(rw*.33,-rd*.03)
 table('Dining',-rw*.18,rd*.20,320,210)
 for px in [-rw*.18-210,-rw*.18+210]:chair(px,rd*.20)
 chair(-rw*.18,rd*.20-165)
 for px in [-rw*.18-80,-rw*.18+60]:box('TablePlaceSetting',(px,rd*.20,121),(60,60,9),'Cream')
 box('Sideboard',(-rw/2+150,rd*.23,95),(190,440,160),'Plank',True)
 for py in [rd*.23-130,rd*.23,rd*.23+130]:box('DrawerHandle',(-rw/2+255,py,115),(14,45,10),'Iron')
 box('StorageChest',(rw*.30,rd*.27,65),(290,180,100),'Plank',True)
 for dx in [-105,105]:box('ChestBand',(rw*.30+dx,rd*.27,72),(22,190,115),'Iron')
 for n in range(3):box('FoldedLinen',(rw*.30,rd*.27,130+n*18),(180-n*15,130,15),'Cream')
 box('EntryRunner',(0,rd/2-260,15),(230,460,4),'Moss')
 for px in [-rw*.36,rw*.36]:box('WallPicture',(px,-rd/2+45,320),(130,20,90),'Moss')
