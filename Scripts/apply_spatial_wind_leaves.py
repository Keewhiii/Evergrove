"""Gust-driven 3D leaf transport, independent tumbling, and wind-carried running bursts."""
from build_companion_combat import call,ref,ROOT,OBJ,ASSET,SCENE,graph
from woodland_fx_graph import Graph,props,MAT
import json,math
F='/Game/Environment/WoodlandWindFX';OLD='/Game/Environment/BreezeWoodland';SM='editor_toolset.toolsets.static_mesh.StaticMeshTools';ACT='editor_toolset.toolsets.actor.ActorTools';BURST='/Game/Game/World/BP_RunLeafBurst.BP_RunLeafBurst'
props(ref('/Script/UnrealEd.Default__EditorPerformanceSettings'),{'bThrottleCPUWhenNotForeground':False})
for item in json.loads((ROOT/'ContentSource/WoodlandWindFX/spatial_leaves_manifest.json').read_text()):
 if not call('exists',{'path':F+'/'+item['name']},ASSET):call('import_file',{'folder_path':F,'asset_name':item['name'],'source_file':item['file'],'import_materials':False,'import_textures':False,'combine_meshes':True},SM)
 call('remove_collisions',{'mesh':ref(F+'/'+item['name']+'.'+item['name'])},SM)
def clear(m):
 for e in call('get_expressions',{'material_or_function':m},MAT):call('delete_expression',{'material_or_function':m,'expression':e},MAT)
 return Graph(m)
def append(g,a,b):
 n=g.n('AppendVector');g.wire(a,n,'A');g.wire(b,n,'B');return n
def data(g,scale=1):
 uv=g.n('TextureCoordinate');xy=g.n('TextureCoordinate',CoordinateIndex=1);zs=g.n('TextureCoordinate',CoordinateIndex=2)
 local=append(g,xy,g.mask(zs,'R'));local=g.mul(local,scale)
 return g.mask(uv,'R'),g.mask(uv,'G'),g.mask(zs,'G'),local
def tumble(g,time,phase,seed,local):
 yaw=g.pair('Add',g.pair('Multiply',time,g.add(g.mul(seed,.45),.28)),g.mul(phase,5))
 pitch=g.pair('Add',g.pair('Multiply',time,g.add(g.mul(seed,.33),.22)),g.mul(phase,3.1))
 sy=g.sine(yaw);cy=g.sine(g.add(yaw,.25));sp=g.sine(pitch);cp=g.sine(g.add(pitch,.25))
 x,y,z=[g.mask(local,c) for c in ['R','G','B']]
 rx=g.pair('Subtract',g.pair('Multiply',x,cy),g.pair('Multiply',y,sy));ry=g.pair('Add',g.pair('Multiply',x,sy),g.pair('Multiply',y,cy))
 fy=g.pair('Subtract',g.pair('Multiply',ry,cp),g.pair('Multiply',z,sp));fz=g.pair('Add',g.pair('Multiply',ry,sp),g.pair('Multiply',z,cp))
 rotated=append(g,append(g,rx,fy),fz);return g.pair('Subtract',rotated,local),cp
def color(g,phase,orientation):
 ramp=g.n('LinearInterpolate');g.wire(g.vec('LeafShadow',(.035,.16,.025)),ramp,'A');g.wire(g.vec('LeafHighlight',(.15,.32,.045)),ramp,'B');g.wire(phase,ramp,'Alpha')
 shade=g.add(g.mul(g.pair('Multiply',orientation,orientation),.30),.70);g.output(g.pair('Multiply',ramp,shade),'MP_EmissiveColor')
def assign(mesh,m):
 for slot in call('get_material_slots',{'mesh':mesh},SM):call('set_material',{'mesh':mesh,'slot_name':slot,'material':m},SM)

