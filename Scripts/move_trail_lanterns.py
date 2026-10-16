"""Move all five posts down the trail, aligned with the shared light settings."""
from build_companion_combat import *
from woodland_lighting_settings import TRAIL_LANTERNS
import re
cozy='/Game/Game/World/BP_CozyWoodland.BP_CozyWoodland'
source=call('read_graph_dsl',{'graph':ref(cozy+':Dress1')})
lines=source.splitlines();index=0
for i,line in enumerate(lines):
    if 'SM_GuildLantern3D' not in line:continue
    x,y=TRAIL_LANTERNS[index];index+=1
    lines[i]=re.sub(r'\(Math\|Vector\|MakeVector [^)]*\)',f'(Math|Vector|MakeVector {float(x)} {float(y)} 3.0)',line,count=1)
assert index==5,index
source='\n'.join(lines)
source=re.sub(r'\(CallFunction\|Part (\(Math\|Vector\|MakeVector [^)]*\)) (\(Math\|Vector\|MakeVector [^)]*\)) ("[^"]*") ("[^"]*")\)',r'(CallFunction|Part :Position \1 :Scale \2 :Mesh \3 :Material \4)',source)
graph(cozy,'Dress1',source)
call('compile_blueprint',{'blueprint':ref(cozy),'warnings_as_errors':True})
call('save_assets',{'asset_paths':[]},ASSET)
print('TRAIL_LANTERNS_MOVED',TRAIL_LANTERNS,flush=True)
