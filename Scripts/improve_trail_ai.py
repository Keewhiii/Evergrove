"""Path following, enemy leashes and readable attack feedback, authored in UE."""
from build_woodland_blockout import *
from style_companion_prototype import material
NAV='/Game/Game/World/BP_TrailNavigator.BP_TrailNavigator'
FX='/Game/Game/Combat/BP_CombatHitFX.BP_CombatHitFX'
NOW='(Utilities|Time|GetGameTimeinSeconds)'
G=lambda n:f'(Variables|Default|Get{n})'

def navigation():
    create(NAV,'/Script/Engine.ActorComponent')
    graph(NAV,'Valid','''(fn Valid (Object) (Utilities|IsValid Object (:"Is Valid" (return true)) (:"Is Not Valid" (return false))))''',[('Object','/Script/CoreUObject.Object',None)],[('IsValid','bool',None)])
    for n,t,c in [('Points','vector','ARRAY'),('NextPoint','int',None),('RepathAt','float',None),('LastGoal','vector',None)]:var(NAV,n,t,c)
    graph(NAV,'Advance','''(fn Advance (Mover Destination StopAt Speed)
 (bind current (Transformation|GetActorLocation :self Mover))
 (bind goal (Math|Vector|MakeVector (.x Destination) (.y Destination) (.z current)))
 (if (== (Utilities|Array|Length (Actor|GetAllActorsOfClass :ActorClass "/Script/NavigationSystem.NavMeshBoundsVolume")) 0)
  (if (> (Math|Vector|VectorLength (- goal current)) StopAt)
   (bind next (Math|Interpolation|VInterptoConstant :Current current :Target goal :DeltaTime 0.2 :InterpSpeed Speed))
   (bind (hit blocked) (Collision|SphereTraceByChannel :Start current :End next :Radius 30.0 :TraceChannel "TraceTypeQuery1" :ActorsToIgnore (Utilities|Array|MakeArray Mover)))
   (if (not blocked) (Transformation|SetActorLocation :self Mover :NewLocation next :bSweep true)))
  (return))
 (if (or (>= (Utilities|Time|GetGameTimeinSeconds) (Variables|Default|GetRepathAt)) (> (Math|Vector|VectorLength (- goal (Variables|Default|GetLastGoal))) 140.0))
  (Variables|Default|SetRepathAt (+ (Utilities|Time|GetGameTimeinSeconds) 0.8))
  (Variables|Default|SetLastGoal goal)
  (Utilities|Array|Clear (Variables|Default|GetPoints))
  (Variables|Default|SetNextPoint 1)
  (bind path (AI|Navigation|FindPathtoLocationSynchronously :PathStart current :PathEnd goal :PathfindingContext Mover))
  (if (CallFunction|Valid :Object path) (if (AI|Navigation|IsValid :self path)
   (if (not (AI|Navigation|IsPartial :self path))
    (Variables|Default|SetPoints (Class|NavigationPath|GetPathPoints :self path))))))
 (if (< (Utilities|Array|Length (Variables|Default|GetPoints)) 2) (return))
 (if (>= (Variables|Default|GetNextPoint) (Utilities|Array|Length (Variables|Default|GetPoints))) (return))
 (bind point (Utilities|Array|Get(acopy) (Variables|Default|GetPoints) (Variables|Default|GetNextPoint)))
 (bind flatPoint (Math|Vector|MakeVector (.x point) (.y point) (.z current)))
 (bind final (== (Variables|Default|GetNextPoint) (- (Utilities|Array|Length (Variables|Default|GetPoints)) 1)))
 (if (and final (<= (Math|Vector|VectorLength (- goal current)) StopAt)) (return))
 (if (and (not final) (< (Math|Vector|VectorLength (- flatPoint current)) 30.0))
  (Variables|Default|SetNextPoint (+ (Variables|Default|GetNextPoint) 1)) (return))
 (Transformation|SetActorLocation :self Mover :NewLocation (Math|Interpolation|VInterptoConstant :Current current :Target flatPoint :DeltaTime 0.2 :InterpSpeed Speed) :bSweep true))''',[('Mover','/Script/Engine.Actor',None),('Destination','vector',None),('StopAt','float',None),('Speed','float',None)])
    graph(DIRECTOR,'MoveToPoint',f'''(fn MoveToPoint (Mover Destination StopAt Speed)
 (bind component (Actor|GetComponentbyClass :self Mover :ComponentClass "{NAV}_C"))
 (if (CallFunction|Valid :Object component)
  (bind navigator (Utilities|Casting|CastToBP_TrailNavigator :Object component)
   (:then (Class|BPTrailNavigator|Advance :self navigator :Mover Mover :Destination Destination :StopAt StopAt :Speed Speed)) (:CastFailed))
  (else
   (bind created (Game|AddComponentbyClass :self Mover :Class "{NAV}_C"))
   (bind navigator (Utilities|Casting|CastToBP_TrailNavigator :Object created)
    (:then (Class|BPTrailNavigator|Advance :self navigator :Mover Mover :Destination Destination :StopAt StopAt :Speed Speed)) (:CastFailed)))))''',[('Mover','/Script/Engine.Actor',None),('Destination','vector',None),('StopAt','float',None),('Speed','float',None)])
    backup(DIRECTOR,'MoveToward')
    graph(DIRECTOR,'MoveToward','''(fn MoveToward (Mover Goal StopAt Speed)
 (CallFunction|MoveToPoint :Mover Mover :Destination (Transformation|GetActorLocation :self Goal) :StopAt StopAt :Speed Speed))''',[('Mover','/Script/Engine.Actor',None),('Goal','/Script/Engine.Actor',None),('StopAt','float',None),('Speed','float',None)])

