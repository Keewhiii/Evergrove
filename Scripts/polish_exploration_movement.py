"""Editor migration: normalize eight-way input and keep four-way sprite facing stable.

Only the move event's three execution links and TryInteract are rerouted. Other
input events, quest logic and save wiring are preserved in the original graph.
"""
from build_companion_combat import *

def infos(g):
    return call('get_node_infos', {'nodes':call('find_nodes',{'graph':g,'title':''})})

def pin(node, direction, name):
    return next(p['pin_id'] for p in node[direction+'_pins'] if p['name']==name)

def reroute(source, output, dest, input_name='execute'):
    p=next(p for p in source['output_pins'] if p['name']==output)
    for old in p['connected_pins']:
        call('break_pins', {'output_pin':p['pin_id'],'input_pin':old})
    call('connect_pins', {'output_pin':p['pin_id'],'input_pin':pin(dest,'input',input_name)})

def author():
    for name,typ in [('PreviousMoveX','float'),('PreviousMoveY','float'),('FacingHorizontal','bool'),('MoveVector','vector')]:var(PLAYER,name,typ)
    graph(PLAYER,'UpdateMoveFacing','''(fn UpdateMoveFacing (X Y)
 (bind ax (Math|Float|Absolute(Float) X)) (bind ay (Math|Float|Absolute(Float) Y))
 (if (or (> ax 0.15) (> ay 0.15))
  (if (> ax (+ ay 0.15)) (Variables|Default|SetFacingHorizontal true))
  (if (> ay (+ ax 0.15)) (Variables|Default|SetFacingHorizontal false))
  (if (and (> ax 0.15) (and (> (Math|Float|Absolute(Float) (- X (Variables|Default|GetPreviousMoveX))) 0.5) (<= (Math|Float|Absolute(Float) (- Y (Variables|Default|GetPreviousMoveY))) 0.5))) (Variables|Default|SetFacingHorizontal true))
  (if (and (> ay 0.15) (and (> (Math|Float|Absolute(Float) (- Y (Variables|Default|GetPreviousMoveY))) 0.5) (<= (Math|Float|Absolute(Float) (- X (Variables|Default|GetPreviousMoveX))) 0.5))) (Variables|Default|SetFacingHorizontal false))
  (if (<= ax 0.15) (Variables|Default|SetFacingHorizontal false))
  (if (<= ay 0.15) (Variables|Default|SetFacingHorizontal true))
  (if (Variables|Default|GetFacingHorizontal)
   (if (> X 0.0) (Variables|Default|SetLastDirection "NewEnumerator3")
    (else (Variables|Default|SetLastDirection "NewEnumerator2")))
   (else (if (> Y 0.0) (Variables|Default|SetLastDirection "NewEnumerator0")
    (else (Variables|Default|SetLastDirection "NewEnumerator1"))))))
 (Variables|Default|SetPreviousMoveX X) (Variables|Default|SetPreviousMoveY Y))''', [('X','float',None),('Y','float',None)])
    code='(fn ApplyMoveAnimation (Moving) (switch Utilities|FlowControl|Switch|SwitchonE_PlayerDirection (Variables|Default|GetLastDirection)\n'
    # The imported horizontal flipbooks face opposite their asset names.
    for index,direction in enumerate(['Up','Down','Right','Left']):
        code+=f'''(:NewEnumerator{index}
 (if Moving
  (if (Variables|Default|GetIsRunning)
   (Sprite|SetFlipbook :self (Variables|Character|GetSprite) :NewFlipbook "/Game/Game/Characters/Player/Flipbooks/Running_{direction}.Running_{direction}")
   (else (Sprite|SetFlipbook :self (Variables|Character|GetSprite) :NewFlipbook "/Game/Game/Characters/Player/Flipbooks/Walking_{direction}.Walking_{direction}")))
  (else (Sprite|SetFlipbook :self (Variables|Character|GetSprite) :NewFlipbook "/Game/Game/Characters/Player/Flipbooks/Idle_{direction}.Idle_{direction}"))))\n'''
    graph(PLAYER,'ApplyMoveAnimation',code+'))',[('Moving','bool',None)])
    graph(PLAYER,'EndExplorationMove','''(fn EndExplorationMove ()
 (Variables|Default|SetPreviousMoveX 0.0) (Variables|Default|SetPreviousMoveY 0.0)
 (Components|Movement|StopMovementImmediately :self (Variables|Character|GetCharacterMovement))
 (CallFunction|ApplyMoveAnimation :Moving false))''')
    graph(PLAYER,'MoveWithFacing','''(fn MoveWithFacing (X Y)
 (if (CallFunction|CanSaveLoad)
  (CallFunction|UpdateMoveFacing :X X :Y Y)
  (bind camera (Game|GetPlayerCameraManager 0))
  (Variables|Default|SetMoveVector (Math|Vector|ClampVectorSize
   :A (+ (* (Math|Vector|Normalize2D(Vector) (Transformation|GetActorForwardVector :self camera)) Y)
         (* (Math|Vector|Normalize2D(Vector) (Transformation|GetActorRightVector :self camera)) X)) :Min 0.0 :Max 1.0))
  (Pawn|Input|AddMovementInput :WorldDirection (Math|Vector|Normalize2D(Vector) (Variables|Default|GetMoveVector)) :ScaleValue (Math|Vector|VectorLength (Variables|Default|GetMoveVector)))
  (CallFunction|ApplyMoveAnimation :Moving (> (Math|Vector|VectorLength (Variables|Default|GetMoveVector)) 0.15))
  (else (CallFunction|EndExplorationMove))))''',[('X','float',None),('Y','float',None)])
    graph(PLAYER,'InteractWithFacing','''(fn InteractWithFacing ()
 (bind camera (Game|GetPlayerCameraManager 0))
 (bind forward (Math|Vector|Normalize2D(Vector) (Transformation|GetActorForwardVector :self camera)))
 (bind right (Math|Vector|Normalize2D(Vector) (Transformation|GetActorRightVector :self camera)))
 (switch Utilities|FlowControl|Switch|SwitchonE_PlayerDirection (Variables|Default|GetLastDirection)
  (:NewEnumerator0 (Variables|Default|SetInteractionDirection forward) (CallFunction|PerformInteractionTrace))
  (:NewEnumerator1 (Variables|Default|SetInteractionDirection (Math|Vector|NegateVector forward)) (CallFunction|PerformInteractionTrace))
  (:NewEnumerator2 (Variables|Default|SetInteractionDirection (Math|Vector|NegateVector right)) (CallFunction|PerformInteractionTrace))
  (:NewEnumerator3 (Variables|Default|SetInteractionDirection right) (CallFunction|PerformInteractionTrace))))''')
    g=ref(PLAYER+':EventGraph'); nodes=infos(g)
    (q.AUDIT/'MovementAudit/input_connections_checkpoint.json').write_text(json.dumps(nodes,indent=2))
    move=next(n for n in nodes if 'EnhancedInputActionIA_Move' in n['type_id'])
    for fn,outs in [('MoveWithFacing',['Triggered']),('EndExplorationMove',['Completed','Canceled'])]:
        existing=next((n for n in nodes if n['type_id'].endswith('|'+fn)),None)
        if not existing:
            new=call('create_node',{'graph':g,'type_id':'CallFunction|'+fn,'pos':{'x':700,'y':-900 if fn=='MoveWithFacing' else -650}})
            existing=call('get_node_infos',{'nodes':[new]})[0]
        for out in outs:reroute(move,out,existing)
        if fn=='MoveWithFacing':
            for axis in ['X','Y']:
                call('connect_pins',{'output_pin':pin(move,'output','ActionValue_'+axis),'input_pin':pin(existing,'input',axis)})
    event=next(n for n in nodes if n['type_id']=='CustomEvent|TryInteract' or n['type_id'].endswith('Custom|TryInteract'))
    new=call('create_node',{'graph':g,'type_id':'CallFunction|InteractWithFacing','pos':{'x':700,'y':-400}})
    reroute(event,'then',call('get_node_infos',{'nodes':[new]})[0])
    idle=next(n for n in nodes if n['type_id'].endswith('Custom|PlayIdle'))
    new=call('create_node',{'graph':g,'type_id':'CallFunction|ApplyMoveAnimation','pos':{'x':700,'y':-150}})
    reroute(idle,'then',call('get_node_infos',{'nodes':[new]})[0])
    call('compile_blueprint',{'blueprint':ref(PLAYER),'warnings_as_errors':True})
    call('save_assets',{'asset_paths':[PLAYER]},ASSET)

if __name__=='__main__':author()
