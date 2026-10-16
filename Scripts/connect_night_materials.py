"""Dim unlit woodland artwork with one shared clock parameter."""
from build_companion_combat import *
from woodland_fx_graph import Graph, props, MAT
collection=ref('/Game/Environment/DayNight/MPC_WorldClock.MPC_WorldClock')
if not call('exists',{'path':collection['refPath'].split('.')[0]},ASSET):
    call('create_parameter_collection',{'folder_path':'/Game/Environment/DayNight','asset_name':'MPC_WorldClock'},MAT)
    props(collection,{'ScalarParameters':[{'ParameterName':'NightBrightness','DefaultValue':1,'Id':'3a1d82c5-4c25-764a-6e24-0dae12345678'}]})
updated=[]
files=list((ROOT/'Content/Environment').rglob('M_*.uasset'))
files += [file for file in (ROOT/'Content/Game/Combat').glob('M_*.uasset') if file.stem.startswith(('M_Woodland_','M_Cozy_'))]
for file in files:
    path='/Game/'+file.relative_to(ROOT/'Content').with_suffix('').as_posix();m=ref(path+'.'+file.stem)
    model=json.loads(call('get_properties',{'instance':m,'properties':['ShadingModel']},OBJ))['ShadingModel']
    if model!='MSM_Unlit' and file.stem!='M_BroadleafGrass':continue
    expressions=call('get_expressions',{'material_or_function':m},MAT)
    connected=False
    for expression in expressions:
        if 'CollectionParameter' not in str(expression):continue
        parameter=json.loads(call('get_properties',{'instance':expression,'properties':['Collection','ParameterName']},OBJ))
        if parameter.get('ParameterName')=='NightBrightness' and 'MPC_WorldClock' in str(parameter.get('Collection')):connected=True
    if connected:
        updated.append(path);continue
    source=call('get_property_input',{'material':m,'material_property':'MP_EmissiveColor'},MAT)
    if not isinstance(source.get('expression'),dict):continue
    g=Graph(m);param=g.n('CollectionParameter',Collection=collection['refPath'],ParameterName='NightBrightness')
    multiply=g.n('Multiply');g.wire(source['expression'],multiply,'A',source.get('output_name',''));g.wire(param,multiply,'B');g.output(multiply,'MP_EmissiveColor')
    call('recompile',{'material_or_function':m},MAT);updated.append(path)
call('save_assets',{'asset_paths':[]},ASSET)
(ROOT/'Saved/DayNightAudit/night_materials.json').write_text(json.dumps(updated,indent=2))
print('NIGHT_MATERIALS_CONNECTED',len(updated),flush=True)
