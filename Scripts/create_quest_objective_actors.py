import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import quest_bank_mcp as q
call=q.call;BANK=q.BANK;PLAYER=q.PLAYER
ASSET='editor_toolset.toolsets.asset.AssetTools';OBJ='editor_toolset.toolsets.object.ObjectTools'
folder='/Game/Game/Quests/Objectives';call('create_folder',{'path':folder},ASSET)
parent='/Game/Game/Characters/Player/Blueprints/BP_TestInteractable.BP_TestInteractable_C'
ENEMY=folder+'/BP_QuestEnemy.BP_QuestEnemy';PICKUP=folder+'/BP_QuestPickup.BP_QuestPickup'
for path in [ENEMY,PICKUP]:
 if not call('exists',{'path':path.split('.')[0]},ASSET):call('create',{'folder_path':folder,'asset_name':path.split('.')[-1],'asset_type':{'refPath':parent}})
 names=call('list_variables',{'blueprint':{'refPath':path}})
 for name,typ in [('ObjectiveTargetType','name'),('SpawnQuestID','name'),('Used','bool')]+([('Health','float'),('MaximumHealth','float')] if path==ENEMY else []):
  if name not in names:call('add_variable',{'blueprint':{'refPath':path},'name':name,'type_name':typ})
  if name in ['ObjectiveTargetType','MaximumHealth']:call('set_variable_instance_editable',{'blueprint':{'refPath':path},'variable_name':name,'instance_editable':True})
 if 'QuestOwner' not in names:call('add_object_variable',{'blueprint':{'refPath':path},'name':'QuestOwner','object_class':{'refPath':PLAYER+'_C'}})
 call('compile_blueprint',{'blueprint':{'refPath':path},'warnings_as_errors':True})
 cdo={'refPath':path.rsplit('.',1)[0]+'.Default__'+path.rsplit('.',1)[1]+'_C'}
 values={'ObjectiveTargetType':'ForestSlime' if path==ENEMY else 'MintCuttings'}
 if path==ENEMY:values.update({'MaximumHealth':3.0,'Health':3.0})
 call('set_properties',{'instance':cdo,'values':json.dumps(values)},OBJ)
q.BANK=ENEMY
f=q.function('TakeQuestDamage',[('Player',PLAYER+'_C',None),('Damage','float',None)],[('Killed','bool',None)])
q.write(f,'''(fn TakeQuestDamage (Player Damage)
 (Utilities|IsValid Player
  (:"Is Valid"
   (if (and (not (Variables|Default|GetUsed)) (> Damage 0.0))
    (Variables|Default|SetHealth (- (Variables|Default|GetHealth) Damage))
    (if (<= (Variables|Default|GetHealth) 0.0)
     (Variables|Default|SetUsed true)
     (bind bank (Class|BPPlayer|GetQuestBank Player))
     (Utilities|IsValid bank
      (:"Is Valid" (bind updated (Class|BPQuestBank|ReportObjectiveProgress :self bank :Player Player :Kind "Combat" :TargetType (Variables|Default|GetObjectiveTargetType) :Amount 1)) (Actor|DestroyActor) (return true))
      (:"Is Not Valid" (Actor|DestroyActor) (return true)))
     (else (return false)))
    (else (return false))))
  (:"Is Not Valid" (return false))))''')
q.write({'refPath':ENEMY+':EventGraph'},'''(event EventBeginPlay
 (Variables|Default|SetHealth (Variables|Default|GetMaximumHealth))
 (Components|StaticMesh|SetStaticMesh :self (Variables|Default|GetCubeMesh) :NewMesh "/Engine/BasicShapes/Sphere.Sphere")
 (Collision|SetCollisionResponsetoChannel :self (Variables|Default|GetCubeMesh) :Channel "ECC_GameTraceChannel1" :NewResponse "ECR_Block"))
(event EventInteract
 (bind player (Utilities|Casting|CastToBP_Player :Object (Game|GetPlayerCharacter 0))
  (:then (bind killed (CallFunction|TakeQuestDamage :Player player :Damage 1.0)))
  (:CastFailed)))
(event Game|Damage|EventAnyDamage (Damage DamageType InstigatedBy DamageCauser)
 (bind player (Utilities|Casting|CastToBP_Player :Object DamageCauser)
  (:then (bind killed (CallFunction|TakeQuestDamage :Player player :Damage Damage)))
  (:CastFailed)))''')
q.BANK=PICKUP
f=q.function('CollectForPlayer',[('Player',PLAYER+'_C',None)],[('Collected','bool',None)])
q.write(f,'''(fn CollectForPlayer (Player)
 (Utilities|IsValid Player
  (:"Is Valid"
   (if (not (Variables|Default|GetUsed))
    (bind bank (Class|BPPlayer|GetQuestBank Player))
    (Utilities|IsValid bank
     (:"Is Valid"
      (Variables|Default|SetUsed true)
      (bind updated (Class|BPQuestBank|ReportObjectiveProgress :self bank :Player Player :Kind "Collection" :TargetType (Variables|Default|GetObjectiveTargetType) :Amount 1))
      (if (> updated 0)
       (Actor|DestroyActor)
       (return true)
       (else (Variables|Default|SetUsed false) (return false))))
     (:"Is Not Valid" (return false)))
    (else (return false))))
  (:"Is Not Valid" (return false))))''')
q.write({'refPath':PICKUP+':EventGraph'},'''(event EventBeginPlay
 (Collision|SetCollisionResponsetoChannel :self (Variables|Default|GetCubeMesh) :Channel "ECC_GameTraceChannel1" :NewResponse "ECR_Block"))
(event EventInteract
 (bind player (Utilities|Casting|CastToBP_Player :Object (Game|GetPlayerCharacter 0))
  (:then (bind collected (CallFunction|CollectForPlayer :Player player)))
  (:CastFailed)))''')
print('Actor assets saved',call('save_assets',{'asset_paths':[ENEMY,PICKUP]},ASSET))
