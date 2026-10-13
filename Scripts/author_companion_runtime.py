"""Authors the companion prototype through Unreal's Blueprint tools."""
from build_companion_combat import *
G=lambda n:f'(Variables|Default|Get{n})'
S=lambda n,v='':f'(Variables|Default|Set{n} {v})'
NOW='(Utilities|Time|GetGameTimeinSeconds)'
P=G('Player'); C=G('Companion')
def valid_branches(code):
    # Multi-exec macros terminate DSL flow. Use a small bool helper so validity
    # branches can rejoin before later statements in the same function.
    tokens=[];index=0
    while index<len(code):
        if code[index].isspace():index+=1;continue
        if code[index] in '()':tokens.append(code[index]);index+=1;continue
        begin=index
        if code[index]=='"' or code[index:index+2]==':"':
            index+=2 if code[index]==':' else 1
            while index<len(code):
                if code[index]=='\\':index+=2;continue
                if code[index]=='"':index+=1;break
                index+=1
        else:
            embedded=0
            while index<len(code) and not code[index].isspace():
                if code[index]=='(':embedded+=1
                elif code[index]==')':
                    if not embedded:break
                    embedded-=1
                index+=1
        tokens.append(code[begin:index])
    at=0
    def parse():
        nonlocal at
        t=tokens[at];at+=1
        if t!='(':return t
        out=[]
        while tokens[at]!=')':out.append(parse())
        at+=1;return out
    def rewrite(x):
        if not isinstance(x,list):return x
        if len(x)==3 and x[0]=='bind' and x[1]==['hit','moved']:
            return rewrite(x[2])
        if x and x[0]=='Utilities|IsValid':
            obj=rewrite(x[1]);test=['CallFunction|Valid',':Object',obj]
            if len(x)==2:return test
            yes=next((b[1:] for b in x[2:] if b[0]==':"Is Valid"'),[])
            no=next((b[1:] for b in x[2:] if b[0]==':"Is Not Valid"'),[])
            return ['if',test]+[rewrite(b) for b in yes]+([['else']+[rewrite(b) for b in no]] if no else [])
        return [rewrite(b) for b in x]
    def emit(x):return '('+' '.join(emit(b) for b in x)+')' if isinstance(x,list) else x
    forms=[]
    while at<len(tokens):forms.append(emit(rewrite(parse())))
    return '\n'.join(forms)
def fn(name,body,inputs=(),outputs=()):
    q.BANK=DIRECTOR
    code=f'(fn {name} ({" ".join(x[0] for x in inputs)})\n{body})'
    q.write(ref(DIRECTOR+':'+name),code if name=='Valid' else valid_branches(code))
def declare():
    for name,typ in [('NearestDistance','float'),('HurtReadyAt','float'),('SwitchReadyAt','float'),('HUDText','string')]:var(DIRECTOR,name,typ)
    specs={
      'Valid':([('Object','/Script/CoreUObject.Object',None)],[('IsValid','bool',None)]),
      'Say':([('Text','string',None)],[]), 'CanAct':([],[('Allowed','bool',None)]),
      'FindEnemy':([('Range','float',None)],[('Enemy',ENEMY+'_C',None)]),
      'MoveToward':([('Mover','/Script/Engine.Actor',None),('Goal','/Script/Engine.Actor',None),('StopAt','float',None),('Speed','float',None)],[]),
      'SummonSlot':([('Index','int',None)],[]),'ReleaseActive':([],[]),'Heal':([],[]),
      'Attack':([],[]),'Command':([],[]),'Hurt':([('Amount','float',None),('HitCompanion','bool',None)],[]),
      'MeetBeast':([('Beast',BEAST+'_C',None)],[]),'Setup':([],[]),'CombatStep':([],[]),
      'EnemyStep':([('Enemy',ENEMY+'_C',None)],[]),
      'CaptureCombat':([('Snapshot',SAVE+'_C',None)],[]),'RestoreCombat':([('Snapshot',SAVE+'_C',None)],[]),
      'RefreshHUD':([],[]),
    }
    if '--resume' not in sys.argv:
        for name,(ins,outs) in specs.items():
            q.BANK=DIRECTOR;q.function(name,ins,outs)
    else:
        q.BANK=DIRECTOR;q.function('Valid',*specs['Valid'])
    call('compile_blueprint',{'blueprint':ref(DIRECTOR),'warnings_as_errors':False})
    return specs
