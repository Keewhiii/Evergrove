"""Beast interaction, readable prototype HUD and save integration."""
from build_companion_combat import *
def beasts():
    var(BEAST,'Label','/Script/Engine.TextRenderComponent')
    graph(BEAST,'StartRegrow','''(fn StartRegrow ()
 (Utilities|Time|SetTimerbyFunctionName :Object self :FunctionName "Regrow" :Time 25.0 :bLooping false))''')
    graph(BEAST,'Regrow','''(fn Regrow ()
 (Rendering|SetActorHiddenInGame :bNewHidden false)
 (Collision|SetActorEnableCollision :bNewActorEnableCollision true))''')
    graph(BEAST,'UpdateLabel','''(fn UpdateLabel ()
 (Utilities|IsValid (Variables|Default|GetLabel)
  (:"Is Valid"
   (Rendering|Components|TextRender|SetText :self (Variables|Default|GetLabel) :Value
    (Utilities|Text|ToText(String) (select (Variables|Default|GetIsFood) "Beast treat [E]" (Utilities|String|Append (Utilities|String|ToString(Name) (Variables|Default|GetBeastID)) (select (Variables|Default|GetIsCompanion) " (companion)" " [E]")))))
   (Transformation|SetWorldRotation :self (Variables|Default|GetLabel) :NewRotation (Math|Rotator|FindLookatRotation :Start (Transformation|GetActorLocation) :Target (Camera|GetCameraLocation :self (Game|GetPlayerCameraManager 0)))))
  (:"Is Not Valid")))''')
    graph(BEAST,'EventGraph',f'''(event EventBeginPlay
 (Collision|SetCollisionResponseToAllChannels :self (Variables|Default|GetCubeMesh) :NewResponse "ECR_Ignore")
 (Collision|SetCollisionResponseToChannel :self (Variables|Default|GetCubeMesh) :Channel "ECC_GameTraceChannel1" :NewResponse "ECR_Block")
 (Utilities|FlowControl|Delay 0.1)
 (if (not (Variables|Default|GetIsFood))
  (Components|StaticMesh|SetStaticMesh :self (Variables|Default|GetCubeMesh) :NewMesh "/Engine/BasicShapes/Sphere.Sphere"))
 (bind label (AddComponent|Rendering|AddTextRenderComponent :RelativeTransform (Math|Transform|MakeTransform :Location (Math|Vector|MakeVector 0.0 0.0 90.0))))
 (Variables|Default|SetLabel label)
 (Utilities|Time|SetTimerbyFunctionName :Object self :FunctionName "UpdateLabel" :Time 0.3 :bLooping true))
 (event EventInteract
  (for actor (Actor|GetAllActorsOfClass :ActorClass "{DIRECTOR}_C")
   (bind director (Utilities|Casting|CastToBP_CompanionCombat :Object actor)
    (:then (Class|BPCompanionCombat|MeetBeast :self director :Beast self)) (:CastFailed))))''')
    call('save_assets',{'asset_paths':[BEAST]},ASSET)