def enemies():
    for n,t in [('HomeLocation','vector'),('HomeInitialized','bool'),('ReturningHome','bool'),('LastObservedHealth','float'),('HitFlashUntil','float')]:var(ENEMY,n,t)
    for n,t in [('WarningMarker','/Script/Engine.StaticMeshComponent'),('HitLabel','/Script/Engine.TextRenderComponent')]:var(ENEMY,n,t)
    material('M_HitCream',(1.0,.86,.55,1))
    area='/Game/Game/Combat/M_AttackArea.M_AttackArea'
    if not call('exists',{'path':area.split('.')[0]},ASSET):
        material('M_AttackArea',(.95,.60,.12,1))
        mat='editor_toolset.toolsets.material.MaterialTools'
        opacity=call('add_expression',{'material_or_function':ref(area),'expression_class':ref('/Script/Engine.MaterialExpressionConstant')},mat)
        properties(opacity,{'R':0.3})
        call('connect_to_output',{'expression':opacity,'output_name':'','material_property':'MP_Opacity'},mat)
        properties(ref(area),{'BlendMode':'BLEND_Translucent','TwoSided':True})
        call('recompile',{'material_or_function':ref(area)},mat)
        call('save_assets',{'asset_paths':[area]},ASSET)
    graph(DIRECTOR,'InitializeEnemyHome','''(fn InitializeEnemyHome (Enemy)
 (if (Class|BPQuestEnemy|GetHomeInitialized :self Enemy) (return))
 (Class|BPQuestEnemy|SetHomeInitialized :self Enemy :HomeInitialized true)
 (Class|BPQuestEnemy|SetHomeLocation :self Enemy :HomeLocation (Transformation|GetActorLocation :self Enemy))
 (Class|BPQuestEnemy|SetLastObservedHealth :self Enemy :LastObservedHealth (Class|BPQuestEnemy|GetHealth :self Enemy)))''',[('Enemy',ENEMY+'_C',None)])
    # These components only render feedback and never block characters or navigation.
    graph(ENEMY,'EnsureFeedback','''(fn EnsureFeedback ()
 (Utilities|IsValid (Variables|Default|GetWarningMarker)
  (:"Is Valid" (return))
  (:"Is Not Valid"
   (bind marker (AddComponent|Common|AddStaticMeshComponent :RelativeTransform (Math|Transform|MakeTransform :Location (Math|Vector|MakeVector 0.0 0.0 -185.0) :Scale (Math|Vector|MakeVector 6.8 6.8 0.025))))
   (Variables|Default|SetWarningMarker marker)
   (Components|StaticMesh|SetStaticMesh :self marker :NewMesh "/Engine/BasicShapes/Cylinder.Cylinder")
   (Collision|SetCollisionEnabled :self marker :NewType "NoCollision")
   (Rendering|Material|SetMaterial :self marker :ElementIndex 0 :Material "/Game/Game/Combat/M_AttackArea.M_AttackArea")
   (Rendering|SetVisibility :self marker :bNewVisibility false))))''')
    graph(DIRECTOR,'EnemyFeedback',f'''(fn EnemyFeedback (Enemy)
 (Class|BPQuestEnemy|EnsureFeedback :self Enemy)
 (bind health (Class|BPQuestEnemy|GetHealth :self Enemy))
 (if (< health (Class|BPQuestEnemy|GetLastObservedHealth :self Enemy))
  (Class|BPQuestEnemy|SetHitFlashUntil :self Enemy :HitFlashUntil (+ {NOW} 0.4)))
 (Class|BPQuestEnemy|SetLastObservedHealth :self Enemy :LastObservedHealth health)
 (Transformation|SetWorldScale3D :self (Class|BPQuestEnemy|GetWarningMarker :self Enemy) :NewScale (Math|Vector|MakeVector 3.4 3.4 0.025))
 (bind location (Transformation|GetActorLocation :self Enemy))
 (Transformation|SetWorldLocation :self (Class|BPQuestEnemy|GetWarningMarker :self Enemy) :NewLocation (Math|Vector|MakeVector (.x location) (.y location) (- (.z location) 82.0)))
 (Rendering|SetVisibility :self (Class|BPQuestEnemy|GetWarningMarker :self Enemy) :bNewVisibility (Class|BPQuestEnemy|GetWindingUp :self Enemy))
 (Rendering|Material|SetMaterial :self (Class|BPTestInteractable|GetCubeMesh :self Enemy) :ElementIndex 0 :Material "/Game/Game/Combat/M_Enemy.M_Enemy")
 (if (Class|BPQuestEnemy|GetWindingUp :self Enemy) (Rendering|Material|SetMaterial :self (Class|BPTestInteractable|GetCubeMesh :self Enemy) :ElementIndex 0 :Material "/Game/Game/Combat/M_Warning.M_Warning"))
 (if (< {NOW} (Class|BPQuestEnemy|GetHitFlashUntil :self Enemy)) (Rendering|Material|SetMaterial :self (Class|BPTestInteractable|GetCubeMesh :self Enemy) :ElementIndex 0 :Material "/Game/Game/Combat/M_HitCream.M_HitCream")))''',[('Enemy',ENEMY+'_C',None)])
    graph(DIRECTOR,'ReturnEnemyHome',f'''(fn ReturnEnemyHome (Enemy)
 (Class|BPQuestEnemy|SetWindingUp :self Enemy :WindingUp false)
 (Class|BPQuestEnemy|SetReturningHome :self Enemy :ReturningHome true)
 (Class|BPQuestEnemy|SetAttackAt :self Enemy :AttackAt (+ {NOW} 1.0))
 (CallFunction|MoveToPoint :Mover Enemy :Destination (Class|BPQuestEnemy|GetHomeLocation :self Enemy) :StopAt 45.0 :Speed 180.0)
 (if (< (Math|Vector|VectorLength (- (Transformation|GetActorLocation :self Enemy) (Class|BPQuestEnemy|GetHomeLocation :self Enemy))) 60.0)
  (Class|BPQuestEnemy|SetReturningHome :self Enemy :ReturningHome false))
 (CallFunction|EnemyFeedback :Enemy Enemy))''',[('Enemy',ENEMY+'_C',None)])
    # Preserve the existing attack amounts, party hits and cooldowns.
    checkpoint=q.AUDIT/'EnemyStep_pre_navigation.dsl'
    if not checkpoint.exists():checkpoint.write_text((q.AUDIT/'EnemyStep.dsl').read_text())
    source=checkpoint.read_text().strip()
    old='(if (CallFunction|IsInSafeHub) (Class|BPQuestEnemy|SetWindingUp :self Enemy :WindingUp false) (return))'
    source=source.replace(old,'')
    source=source.replace('(fn EnemyStep (Enemy)',f'''(fn EnemyStep (Enemy)
 (CallFunction|InitializeEnemyHome :Enemy Enemy)
 (if (or (CallFunction|IsInSafeHub) (or (Class|BPQuestEnemy|GetReturningHome :self Enemy) (> (Math|Vector|VectorLength (- (Transformation|GetActorLocation :self (Variables|Default|GetPlayer)) (Class|BPQuestEnemy|GetHomeLocation :self Enemy))) 900.0)))
  (CallFunction|ReturnEnemyHome :Enemy Enemy) (return))''',1)
    source=source.replace('(Class|BPQuestEnemy|SetWindingUp :self Enemy :WindingUp false) (return)) (if (Class|BPQuestEnemy|GetWindingUp', '(CallFunction|ReturnEnemyHome :Enemy Enemy) (return)) (if (Class|BPQuestEnemy|GetWindingUp',1)
    # Refresh markers after start/cancel/hit, including paths that return early.
    source=source.replace('(return)) (if (>= (Utilities|Time|GetGameTimeinSeconds)', '(CallFunction|EnemyFeedback :Enemy Enemy) (return)) (if (>= (Utilities|Time|GetGameTimeinSeconds)',1)
    source=source[:-1]+' (CallFunction|EnemyFeedback :Enemy Enemy))'
    graph(DIRECTOR,'EnemyStep',source,[('Enemy',ENEMY+'_C',None)])
    checkpoint=q.AUDIT/'FindEnemy_pre_navigation.dsl'
    if not checkpoint.exists():checkpoint.write_text((q.AUDIT/'FindEnemy.dsl').read_text())
    source=checkpoint.read_text().replace('(:then (if (not (Class|BPQuestEnemy|GetUsed :self enemy))','''(:then (CallFunction|InitializeEnemyHome :Enemy enemy) (if (and (not (Class|BPQuestEnemy|GetUsed :self enemy)) (and (not (Class|BPQuestEnemy|GetReturningHome :self enemy)) (<= (Math|Vector|VectorLength (- (Transformation|GetActorLocation :self (Variables|Default|GetPlayer)) (Class|BPQuestEnemy|GetHomeLocation :self enemy))) 900.0)))''',1)
    graph(DIRECTOR,'FindEnemy',source,[('Range','float',None)],[('Enemy',ENEMY+'_C',None)])
    call('save_assets',{'asset_paths':[NAV,ENEMY,DIRECTOR]},ASSET)

