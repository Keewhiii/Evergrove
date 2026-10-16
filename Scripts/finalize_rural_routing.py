from build_companion_combat import *
M='/Game/Game/UI/BP_EvergroveIntroHUD.BP_EvergroveIntroHUD'
O='/Game/Game/UI/BP_EvergroveOpeningHUD.BP_EvergroveOpeningHUD'
W='/Game/Game/World/BP_WoodlandWorld.BP_WoodlandWorld'
for bp,name,inputs in [(M,'ReadSaveSummary',[]),(O,'FinishDream',[]),(W,'CreateLanternLights',[])]:
 code=(ROOT/'Saved/CombatAudit'/(name+'.dsl')).read_text().replace('L_EvergroveVillage','L_EvergroveStart')
 graph(bp,name,code,inputs)
code=(ROOT/'Saved/CombatAudit/EvaluateCaption.dsl').read_text().replace('You who carries a burden','You who bear a burden')
graph(O,'EvaluateCaption',code)
for target in [M,O,W]:call('compile_blueprint',{'blueprint':ref(target),'warnings_as_errors':True})
call('save_assets',{'asset_paths':[M,O,W]},ASSET)
