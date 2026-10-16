from pathlib import Path
import math,random,shutil
r=Path.cwd();out=r/'ContentSource/ForestAtmosphere';out.mkdir(exist_ok=True)
b=r/'Saved/ForestRecoveryBackup/BeforeAtmosphere';b.mkdir(parents=True,exist_ok=True)
for rel in ['Content/Game/World/BP_WoodlandWorld.uasset','Content/Maps/L_EvergroveForest.umap','Content/__ExternalActors__/Maps/L_EvergroveForest','Content/Environment/ForestFeatures/SM_ForestCartoonLog.uasset']:
 p=r/rel;d=b/rel;d.parent.mkdir(parents=True,exist_ok=True)
 if p.is_dir():shutil.copytree(p,d,dirs_exist_ok=True)
 elif p.exists():shutil.copy2(p,d)
verts=[];faces=[];uv=[];rng=random.Random(1618)
outline=[(-3,0),(-1.8,-5),(.2,-9),(1.9,-5.5),(3.4,-1.5),(2.3,4),(0,10),(-2.5,4)]
for x in range(1800,12001,300):
 for y in range(-5700,4801,300):
  phase=rng.random();angle=rng.random()*math.tau;size=rng.uniform(.72,1.15);start=len(verts)
  for lx,ly in outline+[(0,0)]:
   xx=lx*math.cos(angle)-ly*math.sin(angle);yy=lx*math.sin(angle)+ly*math.cos(angle)
   verts.append((x+xx*size,y+yy*size,740+(1.7 if lx==ly==0 else -.5*abs(lx))))
   uv.append((phase,1 if lx==ly==0 else .15))
  for i in range(8):faces.append((start+8,start+i,start+(i+1)%8))
  # Short visible petiole rather than a geometric cross silhouette.
  for lx,ly in [(-.35,-8),(.35,-8),(.2,-13),(-.2,-13)]:
   verts.append((x+(lx*math.cos(angle)-ly*math.sin(angle))*size,y+(lx*math.sin(angle)+ly*math.cos(angle))*size,740));uv.append((phase,.55))
  faces.append((start+9,start+10,start+11,start+12))
lines=['o SM_CanopyFallingLeaves','usemtl Leaf']+[f'v {x} {-y} {z}' for x,y,z in verts]+[f'vt {a} {b}' for a,b in uv]
lines+=['f '+' '.join(f'{i+1}/{i+1}' for i in f) for f in faces]
(out/'SM_CanopyFallingLeaves.obj').write_text('\n'.join(lines))
print('CANOPY_LEAVES',len(verts)//13)