m=ref(OLD+'/M_BreezeFallingLeaves.M_BreezeFallingLeaves');g=clear(m);time=g.n('Time');phase,height,seed,local=data(g);gust=g.gust(time)
age=g.n('Frac');g.wire(g.pair('Add',g.pair('Multiply',time,g.add(g.mul(seed,.025),.05)),phase),age,'Input')
rotation,orientation=tumble(g,time,phase,seed,local)
center=g.pair('Subtract',g.n('WorldPosition'),local);cx=g.mask(center,'R')
# Integrate the positive gust envelope. Sideways velocity rises with the visible wind, rather than merely tilting a gravity fall.
omega=math.tau/32;ta=math.asin(.35)/omega;tb=(math.pi-math.asin(.35))/omega
cycle=g.n('Frac');g.wire(g.mul(time,1/32),cycle,'Input');cycle=g.mul(cycle,32)
s=g.add(g.mul(g.clamp(g.mul(g.add(cycle,-ta),1/(tb-ta))),tb-ta),ta)
cosine=g.sine(g.add(g.mul(s,1/32),.25));integral=g.mul(g.pair('Add',g.add(g.mul(cosine,-1),math.cos(math.asin(.35))),g.mul(g.add(s,-ta),-.35*omega)),1/(.65*omega))
travel=g.pair('Add',g.pair('Multiply',integral,g.add(g.mul(seed,100),180)),g.mul(g.add(s,-ta),25))
sign=g.n('ScalarParameter',ParameterName='WindDirectionSign',DefaultValue=1)
windx=g.pair('Multiply',travel,sign);curl=g.pair('Multiply',g.mul(g.sine(g.pair('Add',g.mul(time,.35),g.mul(phase,5))),50),gust)
windx=g.pair('Add',windx,curl)
wrapped=g.n('Frac');g.wire(g.mul(g.add(g.pair('Add',cx,windx),1200),1/6000),wrapped,'Input');newx=g.add(g.mul(wrapped,6000),-1200);dx=g.pair('Subtract',newx,cx)
dy=g.pair('Multiply',g.sine(g.pair('Add',g.pair('Multiply',time,g.add(g.mul(seed,.18),.16)),g.mul(phase,7))),g.add(g.mul(gust,90),12))
fall=g.pair('Multiply',age,g.add(g.mul(height,-1),25));lift=g.pair('Multiply',g.mul(g.sine(g.pair('Add',g.mul(time,.29),g.mul(phase,4))),38),gust);dz=g.pair('Add',fall,lift)
flight=append(g,append(g,dx,dy),dz);g.output(g.pair('Add',flight,rotation),'MP_WorldPositionOffset');color(g,phase,orientation)
g.output(g.pair('Subtract',gust,g.add(g.mul(phase,.45),.10)),'MP_OpacityMask');props(m,{'BlendMode':'BLEND_Masked','OpacityMaskClipValue':.01,'TwoSided':True,'ShadingModel':'MSM_Unlit'});call('recompile',{'material_or_function':m},MAT)
mesh=ref(F+'/SM_SpatialWindLeaves.SM_SpatialWindLeaves');left=ref(OLD+'/MI_BreezeLeaves_Left.MI_BreezeLeaves_Left');assign(mesh,left)
a=call('find_actors',{'name':'Woodland_IntermittentLeaves','tag':'','collision_channels':[]},SCENE)[0];c=call('get_components',{'actor':a,'component_type':ref('/Script/Engine.StaticMeshComponent')},ACT)[0];props(c,{'StaticMesh':mesh['refPath'],'OverrideMaterials':[left['refPath']],'BoundsScale':2,'CastShadow':False,'ForcedLodModel':1})

# The leaves kicked out by running also tumble and are swept into the current gust.
m=ref(F+'/M_RunLeafBurst.M_RunLeafBurst');g=clear(m);time=g.n('Time');phase,height,seed,local=data(g,1.4);birth=g.n('ScalarParameter',ParameterName='BurstStartTime',DefaultValue=0,bUseCustomPrimitiveData=True,PrimitiveDataIndex=0)
age=g.clamp(g.mul(g.pair('Subtract',time,birth),1/1.25));gust=g.gust(time);rotation,orientation=tumble(g,time,phase,seed,local)
outward=append(g,append(g,g.sine(phase),g.sine(g.add(phase,.25))),g.n('Constant',R=0));outward=g.pair('Multiply',outward,g.mul(age,105))
rise=g.pair('Add',g.mul(age,260),g.mul(g.pair('Multiply',age,age),-330));vertical=g.pair('Multiply',rise,g.vec('UpAxis',(0,0,1)))
sign=g.n('ScalarParameter',ParameterName='WindDirectionSign',DefaultValue=-1);wind=g.pair('Multiply',g.pair('Multiply',g.mul(age,230),gust),sign);wind=g.pair('Multiply',wind,g.vec('WindAxis',(1,0,0)))
g.output(g.pair('Add',g.pair('Add',g.pair('Add',outward,vertical),wind),rotation),'MP_WorldPositionOffset');color(g,phase,orientation);props(m,{'TwoSided':True,'ShadingModel':'MSM_Unlit'});call('recompile',{'material_or_function':m},MAT)
mesh=ref(F+'/SM_SpatialRunLeafBurst.SM_SpatialRunLeafBurst');assign(mesh,m);props(mesh,{'PositiveBoundsExtension':{'x':260,'y':150,'z':120},'NegativeBoundsExtension':{'x':260,'y':150,'z':120}})
graph(BURST,'EventGraph','''(event EventBeginPlay
 (bind leaf (AddComponent|Common|AddStaticMeshComponent :RelativeTransform (Math|Transform|MakeTransform)))
 (Components|StaticMesh|SetStaticMesh :self leaf :NewMesh "/Game/Environment/WoodlandWindFX/SM_SpatialRunLeafBurst.SM_SpatialRunLeafBurst")
 (Collision|SetCollisionEnabled :self leaf :NewType "NoCollision")
 (Rendering|Material|SetCustomPrimitiveDataFloat :self leaf :DataIndex 0 :Value (Utilities|Time|GetGameTimeInSeconds))
 (Actor|SetLifeSpan :InLifespan 1.25))''')
call('save_assets',{'asset_paths':[]},ASSET)
out=ROOT/'Saved/WoodlandWindFXAudit';report={'leaf_count':220,'height_range_cm':[90,580],'depth_range_cm':[-1100,1100],'uv_channels':3,'independent_3d_tumbling':True,'gust_sideways_speed_cm_s':[180,280],'base_sideways_speed_cm_s':25,'fall_lifetime_seconds':[13.33,20],'burst_gust_carry_cm':230}
(out/'spatial_leaves.json').write_text(json.dumps(report,indent=2));print('SPATIAL_WIND_LEAVES_AUTHORED '+json.dumps(report),flush=True)
