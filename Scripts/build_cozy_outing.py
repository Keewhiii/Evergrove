"""Additive woodland dressing and a two-part introductory guild outing."""
from build_woodland_blockout import *
COZY='/Game/Game/World/BP_CozyWoodland.BP_CozyWoodland'
FIRST='0_Woodland_010_Tea'
SECOND='0_Woodland_020_Trail'
DT='editor_toolset.toolsets.data_table.DataTableTools'
DA='editor_toolset.toolsets.data_asset.DataAssetTools'

def quests():
    bank=ref('/Game/Game/Quests/DA_QuestBank.DA_QuestBank')
    rows={FIRST:{'questId':FIRST,'questName':'A Little Warmth â€” Tea for the Guild','description':'Before your first woodland patrol, would you gather three sprigs of meadow mint? Look in the sunny patches beside the east trail. Bring them back to me and we will put the kettle on. Reward: 20 gold.','objectiveText':'Gather 3 meadow mint sprigs along the east trail, then return to Luna.','difficulty':'Easy','rewardGold':20,'questGiver':'Luna','targetNPC':'Luna','requiredAmount':3},SECOND:{'questId':SECOND,'questName':'A Little Warmth â€” A Peaceful Path','description':'The tea smells lovely! A few bramble pests are troubling the woodland path. Clear three of them from the trail, then come back to the guild for a warm welcome. Take your beasts along if you have befriended any. Reward: 40 gold.','objectiveText':'Defeat 3 bramble pests on the east trail, then return to Luna.','difficulty':'Easy','rewardGold':40,'questGiver':'Luna','targetNPC':'Luna','requiredAmount':3}}
    existing=call('list_rows',{'data_table':ref(q.TABLE)},DT)
    missing=[k for k in rows if k not in existing]
    if missing:call('add_rows',{'data_table':ref(q.TABLE),'row_names':missing},DT)
    call('set_rows',{'data_table':ref(q.TABLE),'values':json.dumps(rows)},DT)
    rules=json.loads(call('get_properties',{'instance':bank,'properties':['ItemRules']},OBJ))['ItemRules']
    paths=[]
    for quest,kind,target,done in [(FIRST,'Collection','MeadowMint','Just what we needed. Thank you! Here is 20 gold. The kettle is warming; ask me about our next request when you are ready.'),(SECOND,'Combat','BramblePest','The path is peaceful again, and the tea is ready. Here is your 40 gold. You and your companions will always have a place by our hearth.')]:
        name='DA_'+quest;path='/Game/Game/Quests/'+name+'.'+name
        if not call('exists',{'path':path.split('.')[0]},ASSET):call('create',{'folder_path':'/Game/Game/Quests','asset_name':name,'asset_type':ref('/Game/Game/Quests/Blueprints/BP_QuestItemRule.BP_QuestItemRule_C')},DA)
        properties(ref(path),{'QuestID':quest,'ObjectiveType':kind,'ObjectiveTargetType':target,'SharedItemTypes':[target] if kind=='Collection' else [],'CompletionText':done,'CompletedText':'Thank you for helping make the woodland a little more welcoming.'})
        rules[quest]=path;paths.append(path)
    properties(bank,{'ItemRules':rules})
    # Use the authored source: graph readback loses struct output names.
    source=(ROOT/'Saved/QuestBankAudit/CheckQuestEligibility.dsl').read_text(encoding='utf-8')
    backup_path=ROOT/'Saved/CombatAudit/Eligibility_before_cozy.dsl'
    if not backup_path.exists():backup_path.write_text(source,encoding='utf-8')
    source=backup_path.read_text(encoding='utf-8')
    gate=f'''(if (or (== QuestID (Utilities|Name|MakeLiteralName "{FIRST}")) (== QuestID (Utilities|Name|MakeLiteralName "{SECOND}")))
 (if (== (Utilities|Array|Length (Actor|GetAllActorsOfClass :WorldContextObject Player :ActorClass "{WORLD}_C")) 0) (return false))
 (if (not (Utilities|Array|ContainsItem (Class|BPPlayer|GetCompletedQuestIDs Player) (Utilities|Name|MakeLiteralName "0_Delivery_001"))) (return false))
 (if (and (== QuestID (Utilities|Name|MakeLiteralName "{SECOND}")) (not (Utilities|Array|ContainsItem (Class|BPPlayer|GetCompletedQuestIDs Player) (Utilities|Name|MakeLiteralName "{FIRST}")))) (return false)))'''
    source=source.replace('(:"Is Valid"','(:"Is Valid"\n'+gate,1)
    graph('/Game/Game/Quests/Blueprints/BP_QuestBank.BP_QuestBank','CheckQuestEligibility',source)
    call('save_assets',{'asset_paths':paths+[q.TABLE,bank['refPath'],'/Game/Game/Quests/Blueprints/BP_QuestBank.BP_QuestBank']},ASSET)

