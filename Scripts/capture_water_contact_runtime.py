import unreal as u,json
from pathlib import Path
w=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
c=u.load_asset('/Game/Environment/ForestFeatures/MPC_WaterInteraction')
v=u.MaterialLibrary.get_vector_parameter_value(w,c,'Contact')
Path('E:/UE5 Projects/AdventureRPG/Saved/WaterAdjustmentAudit/contact_sample.json').write_text(json.dumps({'x':v.r,'y':v.g,'z':v.b,'activity':v.a}))

