"""Explicit editor migration: encounter state and three concurrent companions.

Retains the existing shared companion health/recovery and save schema. Actor
references and per-beast attack timers are transient and rebuilt on load.
Run after the original companion prototype migrations, never at game startup.
"""
from build_companion_combat import *
from author_companion_runtime import G, S, NOW, P, C, valid_branches

PARTY = G('PartyActors')


def original_sources():
    # Graph readback can misidentify same-named getters on Player/PlayerSave.
    # Reuse the original authoring expressions instead of lossy DSL exports.
    import ast
    import author_companion_runtime as runtime
    tree = ast.parse(Path(runtime.__file__).read_text())
    declaration = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'declare')
    assignment = next(n for n in declaration.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'specs' for t in n.targets))
    specs = eval(compile(ast.Expression(assignment.value), '<original specs>', 'eval'), runtime.__dict__)
    sources = {}
    class CapturedSetup(Exception): pass
    def capture(name, body, inputs=(), outputs=()):
        sources[name] = valid_branches(f'(fn {name} ({" ".join(p[0] for p in inputs)})\n{body})')
        if name == 'Setup': raise CapturedSetup()
    old_fn, old_declare, old_args = runtime.fn, runtime.declare, sys.argv
    try:
        runtime.fn, runtime.declare, sys.argv = capture, lambda: specs, []
        try: runtime.author()
        except CapturedSetup: pass
    finally:
        runtime.fn, runtime.declare, sys.argv = old_fn, old_declare, old_args
    return sources


