"""Tree-palette pixel shading plus local, movement-sensitive grass bend and shake."""
from build_companion_combat import call,ref,ROOT,OBJ,ASSET,graph,var
import json,math
MAT='editor_toolset.toolsets.material.MaterialTools';F='/Game/Environment/BroadleafGrass';m=ref(F+'/M_BroadleafGrass.M_BroadleafGrass');collection=ref(F+'/MPC_GrassInteraction.MPC_GrassInteraction');WORLD='/Game/Game/World/BP_WoodlandWorld.BP_WoodlandWorld'
def props(o,p):return call('set_properties',{'instance':o,'values':json.dumps(p)},OBJ)
props(ref('/Script/UnrealEd.Default__EditorPerformanceSettings'),{'bThrottleCPUWhenNotForeground':False})
def n(t,**p):
 o=call('add_expression',{'material_or_function':m,'expression_class':ref('/Script/Engine.MaterialExpression'+t)},MAT)
 if p:props(o,p)
 return o
def wire(a,b,p,out=''):
 pins=call('get_expression_input_names',{'expression':b},MAT)
 if p=='Input' and p not in pins:p=''
 call('connect_expressions',{'from_expression':a,'from_output_name':out,'to_expression':b,'to_input_name':p},MAT)
def pair(t,a,b):
 o=n(t);wire(a,o,'A');wire(b,o,'B');return o
def mul(a,value):
 o=n('Multiply',ConstB=value);wire(a,o,'A');return o
def add(a,value):
 o=n('Add',ConstB=value);wire(a,o,'A');return o
def clamp(a):
 o=n('Clamp');wire(a,o,'Input');return o
def vec(label,v):return n('VectorParameter',ParameterName=label,DefaultValue={'R':v[0],'G':v[1],'B':v[2],'A':1})
def mask(a,channels,out=''):
 o=n('ComponentMask',R='R' in channels,G='G' in channels,B='B' in channels,A='A' in channels);wire(a,o,'Input',out);return o
def linear(c):
 c=c/255;return c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4
expressions=call('get_expressions',{'material_or_function':m},MAT)
sample=[e for e in expressions if 'TextureSample' in str(call('get_class',{'instance':e},OBJ))][0]
# The same flat forest-to-lime shading language as the tree leaves, retaining the painted pixel clusters.
ramp=n('LinearInterpolate');wire(vec('GrassShadow',[linear(c) for c in (9,58,40)]),ramp,'A');wire(vec('GrassHighlight',[linear(c) for c in (117,172,47)]),ramp,'B')
shade=n('Multiply',ConstB=1.9);wire(sample,shade,'A','G');wire(clamp(shade),ramp,'Alpha')
call('connect_to_output',{'expression':ramp,'output_name':'','material_property':'MP_EmissiveColor'},MAT)
ambient=call('get_property_input',{'material':m,'material_property':'MP_WorldPositionOffset'},MAT)['expression']
interactor=n('CollectionParameter',Collection=collection['refPath'],ParameterName='GrassInteractor')
names=call('get_expression_output_names',{'expression':interactor},MAT);print('COLLECTION_OUTPUTS',names,flush=True)
objectpos=n('ObjectPositionWS');worldpos=n('WorldPosition')
playerxy=mask(interactor,'RG');objectxy=mask(objectpos,'RG');distance=pair('Distance',playerxy,objectxy)
proximity=clamp(add(mul(distance,-1/105),1));weight=pair('Multiply',proximity,proximity)
energy=mask(interactor,'R','A') if 'A' in names else mask(interactor,'A');weight=pair('Multiply',weight,energy)
height=mask(worldpos,'B');weight=pair('Multiply',weight,clamp(mul(height,1/55)))
delta=pair('Subtract',objectxy,playerxy);normalize=n('Normalize');wire(delta,normalize,'Input')
append=n('AppendVector');wire(normalize,append,'A');zero=n('Constant',R=0);wire(zero,append,'B')
bend=mul(append,13)
time=n('Time');sine=n('Sine',Period=1);wire(mul(time,5.5),sine,'Input');shake=pair('Multiply',sine,vec('BrushShakeAmplitude',(8,3,1)))
reaction=pair('Multiply',pair('Add',bend,shake),weight);offset=pair('Add',ambient,reaction)
call('connect_to_output',{'expression':offset,'output_name':'','material_property':'MP_WorldPositionOffset'},MAT)
call('delete_unused_expressions',{'material':m},MAT);call('recompile',{'material_or_function':m},MAT)
var(WORLD,'GrassMoveEnergy','float')
graph(WORLD,'UpdateGrassInteraction','''(fn UpdateGrassInteraction (Delta)
 (bind player (Game|GetPlayerCharacter 0))
 (if (CallFunction|Valid :Object player)
  (bind (x y z) (Math|Vector|BreakVector (Transformation|GetActorLocation :self player)))
  (bind speed (Math|Vector|VectorLengthXY (Transformation|GetVelocity :self player)))
  (Variables|Default|SetGrassMoveEnergy (Math|Interpolation|FInterpTo :Current (Variables|Default|GetGrassMoveEnergy) :Target (Math|Float|Clamp(Float) (/ speed 600.0) 0.0 1.0) :DeltaTime Delta :InterpSpeed 7.0))
  (Rendering|Material|SetVectorParameterValue :Collection "/Game/Environment/BroadleafGrass/MPC_GrassInteraction.MPC_GrassInteraction" :ParameterName "GrassInteractor" :ParameterValue (Utilities|Struct|MakeLinearColor :R x :G y :B z :A (Variables|Default|GetGrassMoveEnergy)))))''',[('Delta','float',None)])
source=(ROOT/'Saved/CombatAudit/UpdateCamera.dsl').read_text(encoding='utf-8')
if '(CallFunction|UpdateGrassInteraction' not in source:source=source.replace('(fn UpdateCamera (Delta)','(fn UpdateCamera (Delta)\n (CallFunction|UpdateGrassInteraction :Delta Delta)',1)
graph(WORLD,'UpdateCamera',source,[('Delta','float',None)])
call('save_assets',{'asset_paths':[]},ASSET)
out=ROOT/'Saved/BroadleafGrassAudit';(out/'interaction.json').write_text(json.dumps({'radius_cm':105,'walk_speed_reference':600,'maximum_bend_cm':13,'shake_cm':8,'settle_interp':7,'palette':[(9,58,40),(117,172,47)]},indent=2));print('GRASS_INTERACTION_AUTHORED',flush=True)