def author():
    specs=declare()
    start=next((arg.split('=',1)[1] for arg in sys.argv if arg.startswith('--start=')),None)
    def F(name,body):
        nonlocal start
        if start and start!=name:return
        if start==name:start=None
        if name=='Say' and '--resume' in sys.argv: return
        fn(name,body,*specs[name])
    F('Valid','(Utilities|IsValid Object (:"Is Valid" (return true)) (:"Is Not Valid" (return false)))')
    F('Say',S('Message','Text')+S('MessageUntil',f'(+ {NOW} 5.0)'))
    F('CanAct',f'''(if (not {G('Enabled')}) (return false))
 (Utilities|IsValid {P}
  (:"Is Valid" (bind allowed (Class|BPPlayer|CanSaveLoad :self {P})) (return allowed))
  (:"Is Not Valid" (return false)))''')
    F('FindEnemy',f'''{S('Target')}{S('NearestDistance','Range')}
 (for actor (Actor|GetAllActorsOfClass :ActorClass "{ENEMY}_C")
  (bind enemy (Utilities|Casting|CastToBP_QuestEnemy :Object actor)
   (:then
    (if (not (Class|BPQuestEnemy|GetUsed :self enemy))
     (bind distance (Transformation|GetDistanceTo :self {P} :OtherActor enemy))
     (if (< distance {G('NearestDistance')}) {S('Target','enemy')}{S('NearestDistance','distance')})))
   (:CastFailed)))
 (return {G('Target')})''')
    F('MoveToward', '''(bind distance (Transformation|GetDistanceTo :self Mover :OtherActor Goal))
 (if (> distance StopAt)
  (bind current (Transformation|GetActorLocation :self Mover))
  (bind goal (Transformation|GetActorLocation :self Goal))
  (bind next (Math|Interpolation|VInterptoConstant :Current current :Target (Math|Vector|MakeVector (.x goal) (.y goal) (.z current)) :DeltaTime 0.2 :InterpSpeed Speed))
  (bind (hit moved) (Transformation|SetActorLocation :self Mover :NewLocation next :bSweep true)))''')
    F('SummonSlot',f'''(if (not (CallFunction|CanAct)) (return))
 (if (or (< Index 0) (>= Index (Utilities|Array|Length {G('Roster')}))) (CallFunction|Say :Text "That summon slot is empty. Befriend a beast first.") (return))
 (if (< {NOW} {G('RetreatUntil')}) (CallFunction|Say :Text "Your companion is resting. It will return shortly.") (return))
 (if (< {NOW} {G('SwitchReadyAt')}) (return))
 (Utilities|IsValid {C} (:"Is Valid" (Actor|DestroyActor :self {C})) (:"Is Not Valid"))
 (bind location (+ (Transformation|GetActorLocation :self {P}) (Math|Vector|MakeVector 0.0 130.0 0.0)))
 (bind beast (Game|SpawnActorfromClass :Class "{BEAST}_C" :SpawnTransform (Math|Transform|MakeTransform :Location location :Scale (Math|Vector|MakeVector 0.55 0.55 0.55)) :CollisionHandlingOverride "AlwaysSpawn"))
 (Utilities|IsValid beast
  (:"Is Valid" {S('Companion','beast')}{S('ActiveIndex','Index')}
   (Class|BPBeast|SetIsCompanion :self beast :IsCompanion true)
   (Class|BPBeast|SetBeastID :self beast :BeastID (Utilities|Array|Get(acopy) {G('Roster')} Index))
   {S('SwitchReadyAt',f'(+ {NOW} 2.0)')}
   (CallFunction|Say :Text "Companion summoned. It will help automatically; Q commands an attack."))
  (:"Is Not Valid" (CallFunction|Say :Text "There is no space to summon here.")))''')
    F('ReleaseActive',f'''(if (not (CallFunction|CanAct)) (return))
 (if (and (>= {G('ActiveIndex')} 0) (< {G('ActiveIndex')} (Utilities|Array|Length {G('Roster')})))
  (Utilities|Array|RemoveIndex {G('Roster')} {G('ActiveIndex')})
  (Utilities|IsValid {C} (:"Is Valid" (Actor|DestroyActor :self {C})) (:"Is Not Valid"))
  {S('ActiveIndex','-1')}{S('Companion')}
  (CallFunction|Say :Text "Companion released. A roster slot is free; you can befriend it again."))''')
    F('MeetBeast',f'''(if (not (CallFunction|CanAct)) (return))
 (bind id (Class|BPBeast|GetBeastID :self Beast))
 (if (Class|BPBeast|GetIsCompanion :self Beast) (CallFunction|Say :Text "Your companion is ready to help. Q: attack nearest threat.") (return))
 (if (Class|BPBeast|GetIsFood :self Beast)
  (bind (quantity found) (Utilities|Map|Find (Class|BPPlayer|GetInventoryItems :self {P}) "BeastTreat"))
  (Utilities|Map|Add (Class|BPPlayer|GetInventoryItems :self {P}) "BeastTreat" (+ quantity 1))
  (Rendering|SetActorHiddenInGame :self Beast :bNewHidden true)
  (Collision|SetActorEnableCollision :self Beast :bNewActorEnableCollision false)
  (Class|BPBeast|StartRegrow :self Beast)
  (CallFunction|Say :Text "Gathered a beast treat. Two treats will befriend a beast you have met.") (return))
 (if (Utilities|Array|ContainsItem {G('Roster')} id) (CallFunction|Say :Text "Already befriended! Use 1, 2 or 3 to summon from your roster.") (return))
 (if (>= (Utilities|Array|Length {G('Roster')}) 3) (CallFunction|Say :Text "Your roster is full (3/3). Backspace releases your selected companion.") (return))
 (if (not (Utilities|Array|ContainsItem {G('MetBeasts')} id))
  (Utilities|Array|AddUnique {G('MetBeasts')} id)
  (CallFunction|Say :Text "A new friend! Gather two treats from the small nearby cubes, then return and press E.") (return))
 (bind (quantity found) (Utilities|Map|Find (Class|BPPlayer|GetInventoryItems :self {P}) "BeastTreat"))
 (if (< quantity 2) (CallFunction|Say :Text "This beast would like two treats. Gather some from the nearby cubes.") (return))
 (Utilities|Map|Add (Class|BPPlayer|GetInventoryItems :self {P}) "BeastTreat" (- quantity 2))
 (Utilities|Array|AddUnique {G('Roster')} id)
 (CallFunction|SummonSlot :Index (- (Utilities|Array|Length {G('Roster')}) 1))
 (CallFunction|Say :Text "Befriended! Your roster holds up to three summons; only one travels with you.")''')
    F('Attack',f'''(if (not (CallFunction|CanAct)) (return))
 (if (< {NOW} {G('AttackReadyAt')}) (return))
 (bind range (select {G('UseSpell')} 750.0 190.0))
 (bind enemy (CallFunction|FindEnemy :Range range))
 (Utilities|IsValid enemy
  (:"Is Valid"
   {S('AttackReadyAt',f'(+ {NOW} (select {G("UseSpell")} 1.4 0.8))')}
   (Rendering|Debug|DrawDebugLine :LineStart (Transformation|GetActorLocation :self {P}) :LineEnd (Transformation|GetActorLocation :self enemy) :LineColor "(R=0.15,G=0.7,B=1,A=1)" :Duration 0.3 :Thickness 8.0)
   (bind killed (Class|BPQuestEnemy|TakeQuestDamage :self enemy :Player {P} :Damage (select {G('UseSpell')} 4.0 3.0))))
  (:"Is Not Valid" (CallFunction|Say :Text "No enemy in range. Sword: close range. Spell: ranged.")))''')
    F('Command',f'''(if (not (CallFunction|CanAct)) (return))
 (bind enemy (CallFunction|FindEnemy :Range 950.0))
 (CallFunction|Say :Text "Companion: attack the nearest threat!")''')
    F('Heal',f'''(if (not (CallFunction|CanAct)) (return))
 (if (< {NOW} {G('HealReadyAt')}) (CallFunction|Say :Text "Healing is recharging (8 seconds).") (return))
 {S('PlayerHealth',f'(Math|Float|Min(Float) ( + {G("PlayerHealth")} 35.0) 100.0)')}
 {S('CompanionHealth',f'(Math|Float|Min(Float) (+ {G("CompanionHealth")} 25.0) 60.0)')}
 {S('HealReadyAt',f'(+ {NOW} 8.0)')}
 (CallFunction|Say :Text "A soothing spell restores you and your companion.")''')
    F('Hurt',f'''(if (not (CallFunction|CanAct)) (return))
 (if (<= Amount 0.0) (return))
 (if (< {NOW} {G('HurtReadyAt')}) (return))
 {S('HurtReadyAt',f'(+ {NOW} 0.8)')}
 (if HitCompanion
  {S('CompanionHealth',f'(Math|Float|Max(Float) 0.0 (- {G("CompanionHealth")} Amount))')}
  (if (<= {G('CompanionHealth')} 0.0)
   (Utilities|IsValid {C} (:"Is Valid" (Actor|DestroyActor :self {C})) (:"Is Not Valid"))
   {S('Companion')}{S('RetreatUntil',f'(+ {NOW} 15.0)')}
   (CallFunction|Say :Text "Your companion retreated to recover. It returns in 15 seconds."))
  (else
   {S('PlayerHealth',f'(Math|Float|Max(Float) 0.0 (- {G("PlayerHealth")} Amount))')}
   (if (<= {G('PlayerHealth')} 0.0)
    (bind (hit moved) (Transformation|SetActorTransform :self {P} :NewTransform {G('SafeTransform')} :bSweep false :bTeleport true))
    (Components|Movement|StopMovementImmediately :self (Class|Character|GetCharacterMovement :self {P}))
    {S('PlayerHealth','100.0')}{S('CompanionHealth','60.0')}{S('HurtReadyAt',f'(+ {NOW} 5.0)')}
    (Utilities|IsValid {C} (:"Is Valid" (bind (hit moved) (Transformation|SetActorLocation :self {C} :NewLocation (+ (Transformation|GetActorLocation :self {P}) (Math|Vector|MakeVector 0.0 130.0 0.0)) :bTeleport true))) (:"Is Not Valid"))
    (CallFunction|Say :Text "You returned to safety. Your items and quest progress are safe."))))''')
    F('EnemyStep',f'''(if (Class|BPQuestEnemy|GetUsed :self Enemy) (return))
 (bind distance (Transformation|GetDistanceTo :self Enemy :OtherActor {P}))
 (if (> distance 900.0) (Class|BPQuestEnemy|SetWindingUp :self Enemy :WindingUp false) (return))
 (bind now {NOW})
 (if (Class|BPQuestEnemy|GetWindingUp :self Enemy)
  (if (>= now (Class|BPQuestEnemy|GetAttackAt :self Enemy))
   (Class|BPQuestEnemy|SetWindingUp :self Enemy :WindingUp false)
   (Class|BPQuestEnemy|SetAttackAt :self Enemy :AttackAt (+ now 2.0))
   (if (< distance 170.0)
    (CallFunction|Hurt :Amount 8.0 :HitCompanion false))
   (Utilities|IsValid {C}
    (:"Is Valid" (if (< (Transformation|GetDistanceTo :self Enemy :OtherActor {C}) 170.0) (CallFunction|Hurt :Amount 10.0 :HitCompanion true)))
    (:"Is Not Valid")))
  (else
   (if (or (< distance 150.0) (and (Utilities|IsValid {C}) (< (Transformation|GetDistanceTo :self Enemy :OtherActor {C}) 150.0)))
    (if (>= now (Class|BPQuestEnemy|GetAttackAt :self Enemy))
     (Class|BPQuestEnemy|SetWindingUp :self Enemy :WindingUp true)
     (Class|BPQuestEnemy|SetAttackAt :self Enemy :AttackAt (+ now 1.0))
     (Rendering|Debug|DrawDebugLine :LineStart (Transformation|GetActorLocation :self Enemy) :LineEnd (Transformation|GetActorLocation :self {P}) :LineColor "(R=1,G=0.25,B=0.05,A=1)" :Duration 1.0 :Thickness 5.0))
    (else (CallFunction|MoveToward :Mover Enemy :Goal {P} :StopAt 135.0 :Speed 95.0)))))''')
    F('CombatStep',f'''(if (not (CallFunction|CanAct)) (return))
 (bind now {NOW})
 (if (and (> {G('RetreatUntil')} 0.0) (>= now {G('RetreatUntil')}))
  {S('RetreatUntil','0.0')}{S('CompanionHealth','60.0')}{S('SwitchReadyAt','0.0')}
  (CallFunction|SummonSlot :Index {G('ActiveIndex')}))
 (for actor (Actor|GetAllActorsOfClass :ActorClass "{ENEMY}_C")
  (bind enemy (Utilities|Casting|CastToBP_QuestEnemy :Object actor) (:then (CallFunction|EnemyStep :Enemy enemy)) (:CastFailed)))
 (Utilities|IsValid {C}
  (:"Is Valid"
   (Utilities|IsValid {G('Target')}
    (:"Is Valid" (if (> (Transformation|GetDistanceTo :self {P} :OtherActor {G('Target')}) 1050.0) (CallFunction|FindEnemy :Range 850.0)))
    (:"Is Not Valid" (CallFunction|FindEnemy :Range 850.0)))
   (Utilities|IsValid {G('Target')}
    (:"Is Valid"
     (CallFunction|MoveToward :Mover {C} :Goal {G('Target')} :StopAt 115.0 :Speed 220.0)
     (if (and (< (Transformation|GetDistanceTo :self {C} :OtherActor {G('Target')}) 155.0) (>= now {G('CompanionReadyAt')}))
      {S('CompanionReadyAt','(+ now 0.8)')}
      (Class|BPQuestEnemy|TakeQuestDamage :self {G('Target')} :Player {P} :Damage 1.0)))
    (:"Is Not Valid"
     (if (> (Transformation|GetDistanceTo :self {C} :OtherActor {P}) 1600.0)
      (bind (hit moved) (Transformation|SetActorLocation :self {C} :NewLocation (+ (Transformation|GetActorLocation :self {P}) (Math|Vector|MakeVector 0.0 130.0 0.0)) :bTeleport true))
      (else (CallFunction|MoveToward :Mover {C} :Goal {P} :StopAt 130.0 :Speed 260.0))))))
  (:"Is Not Valid"))
 (CallFunction|RefreshHUD)''')
    spawn=''
    for i,id in enumerate(['Mossling','Emberfox','Rivercub','Moonmoth']):
        spawn+=f'''(bind beast{i} (Game|SpawnActorfromClass :Class "{BEAST}_C" :SpawnTransform (Math|Transform|MakeTransform :Location (+ origin (Math|Vector|MakeVector {[-400,-150,150,400][i]}.0 -250.0 0.0)) :Scale (Math|Vector|MakeVector 0.55 0.55 0.55)) :CollisionHandlingOverride "AdjustIfPossibleButAlwaysSpawn"))
 (Class|BPBeast|SetBeastID :self beast{i} :BeastID "{id}")\n'''
    for i in range(8):
        spawn+=f'''(bind food{i} (Game|SpawnActorfromClass :Class "{BEAST}_C" :SpawnTransform (Math|Transform|MakeTransform :Location (+ origin (Math|Vector|MakeVector {[-350,-150,150,350][i%4]}.0 {100+(i//4)*130}.0 -35.0)) :Scale (Math|Vector|MakeVector 0.25 0.25 0.25)) :CollisionHandlingOverride "AlwaysSpawn"))
 (Class|BPBeast|SetIsFood :self food{i} :IsFood true)\n'''
    F('Setup',f'''(if {G('SetupDone')} (return))
 (bind player (Utilities|Casting|CastToBP_Player :Object (Game|GetPlayerCharacter 0))
  (:then {S('Player','player')}{S('SetupDone','true')}
   {S('SafeTransform','(Transformation|GetActorTransform :self player)')}
   (Input|EnableInput :PlayerController (Game|GetPlayerController 0))
   (bind origin (Transformation|GetActorLocation :self player))
   {spawn}
   (CallFunction|Say :Text "Meet a beast (E), gather two treats, then return. Roster: three summons, one active.")
   (Utilities|Time|SetTimerbyFunctionName :Object self :FunctionName "CombatStep" :Time 0.2 :bLooping true))
  (:CastFailed))''')
    F('CaptureCombat', '\n'.join(f'(Class|BPPlayerSave|Set{dest} :self Snapshot :{dest} {G(src)})' for src,dest in [('Roster','SummonRoster'),('MetBeasts','MetBeasts'),('ActiveIndex','ActiveSummonIndex'),('PlayerHealth','CombatPlayerHealth'),('CompanionHealth','CombatCompanionHealth')]))
    restore='\n'.join(S(dest,f'(Class|BPPlayerSave|Get{src} :self Snapshot)') for dest,src in [('Roster','SummonRoster'),('MetBeasts','MetBeasts'),('ActiveIndex','ActiveSummonIndex'),('PlayerHealth','CombatPlayerHealth'),('CompanionHealth','CombatCompanionHealth')])
    F('RestoreCombat',f'''(Utilities|IsValid {C} (:"Is Valid" (Actor|DestroyActor :self {C})) (:"Is Not Valid"))
 {S('Companion')}{S('Target')}{restore}
 {S('AttackReadyAt',f'(+ {NOW} 1.0)')}{S('HealReadyAt',f'(+ {NOW} 8.0)')}{S('HurtReadyAt',f'(+ {NOW} 3.0)')}{S('SwitchReadyAt','0.0')}{S('RetreatUntil','0.0')}
 (if (<= {G('CompanionHealth')} 0.0) {S('RetreatUntil',f'(+ {NOW} 15.0)')}
  (else (if (>= {G('ActiveIndex')} 0) (CallFunction|SummonSlot :Index {G('ActiveIndex')}))))''')
    # Build a compact HUD string with stable, explicit controls.
    text='(Utilities|String|Append "Health: " (Utilities|String|Conv_IntToString 0))'
    F('RefreshHUD',f'''{S('HUDText',f'(Utilities|String|Append "Health " (Utilities|String|ToString(Float) {G("PlayerHealth")}))')}
 {S('HUDText',f'(Utilities|String|Append {G("HUDText")} (Utilities|String|Append " / 100    Companion " (Utilities|String|ToString(Float) {G("CompanionHealth")})))')}
 {S('HUDText',f'(Utilities|String|Append {G("HUDText")} " / 60\\nRoster (max 3): ")')}
 (for id {G('Roster')} {S('HUDText',f'(Utilities|String|Append {G("HUDText")} (Utilities|String|Append (Utilities|String|ToString(Name) id) "   "))')})
 {S('HUDText',f'(Utilities|String|Append {G("HUDText")} (select {G("UseSpell")} "\\nLMB: frost bolt" "\\nLMB: sword"))')}
 {S('HUDText',f'(Utilities|String|Append {G("HUDText")} "   V: switch weapon   Q: companion attack   H: heal\\n1 / 2 / 3: summon slot   Backspace: release selected   E: interact")')}
 (if (< {NOW} {G('MessageUntil')}) {S('HUDText',f'(Utilities|String|Append {G("HUDText")} (Utilities|String|Append "\\n" {G("Message")}))')})''')
    events=f'''(event EventBeginPlay (Utilities|FlowControl|Delay 0.4) (CallFunction|Setup))
 (event Input|MouseEvents|LeftMouseButton (Key) (:Pressed (CallFunction|Attack)) (:Released))
 (event Input|KeyboardEvents|Q (Key) (:Pressed (CallFunction|Command)) (:Released))
 (event Input|KeyboardEvents|H (Key) (:Pressed (CallFunction|Heal)) (:Released))
 (event Input|KeyboardEvents|V (Key) (:Pressed (if (CallFunction|CanAct) {S('UseSpell',f'(not {G("UseSpell")})')})) (:Released))
 (event Input|KeyboardEvents|1 (Key) (:Pressed (CallFunction|SummonSlot :Index 0)) (:Released))
 (event Input|KeyboardEvents|2 (Key) (:Pressed (CallFunction|SummonSlot :Index 1)) (:Released))
 (event Input|KeyboardEvents|3 (Key) (:Pressed (CallFunction|SummonSlot :Index 2)) (:Released))
 (event Input|KeyboardEvents|Backspace (Key) (:Pressed (CallFunction|ReleaseActive)) (:Released))'''
    # Input-event nodes use their native tool IDs; the DSL event shorthand only
    # supports ordinary Blueprint events, not keyboard/mouse events.
    graph(DIRECTOR,'EventGraph','(event EventBeginPlay (Utilities|FlowControl|Delay 0.4) (CallFunction|Setup))')
    graph(DIRECTOR,'ToggleWeapon',f'(fn ToggleWeapon () (if (CallFunction|CanAct) {S("UseSpell",f"(not {G('UseSpell')})")}))')
    bindings=[('Input|MouseEvents|LeftMouseButton','Attack',None),('Input|KeyboardEvents|Q','Command',None),('Input|KeyboardEvents|H','Heal',None),('Input|KeyboardEvents|V','ToggleWeapon',None),('Input|KeyboardEvents|1','SummonSlot',0),('Input|KeyboardEvents|2','SummonSlot',1),('Input|KeyboardEvents|3','SummonSlot',2),('Input|KeyboardEvents|Backspace','ReleaseActive',None)]
    for i,(key,method,index) in enumerate(bindings):
        event=call('create_node',{'graph':ref(DIRECTOR+':EventGraph'),'type_id':key,'pos':{'x':0,'y':300+i*180}})
        action=call('create_node',{'graph':ref(DIRECTOR+':EventGraph'),'type_id':'CallFunction|'+method,'pos':{'x':350,'y':300+i*180}})
        a,b=call('get_node_infos',{'nodes':[event,action]})
        pressed=next(p['pin_id'] for p in a['output_pins'] if p['name']=='Pressed')
        execute=next(p['pin_id'] for p in b['input_pins'] if p['name']=='execute')
        call('connect_pins',{'output_pin':pressed,'input_pin':execute})
        if index is not None:
            call('set_pin_value',{'pin':next(p['pin_id'] for p in b['input_pins'] if p['name']=='Index'),'value':str(index)})
    call('compile_blueprint',{'blueprint':ref(DIRECTOR),'warnings_as_errors':True})
    call('save_assets',{'asset_paths':[DIRECTOR]},ASSET)
if __name__=='__main__': author()
