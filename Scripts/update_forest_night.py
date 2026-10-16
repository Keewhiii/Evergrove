"""Refresh coverage and night balance without resetting clock or camera authoring."""
import runpy
from build_companion_combat import *
runpy.run_path(str(ROOT/'Scripts/connect_night_materials.py'),run_name='__main__')
WORLD='/Game/Game/World/BP_WoodlandWorld.BP_WoodlandWorld'
source=(ROOT/'Saved/CombatAudit/ApplyDayNight.dsl').read_text(encoding='utf-8')
source=source.replace('(+ 0.45 (* d 0.55))','(+ 0.3 (* d 0.7))')
graph(WORLD,'ApplyDayNight',source)
call('compile_blueprint',{'blueprint':ref(WORLD),'warnings_as_errors':True})
call('save_assets',{'asset_paths':[]},ASSET)
print('FOREST_NIGHT_BALANCE_SAVED',flush=True)
