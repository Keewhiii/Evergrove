from build_companion_combat import call,ref,OBJ
import json
MAT='editor_toolset.toolsets.material.MaterialTools'
def props(o,p):return call('set_properties',{'instance':o,'values':json.dumps(p)},OBJ)
class Graph:
 def __init__(self,material):self.m=material
 def n(self,t,**p):
  o=call('add_expression',{'material_or_function':self.m,'expression_class':ref('/Script/Engine.MaterialExpression'+t)},MAT)
  if p:props(o,p)
  return o
 def wire(self,a,b,p,out=''):
  pins=call('get_expression_input_names',{'expression':b},MAT)
  if p=='Input' and p not in pins:p=''
  call('connect_expressions',{'from_expression':a,'from_output_name':out,'to_expression':b,'to_input_name':p},MAT)
 def pair(self,t,a,b):
  o=self.n(t);self.wire(a,o,'A');self.wire(b,o,'B');return o
 def mul(self,a,v):
  o=self.n('Multiply',ConstB=v);self.wire(a,o,'A');return o
 def add(self,a,v):
  o=self.n('Add',ConstB=v);self.wire(a,o,'A');return o
 def vec(self,name,v):return self.n('VectorParameter',ParameterName=name,DefaultValue={'R':v[0],'G':v[1],'B':v[2],'A':1})
 def mask(self,a,c):
  o=self.n('ComponentMask',R='R' in c,G='G' in c,B='B' in c,A='A' in c);self.wire(a,o,'Input');return o
 def sine(self,a,period=1):
  o=self.n('Sine',Period=period);self.wire(a,o,'Input');return o
 def clamp(self,a):
  o=self.n('Clamp');self.wire(a,o,'Input');return o
 def output(self,a,p,out=''):call('connect_to_output',{'expression':a,'output_name':out,'material_property':p},MAT)
 def gust(self,time):return self.clamp(self.mul(self.add(self.sine(self.mul(time,1/32)),-.35),1/.65))
