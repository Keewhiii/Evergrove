"""Capture the woodland art through the editor API, without moving gameplay actors."""
from build_companion_combat import call, SCENE, ROOT
import base64, json

APP='EditorToolset.EditorAppToolset'
OUT=ROOT/'Saved/WoodlandArtAudit'
OUT.mkdir(exist_ok=True)
POSE={'location':{'x':2650,'y':2000,'z':1500},'rotation':{'pitch':-38,'yaw':-90,'roll':0}}
ANNOTATIONS={'gridSpacing':0,'gridExtent':0,'gridHeight':0,'maxLabelDistance':0,'classFilter':{'refPath':'/Script/Engine.Actor'},'maxLabels':0}

def capture(name):
    result=call('CaptureViewport',{'captureTransform':POSE,'annotations':ANNOTATIONS,'bShowUI':False},APP)
    (OUT/(name+'.png')).write_bytes(base64.b64decode(result['image']['data']))
    metadata={k:v for k,v in result.items() if k!='image'}
    (OUT/(name+'.json')).write_text(json.dumps(metadata,indent=2))
    print('Saved '+name+'.png',flush=True)

if __name__=='__main__':
    capture('Woodland_EditorDuringPIE' if call('IsPIERunning',{},APP) else 'Woodland_Editor')
