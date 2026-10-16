"""Connect the title screen to gameplay without touching existing save files."""
from build_companion_combat import *
W='/Game/Game/World/BP_WoodlandWorld.BP_WoodlandWorld'
GI='/Game/Game/UI/BP_EvergroveGameInstance.BP_EvergroveGameInstance'
graph(W,'ResumeTitleSave',f'''(fn ResumeTitleSave ()
 (bind instance (Utilities|Casting|CastToBP_EvergroveGameInstance :Object (Game|GetGameInstance))
  (:then
   (if (Class|BPEvergroveGameInstance|GetPendingLoad :self instance)
    (bind hero (Utilities|Casting|CastToBP_Player :Object (Game|GetPlayerCharacter 0))
     (:then
      (Class|BPEvergroveGameInstance|SetPendingLoad :self instance :PendingLoad false)
      (Class|BPPlayer|SetSaveSlotName :self hero :SaveSlotName (Class|BPEvergroveGameInstance|GetPendingSlot :self instance))
      (bind loaded (Class|BPPlayer|LoadProgress :self hero))
      (if (not loaded)
       (Class|BPEvergroveGameInstance|SetMenuError :self instance :MenuError "This save could not be loaded. Your save has been kept.")
       (Game|OpenLevel(byName) :LevelName "/Game/Maps/L_EvergroveIntro" :bAbsolute true :Options ""))) (:CastFailed)))) (:CastFailed)))''')
source=ROOT/'Saved/CombatAudit/UpdateCamera.dsl'
code=source.read_text(encoding='utf-8')
if '(CallFunction|ResumeTitleSave)' not in code:
 code=code.replace('(fn UpdateCamera (Delta)','(fn UpdateCamera (Delta)\n (CallFunction|ResumeTitleSave)',1)
graph(W,'UpdateCamera',code,[('Delta','float',None)])
call('compile_blueprint',{'blueprint':ref(W),'warnings_as_errors':True})
call('save_assets',{'asset_paths':[W]},ASSET)
print('EVERGROVE_GAMEPLAY_BRIDGE_SAVED',flush=True)