def hud():
    for name in ['HealthLine','RosterLine']:var(DIRECTOR,name,'string')
    graph(DIRECTOR,'RefreshHUD','''(fn RefreshHUD ()
 (Variables|Default|SetHealthLine (Utilities|String|Append "Health " (Utilities|String|ToString(Float) (Variables|Default|GetPlayerHealth))))
 (Variables|Default|SetHealthLine (Utilities|String|Append (Variables|Default|GetHealthLine) (Utilities|String|Append " / 100   Companion " (Utilities|String|ToString(Float) (Variables|Default|GetCompanionHealth)))))
 (Variables|Default|SetHealthLine (Utilities|String|Append (Variables|Default|GetHealthLine) " / 60"))
 (Variables|Default|SetRosterLine "Roster (max 3): ")
 (for id (Variables|Default|GetRoster)
  (Variables|Default|SetRosterLine (Utilities|String|Append (Variables|Default|GetRosterLine) (Utilities|String|Append (Utilities|String|ToString(Name) id) "   ")))))''')
    graph(HUD,'EventGraph',f'''(event EventReceiveDrawHUD (SizeX SizeY)
 (for actor (Actor|GetAllActorsOfClass :ActorClass "{DIRECTOR}_C")
  (bind director (Utilities|Casting|CastToBP_CompanionCombat :Object actor)
   (:then
    (HUD|DrawRect :RectColor "(R=0.025,G=0.04,B=0.035,A=0.85)" :ScreenX 16.0 :ScreenY 16.0 :ScreenW (Math|Float|Min(Float) (- SizeX 32.0) 850.0) :ScreenH 154.0)
    (HUD|DrawText :Text (Class|BPCompanionCombat|GetHealthLine :self director) :TextColor "(R=0.95,G=0.93,B=0.8,A=1)" :ScreenX 28.0 :ScreenY 26.0 :Font "/Engine/EngineFonts/Roboto.Roboto" :Scale 0.85)
    (HUD|DrawText :Text (Class|BPCompanionCombat|GetRosterLine :self director) :TextColor "(R=0.95,G=0.93,B=0.8,A=1)" :ScreenX 28.0 :ScreenY 48.0 :Font "/Engine/EngineFonts/Roboto.Roboto" :Scale 0.85)
    (HUD|DrawText :Text (select (Class|BPCompanionCombat|GetUseSpell :self director) "LMB: frost bolt   V: switch to sword   Q: command   H: heal" "LMB: sword   V: switch to frost bolt   Q: command   H: heal") :TextColor "(R=0.75,G=0.9,B=1,A=1)" :ScreenX 28.0 :ScreenY 70.0 :Font "/Engine/EngineFonts/Roboto.Roboto" :Scale 0.85)
    (HUD|DrawText :Text "1 / 2 / 3: summon slot   Backspace: release   E: interact" :TextColor "(R=0.75,G=0.9,B=1,A=1)" :ScreenX 28.0 :ScreenY 92.0 :Font "/Engine/EngineFonts/Roboto.Roboto" :Scale 0.85)
    (if (< (Utilities|Time|GetGameTimeinSeconds) (Class|BPCompanionCombat|GetMessageUntil :self director))
     (HUD|DrawText :Text (Class|BPCompanionCombat|GetMessage :self director) :TextColor "(R=1,G=0.85,B=0.45,A=1)" :ScreenX 28.0 :ScreenY 124.0 :Font "/Engine/EngineFonts/Roboto.Roboto" :Scale 0.75)))
   (:CastFailed))))''')
    defaults(GM,{'HUDClass':{'refPath':HUD+'_C'}})
    graph(GM,'EventGraph',f'''(event EventBeginPlay
 (Game|SpawnActorfromClass :Class "{DIRECTOR}_C" :SpawnTransform (Math|Transform|MakeTransform) :CollisionHandlingOverride "AlwaysSpawn"))''')
    # Quest enemies retain their established damage function and quest reporting.
    code='''(event EventBeginPlay
 (Variables|Default|SetHealth (Variables|Default|GetMaximumHealth))
 (Components|StaticMesh|SetStaticMesh :self (Variables|Default|GetCubeMesh) :NewMesh "/Engine/BasicShapes/Sphere.Sphere")
 (Collision|SetCollisionResponseToChannel :self (Variables|Default|GetCubeMesh) :Channel "ECC_GameTraceChannel1" :NewResponse "ECR_Block"))
 (event EventInteract)
 (event Game|Damage|EventAnyDamage (Damage DamageType InstigatedBy DamageCauser)
 (bind player (Utilities|Casting|CastToBP_Player :Object DamageCauser)
  (:then (CallFunction|TakeQuestDamage :Player player :Damage Damage)) (:CastFailed)))'''
    start=code.index('(event EventInteract')
    end=code.index('(event Game|Damage|EventAnyDamage',start)
    code=code[:start]+'''(event EventInteract
 (Development|PrintString :InString "Use left mouse to attack, or let your companion help." :Duration 2.0))
\n'''+code[end:]
    graph(ENEMY,'EventGraph',code)
    call('save_assets',{'asset_paths':[HUD,GM,ENEMY,DIRECTOR]},ASSET)
    from style_combat_ui import author as style_hud
    style_hud()