def scenery():
    create(COZY,'/Script/Engine.Actor')
    graph(COZY,'Part','''(fn Part (Position Scale Mesh Material)
 (bind part (AddComponent|Common|AddStaticMeshComponent :RelativeTransform (Math|Transform|MakeTransform :Location Position :Scale Scale)))
 (Components|StaticMesh|SetStaticMesh :self part :NewMesh Mesh)
 (Collision|SetCollisionEnabled :self part :NewType "NoCollision")
 (Rendering|Material|SetMaterial :self part :ElementIndex 0 :Material Material))''',[('Position','vector',None),('Scale','vector',None),('Mesh','/Script/Engine.StaticMesh',None),('Material','/Script/Engine.MaterialInterface',None)])
    colors={'Cream':(.87,.73,.48,1),'Honey':(.55,.31,.12,1),'Terracotta':(.58,.23,.13,1),'Sage':(.31,.43,.20,1),'Petal':(.78,.43,.40,1),'Lavender':(.49,.40,.62,1),'Glow':(1,.70,.24,1),'Mint':(.37,.60,.30,1)}
    mats={k:material('M_Cozy_'+k,v) for k,v in colors.items()}
    mats['Atlas']='/Game/Environment/PixelWoodland/M_PixelWoodland.M_PixelWoodland'
    mats['RockAtlas']='/Game/Environment/PixelProps/M_Prop_Rock.M_Prop_Rock'
    mats['LeafCard']='/Game/Environment/LayeredWoodland/M_StackedLeaf_1.M_StackedLeaf_1'
    mats['GrassCard']='/Game/Environment/BroadleafGrass/M_BroadleafGrass.M_BroadleafGrass'
    mats['LanternCard']='/Game/Environment/PixelProps/M_Prop_Lantern.M_Prop_Lantern'
    mats['DaisyCard']='/Game/Environment/LayeredWoodland/M_LayeredFlowerPixels.M_LayeredFlowerPixels'
    for k in ['Wood','Leaf','Stone','Path']:mats[k]='/Game/Game/Combat/M_Woodland_'+k+'.M_Woodland_'+k
    parts=[]
    def p(pos,size,mat,mesh='Cube'):parts.append((pos,tuple(v/100 for v in size),mats[mat],mesh))
    # The Blender guild exterior supplies its facade, sign, landing and benches.
    for x,y in [(-710,-220),(710,-220),(840,330),(1440,340),(2020,380)]:
        p((x,y,37),(105,85,74),'Terracotta','Cylinder')
        p((x,y,77),(100,80,15),'Wood','Cylinder')
        for dx,dy in [(-25,0),(20,20),(0,-22)]:
            p((x+dx,y+dy,112),(60,50,65),'Sage','Sphere')
            p((x+dx,y+dy,145),(26,26,22),'Petal','Sphere')
    # Low lanterns frame the route; no new collision or navigation blockers.
    for x,y in [(-710,-220),(710,-220),(1000,-240),(1450,-240),(2050,-240)]:
        p((x,y,3),(100,100,100),'LanternCard','/Game/Environment/PixelProps/SM_Prop_Lantern.SM_Prop_Lantern')
    # Organic foliage clusters and flowers around the first clearing's edges.
    for i,(x,y) in enumerate([(-820,440),(-700,680),(710,630),(820,-550),(1330,-670),(1450,660),(1690,810),(2030,780),(2100,-820),(1600,-850)]):
        p((x,y,3),(85,85,85),'LeafCard','/Game/Environment/PixelProps/SM_Prop_Bush.SM_Prop_Bush')
        p((x+90,y+30,3),(80,80,80),'GrassCard','/Game/Environment/BroadleafGrass/SM_BroadleafGrass.SM_BroadleafGrass')
        p((x-40,y+80,3),(110,110,110),'DaisyCard','/Game/Environment/BreezeWoodland/SM_BreezeFlowers_White.SM_BreezeFlowers_White')
    for x,y in [(1150,125),(1300,-110),(1500,90),(1740,-100),(1940,100)]:p((x,y,6),(55,55,55),'RockAtlas','/Game/Environment/PixelProps/SM_Prop_Rock.SM_Prop_Rock')
    for start in range(0,len(parts),35):
        code='(fn Dress'+str(start//35)+' ()\n'
        for pos,scale,mat,mesh in parts[start:start+35]:
            vec=lambda v:'(Math|Vector|MakeVector '+' '.join(str(float(n)) for n in v)+')'
            mesh_path=mesh if mesh.startswith('/') else f'/Engine/BasicShapes/{mesh}.{mesh}'
            code+=f'(CallFunction|Part :Position {vec(pos)} :Scale {vec(scale)} :Mesh "{mesh_path}" :Material "{mat}")\n'
        graph(COZY,'Dress'+str(start//35),code+')')
    graph(COZY,'EventGraph','(event EventBeginPlay\n (bind root (AddComponent|Common|AddSceneComponent))\n'+''.join(f'(CallFunction|Dress{i})\n' for i in range((len(parts)+34)//35))+')')
    var(WORLD,'CozyDressed','bool')
    graph(WORLD,'EnsureCozy','''(fn EnsureCozy ()
 (if (not (Variables|Default|GetCozyDressed))
 (Variables|Default|SetCozyDressed true)
 (bind dressing (Game|SpawnActorfromClass :Class "/Game/Game/World/BP_CozyWoodland.BP_CozyWoodland_C" :SpawnTransform (Math|Transform|MakeTransform) :CollisionHandlingOverride "AlwaysSpawn"))))''')
    source=(ROOT/'Saved/CombatAudit/UpdateCamera.dsl').read_text(encoding='utf-8')
    for previous in ['1800.0','1666.0']:
        source=source.replace('600.0) '+previous+') 1500.0','600.0) 2224.0) 1500.0')
    if '(CallFunction|EnsureCozy)' not in source:source=source.replace('(fn UpdateCamera (Delta)','(fn UpdateCamera (Delta)\n (CallFunction|EnsureCozy)',1)
    graph(WORLD,'UpdateCamera',source,[('Delta','float',None)])
    call('save_assets',{'asset_paths':[COZY,WORLD]},ASSET)
    print('COZY_PARTS',len(parts),flush=True)

def targets():
    source=(ROOT/'Saved/CombatAudit/SpawnTrailObjectives.dsl').read_text(encoding='utf-8')
    baseline=ROOT/'Saved/CombatAudit/SpawnTrailObjectives_before_cozy.dsl'
    if not baseline.exists():baseline.write_text(source,encoding='utf-8')
    source=baseline.read_text(encoding='utf-8')
    source=source.replace('(+ 1800.0 (* column 850.0))',f'(select (or (== QuestID (Utilities|Name|MakeLiteralName "{FIRST}")) (== QuestID (Utilities|Name|MakeLiteralName "{SECOND}"))) (+ 1640.0 (* index 160.0)) (+ 1800.0 (* column 850.0)))')
    for bp,target,mat in [('BP_QuestPickup','MeadowMint','Mint'),('BP_QuestEnemy','BramblePest','Sage')]:
        cls=bp.replace('_','')
        needle=f'(Class|{cls}|SetQuestOwner :self spawned :QuestOwner Player)'
        addition=f'''(if (== TargetType (Utilities|Name|MakeLiteralName "{target}"))
 (Components|StaticMesh|SetStaticMesh :self (Class|BPTestInteractable|GetCubeMesh :self spawned) :NewMesh "/Engine/BasicShapes/Sphere.Sphere")
 (Rendering|Material|SetMaterial :self (Class|BPTestInteractable|GetCubeMesh :self spawned) :ElementIndex 0 :Material "/Game/Game/Combat/M_Cozy_{mat}.M_Cozy_{mat}"))'''
        source=source.replace(needle,needle+'\n'+addition)
    graph(WORLD,'SpawnTrailObjectives',source,[('Player',PLAYER+'_C',None),('QuestID','name',None),('Kind','name',None),('TargetType','name',None),('Required','int',None)],[('Spawned','int',None)])
    call('save_assets',{'asset_paths':[WORLD]},ASSET)

if __name__=='__main__':
    if '--scenery-only' not in sys.argv:quests()
    if '--quests-only' not in sys.argv:scenery()
    targets()

