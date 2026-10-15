"""Reconstruct the original deterministic art placements and preserve full transforms."""
import import_blender_woodland as original
from build_companion_combat import call, ROOT
import json
snapshot=json.loads((ROOT/'Saved/WoodlandArtAudit/scene_before.json').read_text())
by_path={a['actor']['refPath']:a for a in snapshot}
placements=[]
def mock_call(name,args,ts=None):
    if name=='get_current_level':return '/Game/Maps/L_WoodlandBlockout'
    if name=='find_actors':return [] if args['tag'] else [a['actor'] for a in snapshot]
    if name=='get_label':return by_path[args['actor']['refPath']]['label']
    if name=='get_actor_transform':return by_path[args['actor']['refPath']]['transform']
    if name=='get_components':return []
    return True
def record(name,mesh,x,y,z=2,scale=1,yaw=0):
    placements.append({'label':'WoodlandArt_'+name,'mesh':mesh,'transform':{'location':{'x':x,'y':y,'z':z},'rotation':{'pitch':0,'yaw':0,'roll':0},'scale':{'x':scale*1.2,'y':scale*1.2,'z':scale*1.2}}})
    return {'label':name}
original.call=mock_call;original.art=record
original.AUDIT=ROOT/'Saved/PixelWoodlandAudit/Reconstruction';original.AUDIT.mkdir(exist_ok=True)
original.dress()
trees={p['label']:p['transform'] for p in placements if p['mesh'].startswith('Broadleaf')}
script='''import json
def find():
    return execute_tool('editor_toolset.toolsets.scene.SceneTools.find_actors',json.dumps({'name':'','tag':'WoodlandBlenderArt','collision_channels':[]}))['returnValue']
def label(a):
    return execute_tool('editor_toolset.toolsets.actor.ActorTools.get_label',json.dumps({'actor':a}))['returnValue']
def move(a,xf):
    return execute_tool('editor_toolset.toolsets.actor.ActorTools.set_actor_transform',json.dumps({'actor':a,'xform':xf,'worldspace':True}))
def run():
    positions=POSITIONS
    count=0
    for a in find():
        name=label(a)
        if name in positions:move(a,positions[name]);count+=1
    return {'restored_tree_positions':count}
'''.replace('POSITIONS',repr(trees))
print(call('execute_tool_script',{'script':script},'editor_toolset.toolsets.programmatic.ProgrammaticToolset'))