def saves():
    # Preserve all existing quest/objective serialization. Version 1 saves gain
    # empty-roster/healthy defaults for the added fields.
    cap=(ROOT/'Saved/SaveGameAudit/CapturePlayerSave.dsl').read_text()
    extra=f'''(for actor (Actor|GetAllActorsOfClass :ActorClass "{DIRECTOR}_C")
 (bind director (Utilities|Casting|CastToBP_CompanionCombat :Object actor)
  (:then (Class|BPCompanionCombat|CaptureCombat :self director :Snapshot _asbp_playersave)) (:CastFailed)))\n'''
    # Readback uses generated bind names; find the actual snapshot cast binding.
    import re
    savevar=re.search(r'\(bind (\w+) \(Utilities\|Casting\|CastToBP_PlayerSave',cap).group(1)
    extra=extra.replace('_asbp_playersave',savevar)
    pos=cap.rfind('(return ')
    # The final return is the cast-failed path. Insert before the successful return.
    needle='(return '+savevar+')'
    if needle not in cap:raise RuntimeError('Snapshot return not found')
    cap=cap.replace(needle,extra+needle,1)
    q.BANK=PLAYER;q.write(ref(PLAYER+':CapturePlayerSave'),cap)
    restore=(ROOT/'Saved/SaveGameAudit/RestorePlayerSave.dsl').read_text()
    extra=f'''(for actor (Actor|GetAllActorsOfClass :ActorClass "{DIRECTOR}_C")
 (bind director (Utilities|Casting|CastToBP_CompanionCombat :Object actor)
  (:then (Class|BPCompanionCombat|RestoreCombat :self director :Snapshot Snapshot)) (:CastFailed)))\n'''
    restore=restore.replace('(return true)',extra+'(return true)')
    q.BANK=PLAYER;q.write(ref(PLAYER+':RestorePlayerSave'),restore)
    valid=(ROOT/'Saved/SaveGameAudit/ValidatePlayerSave.dsl').read_text()
    # Add early rejection after entry while retaining the original schema checks.
    at=valid.index('\n')
    extra='''
 (if (> (Utilities|Array|Length (Class|BPPlayerSave|GetSummonRoster :self Snapshot)) 3) (return false))
 (if (or (< (Class|BPPlayerSave|GetActiveSummonIndex :self Snapshot) -1) (>= (Class|BPPlayerSave|GetActiveSummonIndex :self Snapshot) (Utilities|Array|Length (Class|BPPlayerSave|GetSummonRoster :self Snapshot)))) (return false))
 (if (or (<= (Class|BPPlayerSave|GetCombatPlayerHealth :self Snapshot) 0.0) (> (Class|BPPlayerSave|GetCombatPlayerHealth :self Snapshot) 100.0)) (return false))
 (if (or (< (Class|BPPlayerSave|GetCombatCompanionHealth :self Snapshot) 0.0) (> (Class|BPPlayerSave|GetCombatCompanionHealth :self Snapshot) 60.0)) (return false))
 (for id (Class|BPPlayerSave|GetSummonRoster :self Snapshot)
  (if (not (or (or (== id (Utilities|Name|MakeLiteralName "Mossling")) (== id (Utilities|Name|MakeLiteralName "Emberfox"))) (or (== id (Utilities|Name|MakeLiteralName "Rivercub")) (== id (Utilities|Name|MakeLiteralName "Moonmoth"))))) (return false)))
'''
    # Snapshot validity must be established before inspecting its fields.
    marker='(:"Is Valid"'
    if marker not in valid:raise RuntimeError('Snapshot validity branch not found')
    valid=valid.replace(marker,marker+extra,1)
    q.BANK=PLAYER;q.write(ref(PLAYER+':ValidatePlayerSave'),valid)
    call('save_assets',{'asset_paths':[PLAYER,SAVE]},ASSET)
if __name__=='__main__':
    if 'beasts' in sys.argv:beasts()
    elif 'hud' in sys.argv:hud()
    elif 'saves' in sys.argv:saves()
    else:beasts();hud();saves()
