"""Author the woodland clock, sun/moon lighting, and lantern pools."""
from build_companion_combat import *
from woodland_lighting_settings import TRAIL_LANTERNS
WORLD='/Game/Game/World/BP_WoodlandWorld.BP_WoodlandWorld'
OUT=ROOT/'Saved/DayNightAudit'; OUT.mkdir(exist_ok=True)
for function_name in ['CreateLanternLights','ApplyDayNight','UpdateInteriorLighting']:
    q.BANK=WORLD; q.function(function_name, [], [])
for n,t in [('TimeOfDayMinutes','float'),('DayNumber','int'),('RealSecondsPerDay','float'),('ClockPaused','bool'),('Daylight','float'),('DayProgress','float'),('ClockHour','int'),('ClockMinute','int'),('IsNight','bool'),('ClockSun','/Script/Engine.DirectionalLight'),('ClockSky','/Script/Engine.SkyLight')]:var(WORLD,n,t)
var(WORLD,'NightLightFactor','float');var(WORLD,'InteriorLightingActive','bool');var(WORLD,'ExteriorLightScale','float')
for n in ['TimeOfDayMinutes','DayNumber','RealSecondsPerDay','ClockPaused','ExteriorLightScale']:
    call('set_variable_instance_editable',{'blueprint':ref(WORLD),'variable_name':n,'instance_editable':True})
graph(WORLD,'AdvanceWorldClock','''(fn AdvanceWorldClock (Delta)
 (if (not (Variables|Default|GetClockPaused))
  (bind total (+ (Variables|Default|GetTimeOfDayMinutes) (/ (* (Math|Float|Max(Float) Delta 0.0) 1440.0) (Math|Float|Max(Float) (Variables|Default|GetRealSecondsPerDay) 1.0))))
  (bind days (Math|Float|Floor (/ total 1440.0)))
  (Variables|Default|SetDayNumber (+ (Variables|Default|GetDayNumber) days))
  (Variables|Default|SetTimeOfDayMinutes (- total (* days 1440.0))))
 (Variables|Default|SetDayProgress (/ (Variables|Default|GetTimeOfDayMinutes) 1440.0))
 (Variables|Default|SetClockHour (Math|Float|Floor (/ (Variables|Default|GetTimeOfDayMinutes) 60.0)))
 (Variables|Default|SetClockMinute (Math|Float|Floor (- (Variables|Default|GetTimeOfDayMinutes) (* (Variables|Default|GetClockHour) 60.0))))
 (Variables|Default|SetIsNight (or (< (Variables|Default|GetTimeOfDayMinutes) 360.0) (>= (Variables|Default|GetTimeOfDayMinutes) 1080.0)))
 (Variables|Default|SetDaylight (Math|Float|Clamp(Float) (* (Math|Trig|Sin(Degrees) (* (- (Variables|Default|GetTimeOfDayMinutes) 360.0) 0.25)) 1.5) 0.0 1.0))
 (Variables|Default|SetNightLightFactor (Math|Float|Clamp(Float) (select (< (Variables|Default|GetTimeOfDayMinutes) 720.0) (/ (- 420.0 (Variables|Default|GetTimeOfDayMinutes)) 120.0) (/ (- (Variables|Default|GetTimeOfDayMinutes) 960.0) 180.0)) 0.0 1.0)))''',[('Delta','float',None)])
graph(WORLD,'UpdateInteriorLighting','''(fn UpdateInteriorLighting ()
 (Variables|Default|SetInteriorLightingActive false)
 (bind player (Game|GetPlayerCharacter 0))
 (if (CallFunction|Valid :Object player)
  (for zone (Actor|GetAllActorswithTag :Tag "StableInteriorLighting")
   (bind (origin extent) (Collision|GetActorBounds :self zone :bOnlyCollidingComponents false))
   (if (Math|Geometry|IsPointinBox :Point (Transformation|GetActorLocation :self player) :BoxOrigin origin :BoxExtent extent)
    (Variables|Default|SetInteriorLightingActive true)))))''')
graph(WORLD,'InitializeDayNight','''(fn InitializeDayNight ()
 (for sun (Actor|GetAllActorsOfClass :ActorClass "/Script/Engine.DirectionalLight")
  (bind light (Utilities|Casting|CastToDirectionalLight :Object sun) (:then (Variables|Default|SetClockSun light)) (:CastFailed)))
 (for sky (Actor|GetAllActorsOfClass :ActorClass "/Script/Engine.SkyLight")
  (bind light (Utilities|Casting|CastToSkyLight :Object sky) (:then (Variables|Default|SetClockSky light)) (:CastFailed)))
 (CallFunction|CreateLanternLights)
 (CallFunction|AdvanceWorldClock :Delta 0.0)
 (CallFunction|ApplyDayNight))''')
code='(fn CreateLanternLights ()\n'
sources=[(x,y,216) for x,y in TRAIL_LANTERNS]
for side in [-1,1]:
    sources += [(side*805,-640,z) for z in [225,535,805]]
    sources += [(side*550,-615,z) for z in [225,510]]