def author():
    if call('IsPIERunning', {}, 'EditorToolset.EditorAppToolset'):
        raise RuntimeError('Stop Play before authoring runtime Blueprints.')
    for name, typ, container in [('InCombat', 'bool', None), ('LastThreatAt', 'float', None),
                                 ('PartyActors', BEAST+'_C', 'ARRAY'),
                                 ('EmptyPartyActor', BEAST+'_C', None)]:
        var(DIRECTOR, name, typ, container)
    var(BEAST, 'PartyAttackReadyAt', 'float')
    call('compile_blueprint', {'blueprint': ref(BEAST), 'warnings_as_errors': True})
    specs = {'ClearParty': ([], []), 'SyncParty': ([], []),
             'SyncPartySlot': ([('Index', 'int', None)], []),
             'RefreshEncounter': ([], []),
             'StepPartyBeast': ([('Beast', BEAST+'_C', None), ('Index', 'int', None)], [])}
    for name, (ins, outs) in specs.items():
        q.BANK = DIRECTOR
        q.function(name, ins, outs)
    call('compile_blueprint', {'blueprint': ref(DIRECTOR), 'warnings_as_errors': True})

    start = next((arg.split('=',1)[1] for arg in sys.argv if arg.startswith('--start=')), None)
    def F(name, body, inputs=None):
        nonlocal start
        if start and name != start:
            return
        if name == start:
            start = None
        ins = inputs if inputs is not None else specs.get(name, ([], []))[0]
        code = f'(fn {name} ({" ".join(p[0] for p in ins)})\n{body})'
        # All validity checks rejoin execution; no dangling macro branches.
        graph(DIRECTOR, name, valid_branches(code), ins)

    F('ClearParty', f'''(if (CallFunction|Valid :Object {C}) (Actor|DestroyActor :self {C}))
    {S('Companion')}
    (for beast {PARTY}
     (if (CallFunction|Valid :Object beast) (Actor|DestroyActor :self beast)))
    (Utilities|Array|Clear {PARTY})
    ''' + '\n'.join(f'(Utilities|Array|Add {PARTY} {G("EmptyPartyActor")})' for _ in range(3)))

    F('SyncPartySlot', f'''(bind beast (Utilities|Array|Get(acopy) {PARTY} Index))
    (bind wanted (and (< Index (Utilities|Array|Length {G('Roster')}))
      (and (> {G('CompanionHealth')} 0.0)
       (and (>= {NOW} {G('RetreatUntil')}) (or {G('InCombat')} (== Index {G('ActiveIndex')}))))))
    (if (not wanted)
     (if (CallFunction|Valid :Object beast) (Actor|DestroyActor :self beast))
     (Utilities|Array|SetArrayElem :TargetArray {PARTY} :Index Index :Item {G('EmptyPartyActor')})
     (return))
    (if (CallFunction|Valid :Object beast) (return))
    (bind location (+ (Transformation|GetActorLocation :self {P})
      (Math|Vector|MakeVector (- (* Index 120.0) 120.0) 130.0 0.0)))
    (bind created (Game|SpawnActorfromClass :Class "{BEAST}_C"
      :SpawnTransform (Math|Transform|MakeTransform :Location location :Scale (Math|Vector|MakeVector 0.55 0.55 0.55))
      :CollisionHandlingOverride "AlwaysSpawn"))
    (if (CallFunction|Valid :Object created)
     (Class|BPBeast|SetIsCompanion :self created :IsCompanion true)
     (Class|BPBeast|SetBeastID :self created :BeastID (Utilities|Array|Get(acopy) {G('Roster')} Index))
     (Utilities|Array|SetArrayElem :TargetArray {PARTY} :Index Index :Item created))''')

    F('SyncParty', f'''(if (!= (Utilities|Array|Length {PARTY}) 3) (CallFunction|ClearParty))
    (if (or (< {G('ActiveIndex')} 0) (>= {G('ActiveIndex')} (Utilities|Array|Length {G('Roster')})))
     {S('ActiveIndex', f'(select (> (Utilities|Array|Length {G("Roster")}) 0) 0 -1)')})
    (CallFunction|SyncPartySlot :Index 0)
    (CallFunction|SyncPartySlot :Index 1)
    (CallFunction|SyncPartySlot :Index 2)
    {S('Companion')}
    (if (and (>= {G('ActiveIndex')} 0) (< {G('ActiveIndex')} 3))
     {S('Companion', f'(Utilities|Array|Get(acopy) {PARTY} {G("ActiveIndex")})')})''')

    F('RefreshEncounter', f'''(bind threat (CallFunction|FindEnemy :Range (select {G('InCombat')} 1050.0 850.0)))
    (if (CallFunction|Valid :Object threat)
     {S('InCombat', 'true')}{S('LastThreatAt', NOW)}
     (else (if (and {G('InCombat')} (>= (- {NOW} {G('LastThreatAt')}) 4.0))
      {S('InCombat', 'false')}{S('Target')})))''')

    F('StepPartyBeast', f'''(if (not (CallFunction|Valid :Object Beast)) (return))
    (if {G('InCombat')}
     (if (CallFunction|Valid :Object {G('Target')})
      (if (not (Class|BPQuestEnemy|GetUsed :self {G('Target')}))
       (CallFunction|MoveToward :Mover Beast :Goal {G('Target')} :StopAt (+ 110.0 (* Index 15.0)) :Speed 220.0)
       (if (and (< (Transformation|GetDistanceTo :self Beast :OtherActor {G('Target')}) 175.0)
                (>= {NOW} (Class|BPBeast|GetPartyAttackReadyAt :self Beast)))
        (Class|BPBeast|SetPartyAttackReadyAt :self Beast :PartyAttackReadyAt (+ {NOW} 0.8))
        (Class|BPQuestEnemy|TakeQuestDamage :self {G('Target')} :Player {P} :Damage 1.0)))
      (else (CallFunction|MoveToward :Mover Beast :Goal {P} :StopAt (+ 130.0 (* Index 35.0)) :Speed 260.0)))
     (else
      (if (> (Transformation|GetDistanceTo :self Beast :OtherActor {P}) 1600.0)
       (Transformation|SetActorLocation :self Beast :NewLocation (+ (Transformation|GetActorLocation :self {P}) (Math|Vector|MakeVector 0.0 130.0 0.0)) :bTeleport true)
       (else (CallFunction|MoveToward :Mover Beast :Goal {P} :StopAt 130.0 :Speed 260.0)))))''')

    F('SummonSlot', f'''(if (not (CallFunction|CanAct)) (return))
    (if (or (< Index 0) (>= Index (Utilities|Array|Length {G('Roster')})))
     (CallFunction|Say :Text "That follower slot is empty. Befriend a beast first.") (return))
    (if (< {NOW} {G('SwitchReadyAt')}) (return))
    {S('ActiveIndex', 'Index')}{S('SwitchReadyAt', f'(+ {NOW} 2.0)')}
    (CallFunction|SyncParty)
    (CallFunction|Say :Text (select {G('InCombat')}
      "All your friends fight together. Your overworld follower is selected."
      "Follower selected. All tamed friends will join you in combat."))''', [('Index', 'int', None)])

    F('ReleaseActive', f'''(if (not (CallFunction|CanAct)) (return))
    (if {G('InCombat')} (CallFunction|Say :Text "Wait until combat ends to release a friend.") (return))
    (if (and (>= {G('ActiveIndex')} 0) (< {G('ActiveIndex')} (Utilities|Array|Length {G('Roster')})))
     (Utilities|Array|RemoveIndex {G('Roster')} {G('ActiveIndex')})
     (CallFunction|ClearParty)
     {S('ActiveIndex', '-1')}
     (CallFunction|SyncParty)
     (CallFunction|Say :Text "Companion released. A roster slot is free."))''')

    # Enemies now consider every active summon when choosing to wind up/hit.
    nearby = '\n'.join(f'''(bind friend{i} (Utilities|Array|Get(acopy) {PARTY} {i}))
     (if (CallFunction|Valid :Object friend{i})
      (if (< (Transformation|GetDistanceTo :self Enemy :OtherActor friend{i}) 170.0)
       (CallFunction|Hurt :Amount 10.0 :HitCompanion true)))''' for i in range(3))
    close = '\n'.join(f'''(bind friend{i} (Utilities|Array|Get(acopy) {PARTY} {i}))
     (if (CallFunction|Valid :Object friend{i})
      (if (< (Transformation|GetDistanceTo :self Enemy :OtherActor friend{i}) 150.0)
       (Class|BPQuestEnemy|SetWindingUp :self Enemy :WindingUp true)))''' for i in range(3))
    F('EnemyStep', f'''(if (Class|BPQuestEnemy|GetUsed :self Enemy) (return))
    (Rendering|Material|SetMaterial :self (Class|BPTestInteractable|GetCubeMesh :self Enemy) :ElementIndex 0 :Material "/Game/Game/Combat/M_Enemy.M_Enemy")
    (bind distance (Transformation|GetDistanceTo :self Enemy :OtherActor {P}))
    (if (or (not {G('InCombat')}) (> distance 1050.0))
     (Class|BPQuestEnemy|SetWindingUp :self Enemy :WindingUp false) (return))
    (if (Class|BPQuestEnemy|GetWindingUp :self Enemy)
     (Rendering|Material|SetMaterial :self (Class|BPTestInteractable|GetCubeMesh :self Enemy) :ElementIndex 0 :Material "/Game/Game/Combat/M_Warning.M_Warning")
     (if (>= {NOW} (Class|BPQuestEnemy|GetAttackAt :self Enemy))
      (Class|BPQuestEnemy|SetWindingUp :self Enemy :WindingUp false)
      (Class|BPQuestEnemy|SetAttackAt :self Enemy :AttackAt (+ {NOW} 2.0))
      (if (< distance 170.0) (CallFunction|Hurt :Amount 8.0 :HitCompanion false))
      {nearby})
     (return))
    (if (>= {NOW} (Class|BPQuestEnemy|GetAttackAt :self Enemy))
     (if (< distance 150.0) (Class|BPQuestEnemy|SetWindingUp :self Enemy :WindingUp true))
     {close}
     (if (Class|BPQuestEnemy|GetWindingUp :self Enemy)
      (Class|BPQuestEnemy|SetAttackAt :self Enemy :AttackAt (+ {NOW} 1.0))))
    (if (not (Class|BPQuestEnemy|GetWindingUp :self Enemy))
     (CallFunction|MoveToward :Mover Enemy :Goal {P} :StopAt 135.0 :Speed 95.0))''', [('Enemy', ENEMY+'_C', None)])

    steps = '\n'.join(f'(CallFunction|StepPartyBeast :Beast (Utilities|Array|Get(acopy) {PARTY} {i}) :Index {i})' for i in range(3))
    F('CombatStep', f'''(if (not (CallFunction|CanAct)) (return))
    (CallFunction|RefreshEncounter)
    (if (and (> {G('RetreatUntil')} 0.0) (>= {NOW} {G('RetreatUntil')}))
     {S('RetreatUntil','0.0')}{S('CompanionHealth','60.0')}{S('SwitchReadyAt','0.0')})
    (CallFunction|SyncParty)
    (for actor (Actor|GetAllActorsOfClass :ActorClass "{ENEMY}_C")
     (bind enemy (Utilities|Casting|CastToBP_QuestEnemy :Object actor)
      (:then (CallFunction|EnemyStep :Enemy enemy)) (:CastFailed)))
    {steps}
    (CallFunction|RefreshHUD)''')

    restore = '\n'.join(S(dest, f'(Class|BPPlayerSave|Get{src} :self Snapshot)') for dest, src in
        [('Roster','SummonRoster'),('MetBeasts','MetBeasts'),('ActiveIndex','ActiveSummonIndex'),
         ('PlayerHealth','CombatPlayerHealth'),('CompanionHealth','CombatCompanionHealth')])
    F('RestoreCombat', f'''(CallFunction|ClearParty)
    {S('InCombat','false')}{S('LastThreatAt','0.0')}{S('Target')}
    {restore}
    {S('AttackReadyAt', f'(+ {NOW} 1.0)')}{S('HealReadyAt', f'(+ {NOW} 8.0)')}
    {S('HurtReadyAt', f'(+ {NOW} 3.0)')}{S('SwitchReadyAt','0.0')}{S('RetreatUntil','0.0')}
    (if (<= {G('CompanionHealth')} 0.0) {S('RetreatUntil', f'(+ {NOW} 15.0)')})
    (CallFunction|SyncParty)''', [('Snapshot', SAVE+'_C', None)])

    # Preserve befriending, healing, setup, defeat and input wiring; update only
    # messages and party cleanup at the existing knockout/defeat boundaries.
    sources = original_sources()
    for name in ['MeetBeast', 'Heal', 'Setup', 'Hurt']:
        code = sources[name]
        code = code.replace('only one travels with you.', 'one follows outside combat; all join battles.')
        code = code.replace('Roster: three summons, one active.', 'One overworld follower; all tamed friends join combat.')
        code = code.replace('you and your companion.', 'you and your companions.')
        if name == 'Hurt':
            code = code.replace('(Variables|Default|SetCompanionHealth 60.0)',
                                '(Variables|Default|SetCompanionHealth 60.0) (CallFunction|ClearParty)')
            code = code.replace('(CallFunction|Say :Text "Your companion retreated',
                                '(CallFunction|ClearParty) (CallFunction|Say :Text "Your party retreated')
        q.BANK = DIRECTOR
        q.write(ref(DIRECTOR+':'+name), code)
    call('compile_blueprint', {'blueprint': ref(DIRECTOR), 'warnings_as_errors': True})
    print('Saved party runtime:', call('save_assets', {'asset_paths': [DIRECTOR, BEAST]}, ASSET))


if __name__ == '__main__':
    author()
