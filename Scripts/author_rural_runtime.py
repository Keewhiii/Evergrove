"""Route new games to the rural forest map while preserving legacy saves."""
from build_companion_combat import *
V='/Game/Game/World/BP_RuralVillageLighting.BP_RuralVillageLighting'
W='/Game/Game/World/BP_WoodlandWorld.BP_WoodlandWorld'
O='/Game/Game/UI/BP_EvergroveOpeningHUD.BP_EvergroveOpeningHUD'
M='/Game/Game/UI/BP_EvergroveIntroHUD.BP_EvergroveIntroHUD'
GI='/Game/Game/UI/BP_EvergroveGameInstance.BP_EvergroveGameInstance'
create(V,'/Script/Engine.Actor');var(V,'World',W+'_C')
graph(V,'ValidObject','''(fn ValidObject (Object) (Utilities|IsValid Object (:"Is Valid" (return true)) (:"Is Not Valid" (return false))))''',[('Object','/Script/CoreUObject.Object',None)],[('Valid','bool',None)])
graph(V,'CacheWorld',f'''(fn CacheWorld () (for actor (Actor|GetAllActorsOfClass :ActorClass "{W}_C") (bind woodland (Utilities|Casting|CastToBP_WoodlandWorld :Object actor) (:then (Variables|Default|SetWorld woodland)) (:CastFailed))))''')
graph(V,'UpdateWindows','''(fn UpdateWindows ()
 (if (not (CallFunction|ValidObject :Object (Variables|Default|GetWorld))) (return))
 (bind factor (Class|BPWoodlandWorld|GetNightLightFactor :self (Variables|Default|GetWorld)))
 (for actor (Actor|GetAllActorswithTag :Tag "RuralWindowLight")
  (bind lamp (Utilities|Casting|CastToPointLight :Object actor)
   (:then (Rendering|Components|Light|SetIntensity :self (Class|Light|GetLightComponent :self lamp) :NewIntensity (* factor 350.0))) (:CastFailed))))''')
graph(V,'EventGraph','''(event EventBeginPlay (CallFunction|CacheWorld)) (event EventTick (DeltaSeconds) (CallFunction|UpdateWindows))''')
var(GI,'PendingMap','string');var(M,'SavedMap','string')
defaults(GI,{'PendingMap':'/Game/Maps/L_EvergroveStart'})
code=(ROOT/'Saved/CombatAudit/ReadSaveSummary.dsl').read_text()
needle='(Utilities|String|EqualExactly(String) (Class|BPPlayerSave|GetMapName :self snapshot) "L_WoodlandBlockout")'
code=code.replace(needle,'(or '+needle+' (Utilities|String|EqualExactly(String) (Class|BPPlayerSave|GetMapName :self snapshot) "L_EvergroveStart"))')
code=code.replace('(Variables|Default|SetHasSave true)','(Variables|Default|SetHasSave true)\n (Variables|Default|SetSavedMap (Utilities|String|Append "/Game/Maps/" (Class|BPPlayerSave|GetMapName :self snapshot)))')
graph(M,'ReadSaveSummary',code)
code=(ROOT/'Saved/CombatAudit/RequestStart.dsl').read_text()
code=code.replace('(if LoadSaved','(if LoadSaved\n (Class|BPEvergroveGameInstance|SetPendingMap :self (Variables|Default|GetInstance) :PendingMap (Variables|Default|GetSavedMap))',1)
graph(M,'RequestStart',code,[('LoadSaved','bool',None)])
code=(ROOT/'Saved/CombatAudit/UpdateMenu.dsl').read_text().replace(':LevelName "/Game/Maps/L_WoodlandBlockout"',':LevelName (Utilities|String|StringToName (Class|BPEvergroveGameInstance|GetPendingMap :self (Variables|Default|GetInstance)))')
graph(M,'UpdateMenu',code,[('Delta','float',None)])
code=(ROOT/'Saved/CombatAudit/FinishDream.dsl').read_text().replace('/Game/Maps/L_WoodlandBlockout','/Game/Maps/L_EvergroveStart')
graph(O,'FinishDream',code)
code=(ROOT/'Saved/CombatAudit/InitializeOpening.dsl').read_text().replace('"L_WoodlandBlockout") 1 0','"L_EvergroveIntro") 0 1')
graph(O,'InitializeOpening',code)
code=(ROOT/'Saved/CombatAudit/UpdateCamera.dsl').read_text().replace('x -550.0 3700.0','x -2700.0 4300.0').replace('y -500.0 600.0','y -1900.0 1900.0')
graph(W,'UpdateCamera',code,[('Delta','float',None)])
code=(ROOT/'Saved/CombatAudit/CreateLanternLights.dsl').read_text()
if 'L_EvergroveStart' not in code:
 code=code.replace('(bind lamp5','(if (Utilities|String|EqualExactly(String) (Game|GetCurrentLevelName :bRemovePrefixString true) "L_EvergroveStart") (return))\n(bind lamp5',1)
 graph(W,'CreateLanternLights',code)
for target in [V,W,O,M,GI]:call('compile_blueprint',{'blueprint':ref(target),'warnings_as_errors':True})
call('save_assets',{'asset_paths':[V,W,O,M,GI]},ASSET)
print('RURAL_RUNTIME_AND_LEGACY_LOAD_ROUTING_SAVED',flush=True)