def hit_effects():
    create(FX,'/Script/Engine.Actor')
    var(FX,'Amount','float');var(FX,'Label','/Script/Engine.TextRenderComponent')
    graph(FX,'EventGraph','''(event EventBeginPlay
 (bind label (AddComponent|Rendering|AddTextRenderComponent))
 (Variables|Default|SetLabel label)
 (Rendering|Components|TextRender|SetHorizontalAlignment :self label :Value "EHTA_Center")
 (Rendering|Components|TextRender|SetWorldSize :self label :Value 64.0)
 (Rendering|Components|TextRender|SetTextRenderColor :self label :Value "(R=55,G=28,B=12,A=255)")
 (Actor|SetLifeSpan :InLifespan 0.65))
 (event EventTick (DeltaSeconds)
  (Rendering|Components|TextRender|SetText :self (Variables|Default|GetLabel) :Value (Utilities|Text|ToText(String) (Utilities|String|Append "-" (Utilities|String|ToString(Integer) (Math|Float|Truncate (Variables|Default|GetAmount))))))
  (Transformation|SetActorLocation :NewLocation (+ (Transformation|GetActorLocation) (Math|Vector|MakeVector 0.0 0.0 (* DeltaSeconds 55.0)))))''')
    graph(ENEMY,'ShowHit',f'''(fn ShowHit (Damage)
 (Variables|Default|SetHitFlashUntil (+ {NOW} 0.4))
 (bind fx (Game|SpawnActorfromClass :Class "{FX}_C" :SpawnTransform (Math|Transform|MakeTransform :Location (+ (Transformation|GetActorLocation) (Math|Vector|MakeVector 0.0 0.0 85.0)) :Rotation (Math|Rotator|MakeRotator 0.0 0.0 90.0)) :CollisionHandlingOverride "AlwaysSpawn"))
 (Transformation|SetActorLocation :self fx :NewLocation (+ (Transformation|GetActorLocation) (Math|Vector|MakeVector 0.0 0.0 85.0)) :bTeleport true)
 (Transformation|SetActorRotation :self fx :NewRotation (Math|Rotator|MakeRotator 0.0 0.0 90.0))
 (Class|BPCombatHitFX|SetAmount :self fx :Amount Damage))''',[('Damage','float',None)])
    # Insert after the original validated health change, preserving all kill
    # guards, owner/quest credit and return wiring, including one-hit defeats.
    g=ref(ENEMY+':TakeQuestDamage')
    ns=call('get_node_infos',{'nodes':call('find_nodes',{'graph':g,'title':''})})
    by_path={n['node']['refPath']:n for n in ns}
    pending=[n['node']['refPath'] for n in ns if 'FunctionEntry' in n['node']['refPath']]
    reachable=set()
    while pending:
        node=pending.pop()
        if node in reachable:continue
        reachable.add(node)
        for p in by_path[node]['output_pins']:
            if p['type_id']=='Exec':pending.extend(x['node']['refPath'] for x in p['connected_pins'])
    if not any(n['type_id'].endswith('|ShowHit') and n['node']['refPath'] in reachable for n in ns):
        health=next(n for n in ns if n['type_id'].endswith('|SetHealth') and n['node']['refPath'] in reachable)
        p=next(p for p in health['output_pins'] if p['name']=='then')
        old=list(p['connected_pins'])
        new=call('create_node',{'graph':g,'type_id':'CallFunction|ShowHit','pos':{'x':900,'y':300}})
        info=call('get_node_infos',{'nodes':[new]})[0]
        for dest in old:call('break_pins',{'output_pin':p['pin_id'],'input_pin':dest})
        call('connect_pins',{'output_pin':p['pin_id'],'input_pin':next(p['pin_id'] for p in info['input_pins'] if p['name']=='execute')})
        for dest in old:call('connect_pins',{'output_pin':next(p['pin_id'] for p in info['output_pins'] if p['name']=='then'),'input_pin':dest})
        entry=next(n for n in ns if 'FunctionEntry' in n['node']['refPath'])
        call('connect_pins',{'output_pin':next(p['pin_id'] for p in entry['output_pins'] if p['name']=='Damage'),'input_pin':next(p['pin_id'] for p in info['input_pins'] if p['name']=='Damage')})
    call('compile_blueprint',{'blueprint':ref(ENEMY),'warnings_as_errors':True})
    call('save_assets',{'asset_paths':[FX,ENEMY,DIRECTOR,NAV]},ASSET)

if __name__=='__main__':
    if '--hit-only' in sys.argv:hit_effects()
    else:
        if '--enemies-only' not in sys.argv:navigation()
        if '--navigation-only' not in sys.argv:enemies();hit_effects()
