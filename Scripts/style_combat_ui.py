"""Restyle only the combat HUD using the project's existing dialogue artwork."""
from build_companion_combat import *
FRAME='/Game/Game/UI/Whimsical_Woodland_RPG_Dialogue_Frame.Whimsical_Woodland_RPG_Dialogue_Frame'
BROWN='(R=0.12,G=0.055,B=0.022,A=1)'
MUTED='(R=0.27,G=0.16,B=0.075,A=1)'
def rect(x,y,w,h,color):
    return f'(HUD|DrawRect :RectColor "{color}" :ScreenX (* {x} ui) :ScreenY (* {y} ui) :ScreenW (* {w} ui) :ScreenH (* {h} ui))'
def text(value,x,y,scale=1.0,color=BROWN):
    return f'(HUD|DrawText :Text {value} :TextColor "{color}" :ScreenX (* {x} ui) :ScreenY (* {y} ui) :Font "/Engine/EngineFonts/Roboto.Roboto" :Scale (* {scale} ui))'
def frame(x,y,w,h):
    # The existing dialogue image includes transparent headroom above its frame.
    return f'''(HUD|DrawTexture :Texture "{FRAME}" :ScreenX (* {x} ui) :ScreenY (* {y} ui) :ScreenW (* {w} ui) :ScreenH (* {h} ui) :TextureU 0.0 :TextureV 0.38 :TextureUWidth 1.0 :TextureVHeight 0.62 :BlendMode "BLEND_Translucent")'''
def author():
    backup(HUD,'EventGraph')
    body='''(bind ui (Math|Float|Min(Float) 1.0 (Math|Float|Min(Float) (/ SizeX 1000.0) (/ SizeY 620.0))))
'''
    body+=frame(16,12,650,235)
    body+=text('"Companions"',90,92,1.2)
    body+=text('(select (Class|BPCompanionCombat|GetUseSpell :self director) "Frost bolt" "Sword")',490,47,1.05,'(R=1,G=0.9,B=0.65,A=1)')
    for x,label,key,maximum,color in [(90,'You','PlayerHealth',100,'(R=0.55,G=0.16,B=0.14,A=1)'),(350,'Companion','CompanionHealth',60,'(R=0.2,G=0.36,B=0.17,A=1)')]:
        value=f'(Utilities|String|Append "{label}   " (Utilities|String|Append (Utilities|String|ToString(Integer) (Math|Float|Truncate (Class|BPCompanionCombat|Get{key} :self director))) " / {maximum}"))'
        body+=text(value,x,114,.9)
        body+=rect(x,128,226,8,'(R=0.28,G=0.15,B=0.055,A=1)')
        body+=rect(x+2,130,222,4,'(R=0.76,G=0.62,B=0.39,A=1)')
        body+=f'''(HUD|DrawRect :RectColor "{color}" :ScreenX (* {x+2} ui) :ScreenY (* 130.0 ui) :ScreenW (* (* 222.0 (/ (Class|BPCompanionCombat|Get{key} :self director) {maximum}.0)) ui) :ScreenH (* 4.0 ui))'''
    for i,x in enumerate([90,260,430]):
        body+=rect(x,140,156,26,'(R=0.49,G=0.32,B=0.13,A=0.65)')
        body+=rect(x+1,141,154,24,'(R=0.92,G=0.8,B=0.58,A=0.95)')
        body+=f'''(if (== (Class|BPCompanionCombat|GetActiveIndex :self director) {i})
 {rect(x+1,141,154,3,'(R=0.22,G=0.4,B=0.16,A=1)')})'''
        body+=f'''(if (> (Utilities|Array|Length (Class|BPCompanionCombat|GetRoster :self director)) {i})
 {text(f'(Utilities|String|Append "{i+1}  " (Utilities|String|ToString(Name) (Utilities|Array|Get(acopy) (Class|BPCompanionCombat|GetRoster :self director) {i})))',x+10,148,.9)}
 (else {text(f'"{i+1}  Empty"',x+10,148,.9,MUTED)}))'''
    body+=text('"LMB  Attack     V  Sword / spell     Q  Command     H  Heal"',110,174,.75,MUTED)
    body+=text('"1 - 3  Summon     Backspace  Release     E  Interact"',110,189,.75,MUTED)
    body+='''(if (< (Utilities|Time|GetGameTimeinSeconds) (Class|BPCompanionCombat|GetMessageUntil :self director))
'''+frame(16,248,650,112)
    body+=text('(Utilities|String|GetSubstring :SourceString (Class|BPCompanionCombat|GetMessage :self director) :StartIndex 0 :Length 82)',90,311,.82)
    body+=text('(Utilities|String|GetSubstring :SourceString (Class|BPCompanionCombat|GetMessage :self director) :StartIndex 82 :Length 100)',90,327,.82)+')'
    code=f'''(event EventReceiveDrawHUD (SizeX SizeY)
 (for actor (Actor|GetAllActorsOfClass :ActorClass "{DIRECTOR}_C")
  (bind director (Utilities|Casting|CastToBP_CompanionCombat :Object actor)
   (:then {body}) (:CastFailed))))'''
    graph(HUD,'EventGraph',code)
    call('save_assets',{'asset_paths':[HUD]},ASSET)
if __name__=='__main__':author()
