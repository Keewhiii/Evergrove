from pathlib import Path
root=Path('E:/UE5 Projects/AdventureRPG/Scripts')
for name in ['author_forest_terrain_unreal.py','author_forest_atmosphere_unreal.py','author_living_ponds_unreal.py']:
 path=root/name;exec(compile(path.read_text(),str(path),'exec'),{})
