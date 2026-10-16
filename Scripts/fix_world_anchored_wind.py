"""Keep the animated wind in world space; preserve guild interior visibility."""
from build_companion_combat import call, ref, ROOT, graph, BP, ASSET

WORLD = '/Game/Game/World/BP_WoodlandWorld.BP_WoodlandWorld'
target = ref(WORLD + ':UpdateVisibleWind')
audit = ROOT / 'Saved/WoodlandWindFXAudit'
audit.mkdir(exist_ok=True)
before = audit / 'UpdateVisibleWind_camera_locked_before.dsl'
if not before.exists():
    before.write_text(call('read_graph_dsl', {'graph': target}), encoding='utf-8')
graph(WORLD, 'UpdateVisibleWind', '''(fn UpdateVisibleWind ()
 (if (not (CallFunction|Valid :Object (Variables|Default|GetVisibleWindActor)))
  (for wind (Actor|GetAllActorswithTag :Tag "WoodlandWindVisual")
   (Variables|Default|SetVisibleWindActor wind)))
 (bind player (Game|GetPlayerCharacter 0))
 (if (and (CallFunction|Valid :Object player) (CallFunction|Valid :Object (Variables|Default|GetVisibleWindActor)))
  (bind (x y z) (Math|Vector|BreakVector (Transformation|GetActorLocation :self player)))
  (Rendering|SetActorHiddenInGame :self (Variables|Default|GetVisibleWindActor) :bNewHidden (< y -5000.0))
  (Transformation|SetActorLocation :self (Variables|Default|GetVisibleWindActor) :NewLocation (Math|Vector|MakeVector 2000.0 0.0 0.0) :bTeleport true)))''')
call('compile_blueprint', {'blueprint': ref(WORLD), 'warnings_as_errors': True}, BP)
call('save_assets', {'asset_paths': [WORLD]}, ASSET)
print('WORLD_ANCHORED_WIND_SAVED', flush=True)
