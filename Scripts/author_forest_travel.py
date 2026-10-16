from build_companion_combat import *
GI='/Game/Game/UI/BP_EvergroveGameInstance.BP_EvergroveGameInstance';W='/Game/Game/World/BP_WoodlandWorld.BP_WoodlandWorld';O='/Game/Game/UI/BP_EvergroveOpeningHUD.BP_EvergroveOpeningHUD';M='/Game/Game/UI/BP_EvergroveIntroHUD.BP_EvergroveIntroHUD'
P='/Game/Game/World/BP_MapPassage.BP_MapPassage'
create(P,'/Script/Engine.Actor')
var(GI,'TravelSnapshot',SAVE+'_C');var(GI,'TravelPending','bool')
for n,t in [('DestinationMap','string'),('DestinationLabel','string'),('DestinationLocation','Vector'),('Radius','float'),('Age','float'),('TravelDone','bool'),('Requested','bool')]:
 var(P,n,t);call('set_variable_instance_editable',{'blueprint':ref(P),'variable_name':n,'instance_editable':True})
graph(P,'Travel','''(fn Travel ()
 (if (Variables|Default|GetTravelDone) (return))
 (bind hero (Utilities|Casting|CastToBP_Player :Object (Game|GetPlayerCharacter 0))
 (:then
  (bind instance (Utilities|Casting|CastToBP_EvergroveGameInstance :Object (Game|GetGameInstance))
  (:then
   (Variables|Default|SetTravelDone true)
   (bind snapshot (Class|BPPlayer|CapturePlayerSave :self hero))
   (Class|BPPlayerSave|SetMapName :self snapshot :MapName (Variables|Default|GetDestinationLabel))
   (Class|BPPlayerSave|SetPlayerTransform :self snapshot :PlayerTransform (Math|Transform|MakeTransform :Location (Variables|Default|GetDestinationLocation) :Rotation (Transformation|GetActorRotation :self hero) :Scale (Transformation|GetActorScale3D :self hero)))
   (Class|BPEvergroveGameInstance|SetTravelSnapshot :self instance :TravelSnapshot snapshot)
   (Class|BPEvergroveGameInstance|SetTravelPending :self instance :TravelPending true)
   (Class|BPEvergroveGameInstance|SetPendingSlot :self instance :PendingSlot (Class|BPPlayer|GetSaveSlotName :self hero))
   (Game|OpenLevel(byName) :LevelName (Utilities|String|StringToName (Variables|Default|GetDestinationMap)) :bAbsolute true :Options "")) (:CastFailed))) (:CastFailed)))''')
graph(P,'EventGraph','''(event EventTick (DeltaSeconds)
 (Variables|Default|SetAge (+ (Variables|Default|GetAge) DeltaSeconds))
 (if (and (> (Variables|Default|GetAge) 1.0) (not (Variables|Default|GetTravelDone)))
  (if (or (Variables|Default|GetRequested) (< (Math|Vector|Distance(Vector) (Transformation|GetActorLocation :self (Game|GetPlayerCharacter 0)) (Transformation|GetActorLocation)) (Variables|Default|GetRadius))) (CallFunction|Travel))))''')
defaults(P,{'Radius':120,'Age':0,'TravelDone':False,'Requested':False})
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
graph(W,'ResumeMapTravel',code)
code=(ROOT/'Saved/CombatAudit/UpdateCamera.dsl').read_text();code=code.replace('(CallFunction|ResumeTitleSave)','(CallFunction|ResumeTitleSave)\n (CallFunction|ResumeMapTravel)')
graph(W,'UpdateCamera',code,[('Delta','float',None)])
code=(ROOT/'Saved/CombatAudit/FinishDream.dsl').read_text().replace('/Game/Maps/L_EvergroveStart','/Game/Maps/L_EvergroveForest');graph(O,'FinishDream',code)
code=(ROOT/'Saved/CombatAudit/ReadSaveSummary.dsl').read_text();needle='(Utilities|String|EqualExactly(String) (Class|BPPlayerSave|GetMapName :self snapshot) "L_EvergroveStart")'
code=code.replace(needle,'(or '+needle+' (Utilities|String|EqualExactly(String) (Class|BPPlayerSave|GetMapName :self snapshot) "L_EvergroveForest"))');graph(M,'ReadSaveSummary',code)
code=(ROOT/'Saved/CombatAudit/Setup.dsl').read_text();code=code.replace('(not (Utilities|String|EqualExactly(String) (Game|GetCurrentLevelName :bRemovePrefixString true) "L_EvergroveStart"))','(Utilities|String|EqualExactly(String) (Game|GetCurrentLevelName :bRemovePrefixString true) "L_WoodlandBlockout")');graph(DIRECTOR,'Setup',code)
# Keep canopy shade readable and consistent across the forest's ground and sprite assets.
code=(ROOT/'Saved/CombatAudit/ApplyDayNight.dsl').read_text()
code=code.replace('(bind d (select inside 1.0 (Variables|Default|GetDaylight)))','(bind d (select inside 1.0 (Variables|Default|GetDaylight)))\n (bind forest (Utilities|String|EqualExactly(String) (Game|GetCurrentLevelName :bRemovePrefixString true) "L_EvergroveForest"))')
code=code.replace('(+ 0.3 (* d 0.7))','(select forest (+ 0.34 (* d 0.44)) (+ 0.3 (* d 0.7)))').replace(':NewIntensity (+ 2.0 (* d 3.0))',':NewIntensity (* (select forest 0.48 1.0) (+ 2.0 (* d 3.0)))').replace(':NewIntensity 1.0',':NewIntensity (select forest 0.82 1.0)')
graph(W,'ApplyDayNight',code)
for bp in [P,GI,W,O,M,DIRECTOR]:call('compile_blueprint',{'blueprint':ref(bp),'warnings_as_errors':True})
call('save_assets',{'asset_paths':[P,GI,W,O,M,DIRECTOR]},ASSET)
print('SEPARATE_FOREST_TRAVEL_AND_SHADE_AUTHORED',flush=True)
