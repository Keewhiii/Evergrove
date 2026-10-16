from build_companion_combat import *
W='/Game/Game/World/BP_WoodlandWorld.BP_WoodlandWorld'
var(W,'TravelRestoring','bool')
code='''(fn ResumeMapTravel ()
 (if (Variables|Default|GetTravelRestoring) (return))
 (bind instance (Utilities|Casting|CastToBP_EvergroveGameInstance :Object (Game|GetGameInstance))
 (:then (if (Class|BPEvergroveGameInstance|GetTravelPending :self instance)
  (bind hero (Utilities|Casting|CastToBP_Player :Object (Game|GetPlayerCharacter 0))
  (:then
   (Class|BPPlayer|SetSaveSlotName :self hero :SaveSlotName (Class|BPEvergroveGameInstance|GetPendingSlot :self instance))
   (Variables|Default|SetTravelRestoring true)
   (bind restored (Class|BPPlayer|RestorePlayerSave :self hero :Snapshot (Class|BPEvergroveGameInstance|GetTravelSnapshot :self instance)))
   (Variables|Default|SetTravelRestoring false)
   (if restored
    (Class|BPEvergroveGameInstance|SetTravelPending :self instance :TravelPending false)
    (Class|BPEvergroveGameInstance|SetTravelSnapshot :self instance))) (:CastFailed)))) (:CastFailed)))'''
graph(W,'ResumeMapTravel',code);call('compile_blueprint',{'blueprint':ref(W),'warnings_as_errors':True});call('save_assets',{'asset_paths':[W]},ASSET)
