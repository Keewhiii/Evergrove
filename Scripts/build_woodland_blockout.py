"""Author a separate playable hub/trail blockout through Unreal's editor API."""
from build_companion_combat import *
from style_companion_prototype import material

WORLD='/Game/Game/World/BP_WoodlandWorld.BP_WoodlandWorld'
LEVEL='/Game/Maps/L_WoodlandBlockout'
ACTOR='editor_toolset.toolsets.actor.ActorTools'

def properties(obj,values):
    call('set_properties',{'instance':obj,'values':json.dumps(values)},OBJ)

def actor(cls,name,location,scale=(1,1,1),rotation=(0,0,0)):
    a=call('add_to_scene_from_class',{'actor_type':ref(cls),'name':name,'xform':{'location':dict(zip(['x','y','z'],location)), 'rotation':dict(zip(['pitch','yaw','roll'],rotation)), 'scale':dict(zip(['x','y','z'],scale))}},SCENE)
    call('set_label',{'actor':a,'label':name},ACTOR)
    call('add_tag',{'actor':a,'tag':'WoodlandBlockout'},ACTOR)
    return a

def piece(name,location,size,mat,mesh='Cube',collision=True):
    a=actor('/Script/Engine.StaticMeshActor',name,location,tuple(v/100 for v in size))
    c=call('get_components',{'actor':a,'component_type':ref('/Script/Engine.StaticMeshComponent')},ACTOR)[0]
    properties(c,{'StaticMesh':f'/Engine/BasicShapes/{mesh}.{mesh}','OverrideMaterials':[mat]})
    if not collision:
        # Decorative crowns and path overlays must never snag the player/follower.
        properties(c,{'bUseDefaultCollision':False,'BodyInstance':{'CollisionProfileName':'NoCollision','CollisionEnabled':'NoCollision'},'bCanEverAffectNavigation':False})
    return a