for index,(x,y,z) in enumerate(sources):
    code+=f'''(bind lamp{index} (AddComponent|Common|AddPointLightComponent :RelativeTransform (Math|Transform|MakeTransform :Location (Math|Vector|MakeVector {float(x)} {float(y)} {float(z)}))))
 (Rendering|Components|Light|SetLightColor :self lamp{index} :NewLightColor (Math|Color|MakeColor 1.0 0.7 0.38 1.0) :bSRGB false)
 (Rendering|Components|Light|SetIntensityUnits :self lamp{index} :NewIntensityUnits "Lumens")
 (Rendering|Components|Light|SetIntensity :self lamp{index} :NewIntensity 600.0)
 (Rendering|Lighting|SetAttenuationRadius :self lamp{index} :NewRadius {550.0 if index<5 else 240.0})
 (Rendering|Lighting|SetSourceRadius :self lamp{index} :bNewValue 6.0)
 (Rendering|Components|Light|SetCastShadows :self lamp{index} :bNewValue false)
'''
graph(WORLD,'CreateLanternLights',code+')')
graph(WORLD,'ApplyDayNight','''(fn ApplyDayNight ()
 (CallFunction|UpdateInteriorLighting)
 (bind inside (Variables|Default|GetInteriorLightingActive))
 (bind d (select inside 1.0 (Variables|Default|GetDaylight)))
 (Rendering|Material|SetScalarParameterValue :Collection "/Game/Environment/DayNight/MPC_WorldClock.MPC_WorldClock" :ParameterName "NightGlow" :ParameterValue (* (Variables|Default|GetNightLightFactor) 8.0))
 (Rendering|Material|SetScalarParameterValue :Collection "/Game/Environment/DayNight/MPC_WorldClock.MPC_WorldClock" :ParameterName "NightBrightness" :ParameterValue (+ 0.3 (* d 0.7)))
 (if (CallFunction|Valid :Object (Variables|Default|GetClockSun))
  (bind sun (Class|Light|GetLightComponent :self (Variables|Default|GetClockSun)))
  (Rendering|Components|Light|SetIntensity :self sun :NewIntensity (+ 2.0 (* d 3.0)))
  (bind daycolor (Math|Color|Lerp(LinearColor) :A (Math|Color|MakeColor 1.0 0.38 0.12 1.0) :B (Math|Color|MakeColor 1.0 0.95 0.82 1.0) :Alpha d))
  (Rendering|Components|Light|SetLightColor :self sun :NewLightColor (Math|Color|Lerp(LinearColor) :A (Math|Color|MakeColor 0.4 0.55 0.85 1.0) :B daycolor :Alpha (Math|Float|Clamp(Float) (* d 4.0) 0.0 1.0)) :bSRGB false)
  (Transformation|SetActorRotation :self (Variables|Default|GetClockSun) :NewRotation (Math|Rotator|MakeRotator :Pitch (select inside -70.0 (- 0.0 (+ 12.0 (* (Math|Float|Absolute(Float) (Math|Trig|Sin(Degrees) (* (- (Variables|Default|GetTimeOfDayMinutes) 360.0) 0.25))) 58.0)))) :Yaw (select (and (not inside) (Variables|Default|GetIsNight)) 145.0 -35.0)) :bTeleportPhysics true))
 (if (CallFunction|Valid :Object (Variables|Default|GetClockSky))
  (bind sky (Class|SkyLight|GetLightComponent :self (Variables|Default|GetClockSky)))
  (Rendering|Components|SkyLight|SetIntensity :self sky :NewIntensity 1.0)
  (Rendering|Components|SkyLight|SetLightColor :self sky :NewLightColor (Math|Color|Lerp(LinearColor) :A (Math|Color|MakeColor 0.5 0.65 1.0 1.0) :B (Math|Color|MakeColor 1.0 1.0 1.0 1.0) :Alpha d)))
 (for component (Actor|GetComponentsByClass :ComponentClass "/Script/Engine.PointLightComponent")
  (bind lamp (Utilities|Casting|CastToPointLightComponent :Object component)
   (:then (Rendering|Components|Light|SetIntensity :self lamp :NewIntensity (* (* (Variables|Default|GetNightLightFactor) (Variables|Default|GetExteriorLightScale)) (select (> (Class|LocalLightComponent|GetAttenuationRadius :self lamp) 300.0) 300.0 350.0)))) (:CastFailed))))''')
# Rewrite only the event graph, preserving existing camera and save-slot setup.
event=call('read_graph_dsl',{'graph':ref(WORLD+':EventGraph')})
before=OUT/'WorldEventGraph_before.dsl'
if not before.exists():before.write_text(event,encoding='utf-8')
graph(WORLD,'EventGraph','''(event EventBeginPlay
 (for actor (Actor|GetAllActorsOfClass :ActorClass "/Script/Engine.CameraActor")
  (bind camera (Utilities|Casting|CastToCameraActor :Object actor)
   (:then (Variables|Default|SetFollowCamera camera)) (:CastFailed)))
 (Game|Player|SetViewTargetwithBlend :self (Game|GetPlayerController 0) :NewViewTarget (Variables|Default|GetFollowCamera) :BlendTime 0.0)
 (CallFunction|InitializeDayNight)
 (bind player (Utilities|Casting|CastToBP_Player :Object (Game|GetPlayerCharacter 0))
  (:then (Class|BPPlayer|SetSaveSlotName :self player :SaveSlotName "AdventureRPG_WoodlandBlockout")) (:CastFailed))
 )
 (event EventTick (DeltaSeconds)
  (CallFunction|AdvanceWorldClock :Delta DeltaSeconds)
  (CallFunction|ApplyDayNight)
  (CallFunction|UpdateCamera :Delta DeltaSeconds))''')
defaults(WORLD,{'TimeOfDayMinutes':480,'DayNumber':1,'RealSecondsPerDay':1200,'ClockPaused':False,'ExteriorLightScale':1})
for actor in call('find_actors',{'name':'','tag':'','collision_channels':[],'actor_type':ref(WORLD+'_C')},SCENE):
    call('set_properties',{'instance':actor,'values':json.dumps({'TimeOfDayMinutes':480,'DayNumber':1,'RealSecondsPerDay':1200,'ClockPaused':False,'ExteriorLightScale':1})},OBJ)
call('save_assets',{'asset_paths':[]},ASSET)
print('DAY_NIGHT_AUTHORED',flush=True)


