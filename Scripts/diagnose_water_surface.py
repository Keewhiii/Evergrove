from build_companion_combat import *
import time
ACT='editor_toolset.toolsets.actor.ActorTools';APP='EditorToolset.EditorAppToolset'
def find(n='',cls=None):
 d={'name':n,'tag':'','collision_channels':[]}
 if cls:d['actor_type']=ref(cls)
 return call('find_actors',d,SCENE)
def props(a,v):return call('set_properties',{'instance':a,'values':json.dumps(v)},OBJ)
try:
 props(ref('/Script/UnrealEd.Default__EditorPerformanceSettings'),{'bThrottleCPUWhenNotForeground':False})
 call('StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','warmupSeconds':0}},APP);time.sleep(.3)
 player=find(cls=PLAYER+'_C')[0];world=find(cls='/Game/Game/World/BP_WoodlandWorld.BP_WoodlandWorld_C')[0]
 props(world,{'TimeOfDayMinutes':720,'ClockPaused':True});call('set_actor_transform',{'actor':player,'xform':{'location':{'x':8500,'y':1900,'z':110}}},ACT)
 a=next(a for a in find('Forest_Lake') if call('get_label',{'actor':a},ACT)=='Forest_Lake');c=call('get_components',{'actor':a,'component_type':ref('/Script/Engine.StaticMeshComponent')},ACT)[0]
 props(c,{'OverrideMaterials':['/Game/Environment/RuralVillage/M_Rural_Cream.M_Rural_Cream']*4})
 camera=json.loads(call('get_properties',{'instance':world,'properties':['FollowCamera']},OBJ))['FollowCamera'];cam=call('get_components',{'actor':camera,'component_type':ref('/Script/Engine.CameraComponent')},ACT)[0];props(cam,{'OrthoWidth':2400});time.sleep(.3)
 gate=find('Forest_ExitToVillage')[0];props(gate,{'CaptureRequested':True,'CaptureCommand':'HighResShot 1600x900 filename="E:/UE5 Projects/AdventureRPG/Saved/SeparateForestAudit/Water_Diagnostic.png"'});time.sleep(.3)
finally:
 if call('IsPIERunning',{},APP):call('StopPIE',{},APP)
 props(ref('/Script/UnrealEd.Default__EditorPerformanceSettings'),{'bThrottleCPUWhenNotForeground':True})