def author_runtime():
    call('create_folder',{'path':'/Game/Game/World'},ASSET)
    create(WORLD,'/Script/Engine.Actor')
    for n,t in [('FollowCamera','/Script/Engine.CameraActor'),('WorldSpawnCount','int'),('WorldSlotSpawned','bool')]:var(WORLD,n,t)
    graph(WORLD,'Valid','''(fn Valid (Object) (Utilities|IsValid Object (:"Is Valid" (return true)) (:"Is Not Valid" (return false))))''',[('Object','/Script/CoreUObject.Object',None)],[('IsValid','bool',None)])
    graph(WORLD,'IsHubLocation','''(fn IsHubLocation (Location)
 (bind (x y z) (Math|Vector|BreakVector Location))
 (return (and (and (>= x -1100.0) (<= x 1100.0)) (and (>= y -1000.0) (<= y 1000.0)))))''',[('Location','vector',None)],[('Safe','bool',None)])
    graph(WORLD,'UpdateCamera','''(fn UpdateCamera (Delta)
 (bind player (Game|GetPlayerCharacter 0))
 (bind valid (CallFunction|Valid :Object player))
 (if valid
  (bind (x y z) (Math|Vector|BreakVector (Transformation|GetActorLocation :self player)))
  (bind goal (Math|Vector|MakeVector (Math|Float|Clamp(Float) x -550.0 3700.0) (+ (Math|Float|Clamp(Float) y -500.0 600.0) 1800.0) 1500.0))
  (Transformation|SetActorLocation :self (Variables|Default|GetFollowCamera) :NewLocation (Math|Interpolation|VInterpTo :Current (Transformation|GetActorLocation :self (Variables|Default|GetFollowCamera)) :Target goal :DeltaTime Delta :InterpSpeed 5.0) :bTeleport true)))''',[('Delta','float',None)])
    graph(WORLD,'EventGraph',f'''(event EventBeginPlay
 (for actor (Actor|GetAllActorsOfClass :ActorClass "/Script/Engine.CameraActor")
  (bind camera (Utilities|Casting|CastToCameraActor :Object actor)
   (:then (Variables|Default|SetFollowCamera camera)) (:CastFailed)))
 (Game|Player|SetViewTargetwithBlend :self (Game|GetPlayerController 0) :NewViewTarget (Variables|Default|GetFollowCamera) :BlendTime 0.0)
 (bind player (Utilities|Casting|CastToBP_Player :Object (Game|GetPlayerCharacter 0))
  (:then (Class|BPPlayer|SetSaveSlotName :self player :SaveSlotName "AdventureRPG_WoodlandBlockout")) (:CastFailed)))
 (event EventTick (DeltaSeconds) (CallFunction|UpdateCamera :Delta DeltaSeconds))''')
    # Fixed trail clearings replace spawning quest objectives beside the guild desk.
    code='''(fn SpawnTrailObjectives (Player QuestID Kind TargetType Required)
 (Variables|Default|SetWorldSpawnCount 0)
 (if (or (< Required 0) (> Required 24)) (return 0))
 (for index (range Required)
  (Variables|Default|SetWorldSlotSpawned false)
  (for attempt (range 8)
   (if (not (Variables|Default|GetWorldSlotSpawned))
    (bind column (Math|Integer|%(Integer) index 3))
    (bind row (/ index 3))
    (bind location (Math|Vector|MakeVector (+ 1800.0 (* column 850.0)) (+ (select (== Kind (Utilities|Name|MakeLiteralName "Combat")) -450.0 260.0) (+ (* row 100.0) (* attempt 55.0))) 85.0))
    (bind transform (Math|Transform|MakeTransform :Location location :Scale (Math|Vector|MakeVector 0.5 0.5 0.5)))
'''
    for kind,bp in [('Combat','BP_QuestEnemy'),('Collection','BP_QuestPickup')]:
        code+=f'''(if (== Kind (Utilities|Name|MakeLiteralName "{kind}"))
 (bind spawned (Game|SpawnActorfromClass :Class "/Game/Game/Quests/Objectives/{bp}.{bp}_C" :SpawnTransform transform :CollisionHandlingOverride "AdjustIfPossibleButDontSpawnIfColliding"))
 (if (CallFunction|Valid :Object spawned)
  (Class|{bp.replace('_','')}|SetObjectiveTargetType :self spawned :ObjectiveTargetType TargetType)
  (Class|{bp.replace('_','')}|SetSpawnQuestID :self spawned :SpawnQuestID QuestID)
  (Class|{bp.replace('_','')}|SetQuestOwner :self spawned :QuestOwner Player)
'''
        if kind=='Combat':code+='''(Class|BPQuestEnemy|SetMaximumHealth :self spawned :MaximumHealth Required)
 (Class|BPQuestEnemy|SetHealth :self spawned :Health Required)
'''
        code+='''(Variables|Default|SetWorldSlotSpawned true)
 (Variables|Default|SetWorldSpawnCount (+ (Variables|Default|GetWorldSpawnCount) 1))))
'''
    code+='''))) (return (Variables|Default|GetWorldSpawnCount)))'''
    graph(WORLD,'SpawnTrailObjectives',code,[('Player',PLAYER+'_C',None),('QuestID','name',None),('Kind','name',None),('TargetType','name',None),('Required','int',None)],[('Spawned','int',None)])
    call('save_assets',{'asset_paths':[WORLD]},ASSET)

