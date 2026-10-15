from build_companion_combat import call, ROOT, SCENE, ref, OBJ
from preview_blender_woodland import ANNOTATIONS
import json, base64
OUT=ROOT/'Saved/PixelWoodlandAudit';OUT.mkdir(exist_ok=True)
ACT='editor_toolset.toolsets.actor.ActorTools'
hidden=[]
try:
    for name in ['Woodland_NavigationBounds','WoodlandArt_ColorGrade']:
        for a in call('find_actors',{'name':name,'tag':'','collision_channels':[]},SCENE):
            for c in call('get_components',{'actor':a,'component_type':ref('/Script/Engine.BrushComponent')},ACT):
                p=json.loads(call('get_properties',{'instance':c,'properties':['bVisible']},OBJ));hidden.append((c,p))
                call('set_properties',{'instance':c,'values':json.dumps({'bVisible':False})},OBJ)
    for name,pose in [('PixelWoodland_Overview',{'location':{'x':2650,'y':2000,'z':1500},'rotation':{'pitch':-38,'yaw':-90,'roll':0}}),('PixelWoodland_Close',{'location':{'x':1850,'y':1050,'z':1000},'rotation':{'pitch':-43,'yaw':-90,'roll':0}})]:
        capture=call('CaptureViewport',{'captureTransform':pose,'annotations':ANNOTATIONS,'bShowUI':False},'EditorToolset.EditorAppToolset')
        (OUT/(name+'.png')).write_bytes(base64.b64decode(capture['image']['data']))
        print('Saved '+name,flush=True)
finally:
    for c,p in hidden:call('set_properties',{'instance':c,'values':json.dumps(p)},OBJ)
