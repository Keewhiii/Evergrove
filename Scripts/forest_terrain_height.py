import math
HILLS=[(8500,-1900,145,1450,1350),(3700,-3900,165,1350,1250),(10300,3100,135,1600,1350),(7000,1200,105,1100,1400)]
WATER=[(8500,2500,700,500),(4100,2600,230,170),(7950,-4300,260,190)]
def smooth(a,b,x):
 t=max(0,min(1,(x-a)/(b-a)));return t*t*(3-2*t)
def terrain_height(x,y):
 h=sum(z*math.exp(-(((x-cx)/rx)**2+((y-cy)/ry)**2)*1.5) for cx,cy,z,rx,ry in HILLS)
 center=5750+180*math.sin(y/1200)+90*math.sin(y/470)
 h*=smooth(360,850,abs(x-center))
 for cx,cy,rx,ry in WATER:h*=smooth(1.3,2.1,math.hypot((x-cx)/rx,(y-cy)/ry))
 return h+1.0
