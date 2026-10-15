from build_companion_combat import call,ref,OBJ,ASSET
import json
MAT='editor_toolset.toolsets.material.MaterialTools';m=ref('/Game/Environment/BreezeWoodland/M_BreezeFallingLeaves.M_BreezeFallingLeaves')
def n(t,p=None):
 o=call('add_expression',{'material_or_function':m,'expression_class':ref('/Script/Engine.MaterialExpression'+t)},MAT)
 if p:call('set_properties',{'instance':o,'values':json.dumps(p)},OBJ)
 return o
def wire(a,b,p):call('connect_expressions',{'from_expression':a,'from_output_name':'','to_expression':b,'to_input_name':p},MAT)
def vec(label,r,g,b):return n('VectorParameter',{'ParameterName':label,'DefaultValue':{'R':r,'G':g,'B':b,'A':1}})
phase=[e for e in call('get_expressions',{'material_or_function':m},MAT) if 'ComponentMask' in str(call('get_class',{'instance':e},OBJ))][0]
color=n('LinearInterpolate');wire(vec('LeafShadow',.065,.21,.025),color,'A');wire(vec('LeafHighlight',.18,.36,.045),color,'B');wire(phase,color,'Alpha')
call('connect_to_output',{'expression':color,'output_name':'','material_property':'MP_EmissiveColor'},MAT)
call('delete_unused_expressions',{'material':m},MAT);call('recompile',{'material_or_function':m},MAT);call('save_assets',{'asset_paths':[]},ASSET)
call('set_properties',{'instance':ref('/Script/UnrealEd.Default__EditorPerformanceSettings'),'values':json.dumps({'bThrottleCPUWhenNotForeground':False})},OBJ)
print('LEAF_COLOR_FIXED',flush=True)
