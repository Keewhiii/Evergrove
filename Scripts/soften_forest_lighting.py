from build_companion_combat import *
W='/Game/Game/World/BP_WoodlandWorld.BP_WoodlandWorld'
code=(ROOT/'Saved/CombatAudit/ApplyDayNight.dsl').read_text()
code=code.replace('(+ 0.3 (* d 0.32))','(+ 0.34 (* d 0.44))').replace('(select forest 0.35 1.0)','(select forest 0.48 1.0)').replace('(select forest 0.6 1.0)','(select forest 0.82 1.0)')
# Neutral canopy daylight, rather than the warm yellow tint used in the village.
code=code.replace(':B daycolor :Alpha',':B (select forest (Math|Color|MakeColor 0.91 0.97 1.0 1.0) daycolor) :Alpha')
graph(W,'ApplyDayNight',code)
call('compile_blueprint',{'blueprint':ref(W),'warnings_as_errors':True})
call('save_assets',{'asset_paths':[W]},ASSET)
print('NEUTRAL_READABLE_FOREST_LIGHTING_SAVED',flush=True)
