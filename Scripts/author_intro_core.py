"""Create Evergrove's intro assets, persistent preferences, and menu state."""
from build_companion_combat import *
from woodland_fx_graph import props
F='/Game/Game/UI';GI=F+'/BP_EvergroveGameInstance.BP_EvergroveGameInstance';PREF=F+'/BP_EvergroveOptionsSave.BP_EvergroveOptionsSave';MENU=F+'/BP_EvergroveIntroHUD.BP_EvergroveIntroHUD';MODE=F+'/BP_EvergroveIntroMode.BP_EvergroveIntroMode'
OUT=ROOT/'Saved/EvergroveIntroAudit';OUT.mkdir(exist_ok=True)
TEX='editor_toolset.toolsets.texture.TextureTools'
for name,parent in [(GI,'/Script/Engine.GameInstance'),(PREF,'/Script/Engine.SaveGame'),(MENU,'/Script/Engine.HUD'),(MODE,'/Script/Engine.GameModeBase')]:create(name,parent)
for name in ['T_EvergroveBackground','T_EvergroveLogo']:
    folder='/Game/Game/UI/Evergrove';path=folder+'/'+name
    if not call('exists',{'path':path},ASSET):call('import_file',{'folder_path':folder,'asset_name':name,'source_file':str(ROOT/'ContentSource/EvergroveIntro'/(name+'.png'))},TEX)
    props(ref(path+'.'+name),{'LODGroup':'TEXTUREGROUP_UI','Filter':'TF_Bilinear','MipGenSettings':'TMGS_NoMipmaps','NeverStream':True,'CompressionSettings':'TC_EditorIcon'})
for n,t in [('MasterVolume','float'),('Brightness','float'),('MenuMotion','bool')]:var(PREF,n,t)
defaults(PREF,{'MasterVolume':1,'Brightness':1,'MenuMotion':True})
for n,t in [('PendingLoad','bool'),('PendingSlot','string'),('MenuSaveSlot','string'),('OptionsSlot','string'),('MenuError','string'),('MasterVolume','float'),('Brightness','float'),('MenuMotion','bool'),('PreferenceMix','/Script/Engine.SoundMix')]:var(GI,n,t)
for n in ['PendingLoad','PendingSlot','MenuSaveSlot','OptionsSlot','MenuError','MasterVolume','Brightness','MenuMotion']:
    call('set_variable_instance_editable',{'blueprint':ref(GI),'variable_name':n,'instance_editable':True})
graph(GI,'LoadPreferences',f'''(fn LoadPreferences ()
 (if (SaveGame|DoesSaveGameExist :SlotName (Variables|Default|GetOptionsSlot) :UserIndex 0)
  (bind saved (Utilities|Casting|CastToBP_EvergroveOptionsSave :Object (SaveGame|LoadGameFromSlot :SlotName (Variables|Default|GetOptionsSlot) :UserIndex 0))
   (:then
    (Variables|Default|SetMasterVolume (Math|Float|Clamp(Float) (Class|BPEvergroveOptionsSave|GetMasterVolume :self saved) 0.0 1.0))
    (Variables|Default|SetBrightness (Math|Float|Clamp(Float) (Class|BPEvergroveOptionsSave|GetBrightness :self saved) 0.8 1.2))
    (Variables|Default|SetMenuMotion (Class|BPEvergroveOptionsSave|GetMenuMotion :self saved))) (:CastFailed))))''')
graph(GI,'SavePreferences',f'''(fn SavePreferences ()
 (bind saved (Utilities|Casting|CastToBP_EvergroveOptionsSave :Object (SaveGame|CreateSaveGameObject :SaveGameClass "{PREF}_C"))
  (:then
   (Class|BPEvergroveOptionsSave|SetMasterVolume :self saved :MasterVolume (Variables|Default|GetMasterVolume))
   (Class|BPEvergroveOptionsSave|SetBrightness :self saved :Brightness (Variables|Default|GetBrightness))
   (Class|BPEvergroveOptionsSave|SetMenuMotion :self saved :MenuMotion (Variables|Default|GetMenuMotion))
   (bind written (SaveGame|SaveGameToSlot :SaveGameObject saved :SlotName (Variables|Default|GetOptionsSlot) :UserIndex 0))) (:CastFailed)))''')
graph(GI,'ValidObject','''(fn ValidObject (Object) (Utilities|IsValid Object (:"Is Valid" (return true)) (:"Is Not Valid" (return false))))''',[('Object','/Script/CoreUObject.Object',None)],[('Valid','bool',None)])
graph(GI,'ApplyPreferences','''(fn ApplyPreferences ()
 (if (not (CallFunction|ValidObject :Object (Variables|Default|GetPreferenceMix)))
  (bind mix (Utilities|Casting|CastToSoundMix :Object (Game|ConstructObjectfromClass :Class "/Script/Engine.SoundMix" :self self))
   (:then (Variables|Default|SetPreferenceMix mix)
    (Audio|PushSoundMixModifier :InSoundMixModifier mix)) (:CastFailed)))
 (Audio|SetSoundMixClassOverride :InSoundMixModifier (Variables|Default|GetPreferenceMix) :InSoundClass "/Engine/EngineSounds/Master.Master" :Volume (Variables|Default|GetMasterVolume) :Pitch 1.0 :FadeInTime 0.15 :bApplyToChildren true)
 (Development|ExecuteConsoleCommand :Command (Utilities|String|Append "r.TonemapperGamma " (Utilities|String|ToString(Float) (* (Variables|Default|GetBrightness) 2.2)))))''')
graph(GI,'EventGraph','(event EventInit (CallFunction|LoadPreferences))')
defaults(GI,{'PendingLoad':False,'PendingSlot':'AdventureRPG_WoodlandBlockout','MenuSaveSlot':'AdventureRPG_WoodlandBlockout','OptionsSlot':'Evergrove_Options','MenuError':'','MasterVolume':1,'Brightness':1,'MenuMotion':True})
defaults(MODE,{'HUDClass':MENU+'_C','DefaultPawnClass':None,'PlayerControllerClass':'/Script/Engine.PlayerController','bStartPlayersAsSpectators':True})
graph(MODE,'EventGraph',f'''(event Game|EventInitializeHUDForPlayer (NewPlayer) (HUD|ClientSetHUD :self NewPlayer :NewHUDClass "{MENU}_C"))''')
call('save_assets',{'asset_paths':[]},ASSET)
print('EVERGROVE_INTRO_CORE_SAVED',flush=True)
