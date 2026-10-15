"""Temporary, stationary enemy windup for visual QA; no player save writes."""
from build_woodland_blockout import *
T='/Game/Tests/World/BP_EnemyReadabilityPreview.BP_EnemyReadabilityPreview'
create(T,'/Script/Engine.Actor')
graph(T,'EventGraph',f'''(event EventBeginPlay
 (Utilities|FlowControl|Delay 1.0)
 (bind enemy (Game|SpawnActorfromClass :Class "{ENEMY}_C" :SpawnTransform (Math|Transform|MakeTransform :Location (Math|Vector|MakeVector 2300.0 0.0 100.0) :Scale (Math|Vector|MakeVector 0.5 0.5 0.5)) :CollisionHandlingOverride "AlwaysSpawn"))
 (Class|BPQuestEnemy|SetHealth :self enemy :Health 100.0)
 (Class|BPQuestEnemy|SetMaximumHealth :self enemy :MaximumHealth 100.0)
 (Class|BPQuestEnemy|SetWindingUp :self enemy :WindingUp true)
 (Class|BPQuestEnemy|SetAttackAt :self enemy :AttackAt 999999.0)
 (Utilities|FlowControl|Delay 3.0)
 (Development|ExecuteConsoleCommand :Command "Shot showui" :SpecificPlayer (Game|GetPlayerController 0))
 (Utilities|FlowControl|Delay 1.0)
 (bind player (Utilities|Casting|CastToBP_Player :Object (Game|GetPlayerCharacter 0))
  (:then (Class|BPQuestEnemy|TakeQuestDamage :self enemy :Player player :Damage 3.0)
   (Utilities|FlowControl|Delay 0.25)
   (Development|ExecuteConsoleCommand :Command "Shot showui" :SpecificPlayer (Game|GetPlayerController 0))) (:CastFailed)))''')
a=actor(T+'_C','Woodland_TemporaryReadability',(2300,0,0))
(q.AUDIT/'readability_actor.json').write_text(json.dumps(a))
try:
    call('StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InEditorFloating','warmupSeconds':0,'startTransform':{'location':{'x':2380,'y':0,'z':110},'rotation':{'pitch':0,'yaw':180,'roll':0},'scale':{'x':1,'y':1,'z':1}}}},'EditorToolset.EditorAppToolset')
except RuntimeError as e:
    if 'PIE ended before warmup' not in str(e):raise
