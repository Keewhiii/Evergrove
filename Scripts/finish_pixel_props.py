from build_companion_combat import call,ref,ROOT,OBJ,ASSET
import json
MAT='editor_toolset.toolsets.material.MaterialTools';F='/Game/Environment/PixelProps';m=ref(F+'/M_Prop_Lantern.M_Prop_Lantern')
def node(t):return call('add_expression',{'material_or_function':m,'expression_class':ref('/Script/Engine.MaterialExpression'+t)},MAT)
def wire(a,out,b,pin):call('connect_expressions',{'from_expression':a,'from_output_name':out,'to_expression':b,'to_input_name':pin},MAT)
sample=[e for e in call('get_expressions',{'material_or_function':m},MAT) if 'TextureSample' in str(call('get_class',{'instance':e},OBJ))][0]
power=node('Power');call('set_properties',{'instance':power,'values':json.dumps({'ConstExponent':8})},OBJ)
multiply=node('Multiply');call('set_properties',{'instance':multiply,'values':json.dumps({'ConstB':4})},OBJ)
add=node('Add');wire(sample,'RGB',power,'Base');wire(power,'',multiply,'A');wire(multiply,'',add,'A');wire(sample,'RGB',add,'B')
call('connect_to_output',{'expression':add,'output_name':'','material_property':'MP_EmissiveColor'},MAT);call('recompile',{'material_or_function':m},MAT)
call('save_assets',{'asset_paths':[]},ASSET)
print('Lantern glass emissive ready',flush=True)
