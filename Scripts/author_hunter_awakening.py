from build_companion_combat import *
O='/Game/Game/UI/BP_EvergroveOpeningHUD.BP_EvergroveOpeningHUD'
W='/Game/Game/World/BP_WoodlandWorld.BP_WoodlandWorld'
graph(PLAYER,'SetOpeningPose','''(fn SetOpeningPose (Amount)
 (Transformation|SetRelativeRotation :self (Variables|Character|GetSprite) :NewRotation (Math|Rotator|MakeRotator :Roll 0.0 :Pitch (* Amount 90.0) :Yaw 0.0) :bSweep false :bTeleport true)
 (Transformation|SetRelativeLocation :self (Variables|Character|GetSprite) :NewLocation (Math|Vector|MakeVector 0.0 0.0 (* Amount -60.0)) :bSweep false :bTeleport true))''',[('Amount','float',None)])
graph(O,'PosePlayer','''(fn PosePlayer (Amount)
 (bind player (Utilities|Casting|CastToBP_Player :Object (Game|GetPlayerCharacter 0))
  (:then (Class|BPPlayer|SetOpeningPose :self player :Amount Amount)) (:CastFailed)))''',[('Amount','float',None)])
code=(ROOT/'Saved/CombatAudit/PlaceWake.dsl').read_text().replace('3550.0 470.0 120.0','9200.0 1800.0 120.0')
code=code.replace('(Variables|Default|SetWakePlaced true)','(Variables|Default|SetWakePlaced true) (CallFunction|PosePlayer :Amount 1.0)')
graph(O,'PlaceWake',code)
code=(ROOT/'Saved/CombatAudit/UpdateSequence.dsl').read_text().replace('(CallFunction|LockWakeInput)','(CallFunction|LockWakeInput)\n (if (Variables|Default|GetWakePlaced) (CallFunction|PosePlayer :Amount (- 1.0 (Math|Float|Clamp(Float) (/ (- (Variables|Default|GetAge) 7.0) 2.0) 0.0 1.0))))')
code=code.replace("(/ (Variables|Default|GetAge) 10.0)","(/ (Variables|Default|GetAge) 20.0)").replace('12.0','26.0')
graph(O,'UpdateSequence',code,[('Delta','float',None)])
code=(ROOT/'Saved/CombatAudit/FinishWake.dsl').read_text().replace('(Variables|Default|SetFinished true)','(Variables|Default|SetFinished true) (CallFunction|PosePlayer :Amount 0.0)')
graph(O,'FinishWake',code)
v=lambda n:'(Variables|Default|Get'+n+')'
dream=[(.8,4.2,'Oh, child of life...',''),(4.5,8.0,'You who bear a burden','without a name.'),(8.3,11.8,'Wake, and walk this world.',''),(12.1,16.1,'Where life has withered,','may it flourish in your footsteps.'),(16.4,20.0,'When you remember what was lost...',''),(20.3,24.5,'Find me at the end of the worldline.',''),(24.8,28.8,'I will be waiting.','')]
wake=[(1.5,6.0,'Hey... can you hear me?','Rein, a hunter from Evergrove.'),(6.2,10.0,'Easy. I found you lying here, out cold.',"Don't try to stand too quickly."),(10.2,14.0,'Where... am I?',"I can't remember... anything."),(14.2,18.0,'These woods can turn you around.','Look for the old wooden trail markers.'),(18.2,22.0,'My village is beyond the western trail.','Explore carefully. There are a few dead ends.'),(22.2,25.6,'Find your way out of the forest.','Reach the village of Evergrove.')]
code='(fn EvaluateCaption ()\n(Variables|Default|SetCaption "") (Variables|Default|SetCaptionSecond "") (Variables|Default|SetCaptionAlpha 0.0)\n'
for phase,lines in [(0,dream),(1,wake)]:
 for start,end,a,b in lines:
  code+=f'(if (and (== {v("Phase")} {phase}) (and (>= {v("Age")} {start}) (< {v("Age")} {end}))) (Variables|Default|SetCaption {json.dumps(a)}) (Variables|Default|SetCaptionSecond {json.dumps(b)}) (Variables|Default|SetCaptionStart {start}) (Variables|Default|SetCaptionEnd {end}) (Variables|Default|SetCaptionAlpha (Math|Float|Clamp(Float) (Math|Float|Min(Float) (/ (- {v("Age")} {start}) 0.55) (/ (- {end} {v("Age")}) 0.55)) 0.0 1.0)))\n'
graph(O,'EvaluateCaption',code+')')
code=(ROOT/'Saved/CombatAudit/UpdateCamera.dsl').read_text().replace('-3950.0 4300.0','-3950.0 10300.0')
graph(W,'UpdateCamera',code,[('Delta','float',None)])
for bp in [PLAYER,O,W]:call('compile_blueprint',{'blueprint':ref(bp),'warnings_as_errors':True})
call('save_assets',{'asset_paths':[PLAYER,O,W]},ASSET)
print('HUNTER_AWAKENING_AND_PRONE_POSE_SAVED',flush=True)
