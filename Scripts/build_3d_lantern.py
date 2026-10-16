"""Build a solid, guild-style lantern post as an editable OBJ source (centimetres)."""
from pathlib import Path
root = Path(__file__).resolve().parents[1] / 'ContentSource/Lantern3D'
root.mkdir(parents=True, exist_ok=True)
vertices, faces = [], []
def box(center, size, mat):
    x,y,z=center; a,b,c=[s/2 for s in size]; n=len(vertices)
    vertices.extend([(x-a,y-b,z-c),(x+a,y-b,z-c),(x+a,y+b,z-c),(x-a,y+b,z-c),
                     (x-a,y-b,z+c),(x+a,y-b,z+c),(x+a,y+b,z+c),(x-a,y+b,z+c)])
    for f in [(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)]:
        faces.append((mat,[n+i+1 for i in f]))
box((0,0,5),(48,48,10),'Iron')
box((0,0,14),(34,34,8),'Iron')
box((0,0,23),(23,23,10),'Gold')
box((0,0,105),(12,12,154),'Iron')
for z in [35,165,180]: box((0,0,z),(19,19,5),'Gold')
box((0,0,187),(42,42,10),'Iron')
box((0,0,213),(30,30,44),'Glass')
for x in [-18,18]:
    for y in [-18,18]: box((x,y,214),(5,5,48),'Iron')
for z in [193,235]: box((0,0,z),(43,43,5),'Gold')
box((0,0,240),(51,51,6),'Iron')
n=len(vertices); vertices.extend([(-28,-28,243),(28,-28,243),(28,28,243),(-28,28,243),(0,0,268)])
for f in [(0,1,4),(1,2,4),(2,3,4),(3,0,4),(3,2,1,0)]: faces.append(('Roof',[n+i+1 for i in f]))
box((0,0,272),(7,7,8),'Gold')
# Unreal's OBJ importer flips the source Y axis; retain Z-up.
lines=['mtllib Lantern.mtl','o SM_GuildLantern']
lines += [f'v {x} {-y} {z}' for x,y,z in vertices]
for mat in ['Iron','Gold','Glass','Roof']:
    lines.append('usemtl '+mat)
    for m,f in faces:
        if m==mat: lines.append('f '+' '.join(map(str,f)))
(root/'SM_GuildLantern.obj').write_text('\n'.join(lines))
(root/'Lantern.mtl').write_text('\n'.join('newmtl '+m+'\nKd .5 .5 .5' for m in ['Iron','Gold','Glass','Roof']))
print(root/'SM_GuildLantern.obj')
