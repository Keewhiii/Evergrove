from build_companion_combat import *
W='/Game/Game/World/BP_WoodlandWorld.BP_WoodlandWorld'
O='/Game/Game/UI/BP_EvergroveOpeningHUD.BP_EvergroveOpeningHUD'
code=(ROOT/'Saved/CombatAudit/CreateLanternLights.dsl').read_text()
if 'L_EvergroveStart' not in code:
 code=code.replace('(bind lamp5','(if (Utilities|String|EqualExactly(String) (Game|GetCurrentLevelName :bRemovePrefixString true) "L_EvergroveStart") (return))\n(bind lamp5',1)
 graph(W,'CreateLanternLights',code)
code=(ROOT/'Saved/CombatAudit/DrawSequence.dsl').read_text().replace(':TextureUWidth 1.0',':TextureUWidth 0.42',1)
graph(O,'DrawSequence',code,[('SizeX','int',None),('SizeY','int',None)])
for target in [W,O]:call('compile_blueprint',{'blueprint':ref(target),'warnings_as_errors':True})
call('save_assets',{'asset_paths':[W,O]},ASSET)
