"""Simple native mesh beasts and readable material feedback; no external assets."""
from build_companion_combat import *
MAT='editor_toolset.toolsets.material.MaterialTools'
def material(name,color):
    path='/Game/Game/Combat/'+name+'.'+name
    if not call('exists',{'path':path.split('.')[0]},ASSET):
        call('create_material',{'folder_path':'/Game/Game/Combat','asset_name':name},MAT)
        expression=call('add_expression',{'material_or_function':ref(path),'expression_class':ref('/Script/Engine.MaterialExpressionVectorParameter')},MAT)
        call('set_properties',{'instance':expression,'values':json.dumps({'ParameterName':'Tint','DefaultValue':dict(zip(['R','G','B','A'],color))})},OBJ)
        call('connect_to_output',{'expression':expression,'output_name':'','material_property':'MP_EmissiveColor'},MAT)
        call('connect_to_output',{'expression':expression,'output_name':'','material_property':'MP_BaseColor'},MAT)
        call('set_properties',{'instance':ref(path),'values':json.dumps({'ShadingModel':'MSM_Unlit'})},OBJ)
        call('recompile',{'material_or_function':ref(path)},MAT)
        call('save_assets',{'asset_paths':[path]},ASSET)
    return path
def author():
    colors={'M_Mossling':(.22,.55,.28,1),'M_Emberfox':(.8,.3,.12,1),'M_Rivercub':(.16,.48,.8,1),'M_Moonmoth':(.62,.3,.78,1),'M_Treat':(.85,.65,.22,1),'M_Eyes':(.025,.035,.055,1),'M_Enemy':(.62,.16,.23,1),'M_Warning':(1,.65,.05,1)}
    for name,color in colors.items():material(name,color)
    var(BEAST,'BodyMaterial','/Script/Engine.MaterialInterface')
    graph(BEAST,'AddPart','''(fn AddPart (Mesh Offset PartScale Material)
 (bind part (AddComponent|Common|AddStaticMeshComponent :RelativeTransform (Math|Transform|MakeTransform :Location Offset :Scale PartScale)))
 (Components|StaticMesh|SetStaticMesh :self part :NewMesh Mesh)
 (Collision|SetCollisionEnabled :self part :NewType "NoCollision")
 (Rendering|Material|SetMaterial :self part :ElementIndex 0 :Material Material))''',[('Mesh','/Script/Engine.StaticMesh',None),('Offset','vector',None),('PartScale','vector',None),('Material','/Script/Engine.MaterialInterface',None)])
    code='''(fn BuildAppearance ()
 (Variables|Default|SetBodyMaterial "/Game/Game/Combat/M_Mossling.M_Mossling")
'''
    for id in ['Emberfox','Rivercub','Moonmoth']:
        code+=f'''(if (== (Variables|Default|GetBeastID) (Utilities|Name|MakeLiteralName "{id}")) (Variables|Default|SetBodyMaterial "/Game/Game/Combat/M_{id}.M_{id}"))\n'''
    code+='''(if (Variables|Default|GetIsFood) (Variables|Default|SetBodyMaterial "/Game/Game/Combat/M_Treat.M_Treat"))
 (Rendering|Material|SetMaterial :self (Variables|Default|GetCubeMesh) :ElementIndex 0 :Material (Variables|Default|GetBodyMaterial))
 (if (not (Variables|Default|GetIsFood))
'''
    for y in [-23,23]:
        code+=f'''(CallFunction|AddPart :Mesh "/Engine/BasicShapes/Cone.Cone" :Offset (Math|Vector|MakeVector -8.0 {y}.0 45.0) :PartScale (Math|Vector|MakeVector 0.22 0.22 0.45) :Material (Variables|Default|GetBodyMaterial))\n'''
    for y in [-17,17]:
        code+=f'''(CallFunction|AddPart :Mesh "/Engine/BasicShapes/Sphere.Sphere" :Offset (Math|Vector|MakeVector 42.0 {y}.0 10.0) :PartScale (Math|Vector|MakeVector 0.12 0.12 0.16) :Material "/Game/Game/Combat/M_Eyes.M_Eyes")\n'''
    code+='))'
    graph(BEAST,'BuildAppearance',code)
    # Use the authored source, not a lossy graph readback, to preserve bindings.
    import author_companion_support as support
    support.beasts()
    beast=(q.AUDIT/'EventGraph.dsl').read_text()
    beast=beast.replace('(bind label ', '(CallFunction|BuildAppearance)\n (bind label ',1)
    graph(BEAST,'EventGraph',beast)
    call('save_assets',{'asset_paths':[BEAST]},ASSET)
if __name__=='__main__':author()
