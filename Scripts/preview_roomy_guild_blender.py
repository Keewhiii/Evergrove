"""Save and render the whole expanded room without changing the gameplay camera."""
import bpy,math
from mathutils import Vector
scene=bpy.data.scenes['GuildInterior_Studio'];bpy.context.window.scene=scene
cam=scene.camera;cam.data.ortho_scale=37;target=Vector((0,13,3.5));cam.location=target+Vector((0,-.819,.574))*48;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.wm.save_as_mainfile(filepath=r'E:\UE5 Projects\AdventureRPG\ContentSource\GuildInterior\AdventureRPG_GuildInterior.blend')
scene.render.image_settings.file_format=next(x.identifier for x in bpy.types.ImageFormatSettings.bl_rna.properties['file_format'].enum_items if x.identifier=='PNG')
scene.render.filepath=r'E:\UE5 Projects\AdventureRPG\Saved\GuildInteriorAudit\GuildInteriorRoomy.png';bpy.ops.render.render(write_still=True)
