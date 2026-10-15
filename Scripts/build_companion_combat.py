"""Explicit editor migration for relaxed companion combat; not a runtime dependency."""
import json, sys, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'Scripts'))
import quest_bank_mcp as q
request = urllib.request.Request('http://127.0.0.1:8000/mcp', data=json.dumps({'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2024-11-05','capabilities':{},'clientInfo':{'name':'companion-combat-authoring','version':'1'}}}).encode(), headers={'Content-Type':'application/json','Accept':'application/json, text/event-stream'})
with urllib.request.urlopen(request, timeout=40) as response:
    q.m.SESSION = response.headers['Mcp-Session-Id']
    response.read()
def combat_rpc(method,params):
    payload={'jsonrpc':'2.0','id':2,'method':method,'params':params}
    headers={'Content-Type':'application/json','Accept':'application/json, text/event-stream','Mcp-Session-Id':q.m.SESSION}
    with urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:8000/mcp',data=json.dumps(payload).encode(),headers=headers),timeout=600) as response:
        result=json.load(response)
    if 'error' in result:raise RuntimeError(result)
    return result['result']
q.m.rpc=combat_rpc
q.AUDIT = ROOT / 'Saved/CombatAudit'
q.AUDIT.mkdir(exist_ok=True)
call=q.call
BP='editor_toolset.toolsets.blueprint.BlueprintTools'
OBJ='editor_toolset.toolsets.object.ObjectTools'
ASSET='editor_toolset.toolsets.asset.AssetTools'
SCENE='editor_toolset.toolsets.scene.SceneTools'
PLAYER=q.PLAYER
ENEMY='/Game/Game/Quests/Objectives/BP_QuestEnemy.BP_QuestEnemy'
SAVE='/Game/Game/Save/BP_PlayerSave.BP_PlayerSave'
GM='/Game/Game/Characters/Player/Blueprints/BP_Gamemode.BP_Gamemode'
DIRECTOR='/Game/Game/Combat/BP_CompanionCombat.BP_CompanionCombat'
BEAST='/Game/Game/Combat/BP_Beast.BP_Beast'
HUD='/Game/Game/Combat/BP_CombatHUD.BP_CombatHUD'
def ref(path): return {'refPath':path}
def create(path,parent):
    if not call('exists',{'path':path.split('.')[0]},ASSET):
        call('create',{'folder_path':path.rsplit('/',1)[0],'asset_name':path.split('.')[-1],'asset_type':ref(parent)})
def var(path,name,typ,container=None):
    if name in call('list_variables',{'blueprint':ref(path)}): return
    args={'blueprint':ref(path),'name':name}
    if container: args['container_type']=container
    if typ.startswith('/'):
        args['object_class']=ref(typ);call('add_object_variable',args)
    else:
        args['type_name']=typ;call('add_variable',args)
def defaults(path,values):
    call('compile_blueprint',{'blueprint':ref(path),'warnings_as_errors':True})
    call('set_properties',{'instance':ref(path.split('.')[0]+'.Default__'+path.split('.')[-1]+'_C'),'values':json.dumps(values)},OBJ)
def graph(path,name,code,inputs=(),outputs=()):
    q.BANK=path
    target=q.function(name,inputs,outputs) if name!='EventGraph' else ref(path+':EventGraph')
    q.write(target,code)
def backup(path,name):
    dst=q.AUDIT/(path.split('.')[-1]+'_'+name+'_before.dsl')
    if not dst.exists(): dst.write_text(call('read_graph_dsl',{'graph':ref(path+':'+name)}),encoding='utf-8')
def discover(path,filters):
    result={}
    for word in filters:
        ids=call('find_node_types',{'graph':ref(path+':EventGraph'),'type_id_filter':word,'context_pins':[]})
        result[word]={node:call('get_node_type_pins',{'graph':ref(path+':EventGraph'),'type_id':node}) for node in ids if 'DebugEvents' not in node}
    (q.AUDIT/'nodes.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    return result
def setup():
    call('create_folder',{'path':'/Game/Game/Combat'},ASSET)
    create(DIRECTOR,'/Script/Engine.Actor')
    create(BEAST,'/Game/Game/Characters/Player/Blueprints/BP_TestInteractable.BP_TestInteractable_C')
    create(HUD,'/Script/Engine.HUD')
    for path in [PLAYER,ENEMY,GM]: backup(path,'EventGraph')
    for name in ['CapturePlayerSave','RestorePlayerSave','ValidatePlayerSave']: backup(PLAYER,name)
    for name,typ,c in [('Player',PLAYER+'_C',None),('Companion',BEAST+'_C',None),('Target',ENEMY+'_C',None),('Roster','name','ARRAY'),('MetBeasts','name','ARRAY'),('ActiveIndex','int',None),('PlayerHealth','float',None),('CompanionHealth','float',None),('AttackReadyAt','float',None),('HealReadyAt','float',None),('CompanionReadyAt','float',None),('RetreatUntil','float',None),('MessageUntil','float',None),('Message','string',None),('UseSpell','bool',None),('Enabled','bool',None),('SetupDone','bool',None)]:var(DIRECTOR,name,typ,c)
    var(DIRECTOR,'SafeTransform','transform')
    for name,typ in [('BeastID','name'),('IsFood','bool'),('IsCompanion','bool')]:var(BEAST,name,typ)
    for name,typ in [('AttackAt','float'),('WindingUp','bool')]:var(ENEMY,name,typ)
    for name,typ,c in [('SummonRoster','name','ARRAY'),('MetBeasts','name','ARRAY'),('ActiveSummonIndex','int',None),('CombatPlayerHealth','float',None),('CombatCompanionHealth','float',None)]:var(SAVE,name,typ,c)
    defaults(DIRECTOR,{'PlayerHealth':100,'CompanionHealth':60,'ActiveIndex':-1,'Enabled':True,'Message':'Meet a beast, gather two treats, then return to befriend it.'})
    defaults(BEAST,{'BeastID':'Mossling'})
    defaults(SAVE,{'ActiveSummonIndex':-1,'CombatPlayerHealth':100,'CombatCompanionHealth':60})
    call('save_assets',{'asset_paths':[DIRECTOR,BEAST,HUD,SAVE,ENEMY]},ASSET)
if __name__=='__main__':
    setup()
    print('Combat asset declarations prepared. Author runtime/support graphs explicitly next.')
