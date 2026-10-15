"""Connect the new map to quests and enforce its safe guild boundary."""
from build_woodland_blockout import *

def author():
    graph(DIRECTOR,'IsInSafeHub',f'''(fn IsInSafeHub ()
 (for actor (Actor|GetAllActorsOfClass :ActorClass "{WORLD}_C")
  (bind world (Utilities|Casting|CastToBP_WoodlandWorld :Object actor)
   (:then (bind safe (Class|BPWoodlandWorld|IsHubLocation :self world :Location (Transformation|GetActorLocation :self (Variables|Default|GetPlayer)))) (return safe)) (:CastFailed)))
 (return false))''',outputs=[('Safe','bool',None)])
    for name,ins,outs in [('FindEnemy',[('Range','float',None)],[('Enemy',ENEMY+'_C',None)]),('RefreshEncounter',[],[]),('EnemyStep',[('Enemy',ENEMY+'_C',None)],[])]:
        checkpoint=q.AUDIT/(name+'_pre_woodland.dsl')
        if not checkpoint.exists():checkpoint.write_text((q.AUDIT/(name+'.dsl')).read_text())
        code=checkpoint.read_text()
        if name=='FindEnemy':
            code=code.replace('(Variables|Default|SetTarget)', '(Variables|Default|SetTarget) (if (CallFunction|IsInSafeHub) (return (Variables|Default|GetTarget)))',1)
        elif name=='RefreshEncounter':
            code=code.replace('(fn RefreshEncounter ()','''(fn RefreshEncounter ()
 (if (CallFunction|IsInSafeHub) (Variables|Default|SetInCombat false) (Variables|Default|SetTarget) (return))''',1)
        else:
            code=code.replace('(fn EnemyStep (Enemy)','''(fn EnemyStep (Enemy)
 (if (CallFunction|IsInSafeHub) (Class|BPQuestEnemy|SetWindingUp :self Enemy :WindingUp false) (return))''',1)
        graph(DIRECTOR,name,code,ins,outs)
    source=(ROOT/'Saved/QuestBankAudit/SpawnQuestObjectives.dsl').read_text()
    prefix=f'''(for actor (Actor|GetAllActorsOfClass :ActorClass "{WORLD}_C")
 (bind world (Utilities|Casting|CastToBP_WoodlandWorld :Object actor)
  (:then (bind spawned (Class|BPWoodlandWorld|SpawnTrailObjectives :self world :Player Player :QuestID QuestID :Kind Kind :TargetType TargetType :Required Required)) (return spawned)) (:CastFailed)))
'''
    source=source.replace('(fn SpawnQuestObjectives (Player QuestID Kind TargetType Required)', '(fn SpawnQuestObjectives (Player QuestID Kind TargetType Required)\n'+prefix,1)
    graph(PLAYER,'SpawnQuestObjectives',source,[('Player',PLAYER+'_C',None),('QuestID','name',None),('Kind','name',None),('TargetType','name',None),('Required','int',None)],[('Spawned','int',None)])
    call('save_assets',{'asset_paths':[PLAYER,DIRECTOR,WORLD,LEVEL]},ASSET)

if __name__=='__main__':author()
