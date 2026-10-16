"""Import the OFL Cinzel face and create a Canvas-compatible runtime font."""
import unreal
root='E:/UE5 Projects/AdventureRPG'
folder='/Game/Game/UI/Evergrove'
tools=unreal.AssetToolsHelpers.get_asset_tools()
existing_font=unreal.load_asset(folder+'/F_EvergroveStory') if unreal.EditorAssetLibrary.does_asset_exist(folder+'/F_EvergroveStory') else None
task=unreal.AssetImportTask()
task.filename=root+'/ContentSource/EvergroveIntro/Fonts/Cinzel.ttf'
task.destination_path=folder
task.destination_name='FF_Cinzel'
task.automated=True
task.save=True
task.factory=unreal.FontFileImportFactory()
task.factory.set_editor_property('batch_create_font_asset',unreal.BatchCreateFontAsset.NO if existing_font else unreal.BatchCreateFontAsset.YES)
task.replace_existing=True
tools.import_asset_tasks([task])
face=unreal.load_asset(folder+'/FF_Cinzel')
assert face
font=existing_font or next((unreal.load_asset(path) for path in unreal.EditorAssetLibrary.list_assets(folder) if 'Cinzel' in path and isinstance(unreal.load_asset(path),unreal.Font)),None)
assert font
if not existing_font:assert unreal.EditorAssetLibrary.rename_loaded_asset(font,folder+'/F_EvergroveStory')
font.set_editor_property('font_cache_type',unreal.FontCacheType.RUNTIME)
font.set_editor_property('legacy_font_size',24)
font.set_editor_property('legacy_font_name','Regular')
unreal.EditorAssetLibrary.save_loaded_asset(font)
unreal.log('EVERGROVE_CINZEL_FONT_READY')
unreal.SystemLibrary.quit_editor()
