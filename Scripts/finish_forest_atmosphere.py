from build_companion_combat import *
W='/Game/Game/World/BP_WoodlandWorld.BP_WoodlandWorld'
p=ROOT/'Saved/ForestRecoveryBackup/BeforeAtmosphere/UpdateVisibleWind.dsl'
if not p.exists():p.write_text(call('read_graph_dsl',{'graph':ref(W+':UpdateVisibleWind')}))
graph(W,'UpdateVisibleWind','''(fn UpdateVisibleWind ()
 (if (not (CallFunction|Valid :Object (Variables|Default|GetVisibleWindActor)))
  (for wind (Actor|GetAllActorswithTag :Tag "WoodlandWindVisual") (Variables|Default|SetVisibleWindActor wind)))
 (bind player (Game|GetPlayerCharacter 0))
 (if (not (CallFunction|Valid :Object player)) (return))
 (bind (x y z) (Math|Vector|BreakVector (Transformation|GetActorLocation :self player)))
 (bind indoor (and (not (Utilities|String|EqualExactly(String) (Game|GetCurrentLevelName :bRemovePrefixString true) "L_EvergroveForest")) (< y -5000.0)))
 (if (CallFunction|Valid :Object (Variables|Default|GetVisibleWindActor))
  (Rendering|SetActorHiddenInGame :self (Variables|Default|GetVisibleWindActor) :bNewHidden indoor)
  (Transformation|SetActorLocation :self (Variables|Default|GetVisibleWindActor) :NewLocation (Math|Vector|MakeVector 2000.0 0.0 0.0) :bTeleport true))
 (for effect (Actor|GetAllActorswithTag :Tag "ForestAtmosphere")
  (Rendering|SetActorHiddenInGame :self effect :bNewHidden indoor)))''')
call('compile_blueprint',{'blueprint':ref(W),'warnings_as_errors':True});call('save_assets',{'asset_paths':[W]},ASSET)
# Soften the tiled ribbon opacity while retaining its established motion graph.
from woodland_fx_graph import Graph,MAT
m=ref('/Game/Environment/WoodlandWindFX/M_VisibleWind.M_VisibleWind')
p=call('get_property_input',{'material':m,'material_property':'MP_Opacity'},MAT)['expression']
g=Graph(m);soft=g.n('ScalarParameter',ParameterName='ForestWindSoftness',DefaultValue=.32);g.output(g.pair('Multiply',p,soft),'MP_Opacity');call('recompile',{'material_or_function':m},MAT);call('save_assets',{'asset_paths':[m['refPath']]},ASSET)
print('FOREST_ATMOSPHERE_WORLD_ANCHORED_AND_SOFTENED')