def build_scene():
    current=call('get_current_level',{},SCENE)
    if LEVEL not in str(current):raise RuntimeError('Load the copied woodland map before building it: '+str(current))
    # Operate on the copied map only. Keep lighting and engine/world-partition actors.
    for a in call('find_actors',{'name':'','tag':'','collision_channels':[]},SCENE):
        if LEVEL+'.' not in a['refPath']:raise RuntimeError('Unexpected actor outside copied level: '+str(a))
        label=call('get_label',{'actor':a},ACTOR)
        if label in ['Floor','Counter','LeftWall','RightWall','BackWall','Left Wall','Right Wall','Back Wall','Camera_Interior','PlayerStart','NPC_Luna','BP_Rein','StaticMeshActor'] or label.startswith('HLOD') or 'WoodlandBlockout' in call('get_tags',{'actor':a},ACTOR):
            call('remove_from_scene',{'actor':a},SCENE)
    palette={'Meadow':(.22,.32,.16,1),'Forest':(.14,.23,.13,1),'Path':(.55,.40,.24,1),'Wood':(.24,.12,.065,1),'Plaster':(.68,.56,.38,1),'Leaf':(.12,.29,.14,1),'Stone':(.31,.34,.27,1),'Water':(.12,.31,.35,1),'Trim':(.43,.25,.10,1)}
    mats={n:material('M_Woodland_'+n,c) for n,c in palette.items()}
    piece('Woodland_HubGround',(0,0,-20),(2200,2000,40),mats['Meadow'])
    piece('Woodland_ForestGround',(2700,0,-20),(3200,2400,40),mats['Forest'])
    piece('Woodland_HubWalk',(0,-10,2),(300,1800,4),mats['Path'],collision=False)
    piece('Woodland_Trail',(2350,0,3),(3900,300,5),mats['Path'],collision=False)
    piece('Woodland_GuildDeck',(0,-610,10),(1200,720,20),mats['Wood'])
    piece('Woodland_GuildBack',(0,-970,200),(1240,40,380),mats['Plaster'])
    for x in [-620,620]:
        piece('Woodland_GuildSide',(x,-620,170),(40,700,320),mats['Plaster'])
        for y in [-970,-270]:piece('Woodland_GuildPost',(x,y,205),(65,65,410),mats['Wood'])
    piece('Woodland_GuildBeam',(0,-970,380),(1300,70,65),mats['Wood'])
    piece('Woodland_GuildDesk',(-180,-730,60),(500,90,120),mats['Trim'])
    piece('Woodland_GuildDeskTop',(-180,-730,125),(540,120,20),mats['Wood'])
    # Boundary fences keep both player and follower on the supported blockout floor.
    for x,y,sx,sy in [(0,980,2200,35),(0,-990,2200,35),(-1090,0,35,2000),(1090,-650,35,700),(1090,650,35,700),(2700,1190,3200,35),(2700,-1190,3200,35),(4290,0,35,2400)]:
        piece('Woodland_Boundary',(x,y,70),(sx,sy,140),mats['Wood'])
    # Broad clearings leave room for three companions and straightforward steering.
    for i,x in enumerate([1800,2650,3500]):
        piece('Woodland_Clearing_'+str(i),(x,0,1),(650,1550,2),mats['Meadow'],collision=False)
        piece('Woodland_ClearingPath_'+str(i),(x,0,4),(650,300,4),mats['Path'],collision=False)
    trees=[(-930,-820),(-880,-390),(-900,400),(-800,800),(800,800),(850,-760),(1420,-930),(2050,-980),(2850,-950),(3850,-900),(4100,-450),(4100,500),(3800,950),(3000,950),(2200,1000),(1450,950),(1400,520),(2250,-720),(3100,-760)]
    for i,(x,y) in enumerate(trees):
        piece('Woodland_Trunk_'+str(i),(x,y,125),(70,70,250),mats['Wood'],'Cylinder')
        piece('Woodland_Crown_'+str(i),(x,y,340),(350,350,400),mats['Leaf'],'Cone',False)
    for i,(x,y) in enumerate([(1250,-400),(1280,430),(2200,650),(3100,650),(4000,-100),(-800,0)]):
        piece('Woodland_Rock_'+str(i),(x,y,40),(150,110,100),mats['Stone'],'Sphere')
    actor('/Script/Engine.PlayerStart','Woodland_Start',(0,300,100),rotation=(0,180,0))
    camera=actor('/Script/Engine.CameraActor','Woodland_FollowCamera',(0,2100,1500),rotation=(-38,-90,0))
    properties(camera,{'AutoActivateForPlayer':'Player0'})
    comp=call('get_components',{'actor':camera,'component_type':ref('/Script/Engine.CameraComponent')},ACTOR)[0]
    properties(comp,{'FieldOfView':55.0,'bConstrainAspectRatio':False})
    actor(WORLD+'_C','Woodland_World',(0,0,0))
    bounds=actor('/Script/NavigationSystem.NavMeshBoundsVolume','Woodland_NavigationBounds',(1600,0,300),(28,13,5))
    properties(bounds,{'bIsSpatiallyLoaded':False})
    # These are the same dialogue/quest NPC classes used by the original level.
    npc='/Game/Game/Characters/NPCs/BP_Npc.BP_Npc_C'
    for name,loc in [('Luna',(-180,-840,100)),('Rein',(420,-470,100))]:
        a=actor(npc,'Woodland_'+name,loc)
        properties(a,{'NPCName':name,'NPCDialogueText':"Welcome to the Adventurer's Guild. How may I help you?" if name=='Luna' else '', 'HasChoices':name=='Luna','CompletesQuestOnInteract':True,'QuestToComplete':'0_Delivery_001','QuestNPCID':'None'})
    call('save_assets',{'asset_paths':[LEVEL]},ASSET)
    # New external actor packages aren't registered assets yet, so the MCP
    # save_actor helper rejects them. Unreal's Save All persists them correctly.
    print('WOODLAND_SCENE_AUTHORED: use Unreal Save All (Ctrl+Shift+S), then reload and verify 79 WoodlandBlockout-tagged actors before playing.',flush=True)

if __name__=='__main__':
    if '--scene-only' not in sys.argv:author_runtime()
    if '--runtime-only' not in sys.argv:build_scene()
