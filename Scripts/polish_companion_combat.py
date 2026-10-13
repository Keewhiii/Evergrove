from build_companion_combat import *
def author():
    var(DIRECTOR,'MoveIgnoreActors','/Script/Engine.Actor','ARRAY')
    q.BANK=DIRECTOR
    q.write(ref(DIRECTOR+':MoveToward'),'''(fn MoveToward (Mover Goal StopAt Speed)
 (if (> (Transformation|GetDistanceTo :self Mover :OtherActor Goal) StopAt)
  (bind current (Transformation|GetActorLocation :self Mover))
  (bind goal (Transformation|GetActorLocation :self Goal))
  (bind next (Math|Interpolation|VInterptoConstant :Current current :Target (Math|Vector|MakeVector (.x goal) (.y goal) (.z current)) :DeltaTime 0.2 :InterpSpeed Speed))
  (Utilities|Array|Clear (Variables|Default|GetMoveIgnoreActors))
  (Utilities|Array|Add (Variables|Default|GetMoveIgnoreActors) Mover)
  (Utilities|Array|Add (Variables|Default|GetMoveIgnoreActors) Goal)
  (bind (hit blocked) (Collision|SphereTraceByChannel :Start current :End next :Radius 25.0 :TraceChannel "TraceTypeQuery1" :ActorsToIgnore (Variables|Default|GetMoveIgnoreActors) :DrawDebugType "None"))
  (if (not blocked) (Transformation|SetActorLocation :self Mover :NewLocation next :bSweep true))))''')
    code=(q.AUDIT/'EnemyStep.dsl').read_text()
    color='''(Rendering|Material|SetMaterial :self (Class|BPTestInteractable|GetCubeMesh :self Enemy) :ElementIndex 0 :Material "/Game/Game/Combat/M_Enemy.M_Enemy")
 (if (Class|BPQuestEnemy|GetWindingUp :self Enemy) (Rendering|Material|SetMaterial :self (Class|BPTestInteractable|GetCubeMesh :self Enemy) :ElementIndex 0 :Material "/Game/Game/Combat/M_Warning.M_Warning"))
'''
    needle='(bind distance '
    code=code.replace(needle,color+needle,1)
    q.write(ref(DIRECTOR+':EnemyStep'),code)
    call('save_assets',{'asset_paths':[DIRECTOR]},ASSET)
if __name__=='__main__':author()
