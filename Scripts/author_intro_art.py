"""Responsive canvas UI with original illustrated art, motion and named hit boxes."""
from build_companion_combat import *
import math
M='/Game/Game/UI/BP_EvergroveIntroHUD.BP_EvergroveIntroHUD'
BG='/Game/Game/UI/Evergrove/T_EvergroveBackground.T_EvergroveBackground';LOGO='/Game/Game/UI/Evergrove/T_EvergroveLogo.T_EvergroveLogo'
FONT='/Game/Game/UI/Evergrove/F_EvergroveStory.F_EvergroveStory'
def v(n):return '(Variables|Default|Get'+n+')'
def color(r,g,b,a=1):return f'(Math|Color|MakeColor {float(r)} {float(g)} {float(b)} {float(a) if isinstance(a,(int,float)) else a})'
GOLD=color(.77,.58,.27);CREAM=color(.94,.87,.68);INK=color(.08,.12,.09);MUTED=color(.45,.53,.43)
def sx(x):return f'(+ {v("UIX")} (* {x} {v("UIScale")}))'
def sy(y):return f'(+ {v("UIY")} (* {y} {v("UIScale")}))'
def rect(x,y,w,h,c):return f'(HUD|DrawRect :RectColor {c} :ScreenX {sx(x)} :ScreenY {sy(y)} :ScreenW (* {w} {v("UIScale")}) :ScreenH (* {h} {v("UIScale")}))\n'
def line(x,y,x2,y2,c,thick=1):return f'(HUD|DrawLine :StartScreenX {sx(x)} :StartScreenY {sy(y)} :EndScreenX {sx(x2)} :EndScreenY {sy(y2)} :LineColor {c} :LineThickness (* {thick} {v("UIScale")}))\n'
def text(value,x,y,scale=1,c=CREAM):return f'(HUD|DrawText :Text {value} :TextColor {c} :ScreenX {sx(x)} :ScreenY {sy(y)} :Font "{FONT}" :Scale (* (* {scale} 0.4166666667) {v("UIScale")}))\n'
def art(tex,x,y,w,h,tint=None):return f'(HUD|DrawTexture :Texture "{tex}" :ScreenX {sx(x)} :ScreenY {sy(y)} :ScreenW (* {w} {v("UIScale")}) :ScreenH (* {h} {v("UIScale")}) :TextureU 0.0 :TextureV 0.0 :TextureUWidth 1.0 :TextureVHeight 1.0 :TintColor {tint or color(1,1,1)} :BlendMode "BLEND_Translucent")\n'
def hit(name,x,y,w,h):return f'(HUD|AddHitBox :Position (Math|Vector2D|MakeVector2D {sx(x)} {sy(y)}) :Size (Math|Vector2D|MakeVector2D (* {w} {v("UIScale")}) (* {h} {v("UIScale")})) :InName (Utilities|Name|MakeLiteralName "{name}") :bConsumesInput true :Priority 10)\n'
def centered(value,x,y,scale=1,c=CREAM):
    return f'''(bind (width height) (HUD|GetTextSize :Text {value} :Font "{FONT}" :Scale (* (* {scale} 0.4166666667) {v('UIScale')})))
 (HUD|DrawText :Text {value} :TextColor {c} :ScreenX (- {sx(x)} (/ width 2.0)) :ScreenY (- {sy(y)} (/ height 2.0)) :Font "{FONT}" :Scale (* (* {scale} 0.4166666667) {v('UIScale')}))\n'''
def label(value,x,y,scale=1):return f'(CallFunction|DrawLabel :Value {value} :X {x} :Y {y} :TextScale {scale})\n'
def button(item,title,description,x,y,w,h,enabled='true'):
    return f'(CallFunction|DrawButton :Item {item} :Title {title} :Description {description} :X {x} :Y {y} :W {w} :H {h} :Enabled {enabled})\n'
q.BANK=M
for name,inputs in [('DrawLabel',[('Value','string',None),('X','float',None),('Y','float',None),('TextScale','float',None)]),('DrawButton',[('Item','int',None),('Title','string',None),('Description','string',None),('X','float',None),('Y','float',None),('W','float',None),('H','float',None),('Enabled','bool',None)]),('DrawBackdrop',[('SizeX','int',None),('SizeY','int',None)]),('DrawMain',[]),('DrawOptions',[]),('DrawConfirm',[]),('DrawLoading',[('SizeX','int',None),('SizeY','int',None)])]:q.function(name,inputs,[])
graph(M,'DrawLabel','(fn DrawLabel (Value X Y TextScale)\n'+centered('Value','X','Y','TextScale')+')',[('Value','string',None),('X','float',None),('Y','float',None),('TextScale','float',None)])
selected=f'(and Enabled (== Item {v("Selected")}))'
body='(fn DrawButton (Item Title Description X Y W H Enabled)\n'
body+='(if '+selected+'\n'+line('(- X 22.0)','(+ Y (/ H 2.0))','(- X 15.0)','(- (+ Y (/ H 2.0)) 7.0)',GOLD,2)+line('(- X 15.0)','(- (+ Y (/ H 2.0)) 7.0)','(- X 8.0)','(+ Y (/ H 2.0))',GOLD,2)+line('(- X 8.0)','(+ Y (/ H 2.0))','(- X 15.0)','(+ (+ Y (/ H 2.0)) 7.0)',GOLD,2)+line('(- X 15.0)','(+ (+ Y (/ H 2.0)) 7.0)','(- X 22.0)','(+ Y (/ H 2.0))',GOLD,2)+')\n'
title_color=f'(select Enabled (select {selected} {color(1.0,.80,.40)} {CREAM}) {MUTED})'
body+=centered('Title','(+ X (/ W 2.0))','(+ Y 18.0)',2.2,title_color).replace('(bind (width height)','(bind (titleWidth titleHeight)').replace('(/ width 2.0)','(/ titleWidth 2.0)').replace('(/ height 2.0)','(/ titleHeight 2.0)')
body+=centered('Description','(+ X (/ W 2.0))','(+ Y 43.0)',.9,title_color).replace('(bind (width height)','(bind (descWidth descHeight)').replace('(/ width 2.0)','(/ descWidth 2.0)').replace('(/ height 2.0)','(/ descHeight 2.0)')
body+=f'''(if Enabled
 (HUD|AddHitBox :Position (Math|Vector2D|MakeVector2D {sx('X')} {sy('Y')}) :Size (Math|Vector2D|MakeVector2D (* W {v('UIScale')}) (* H {v('UIScale')}))
  :InName (Utilities|String|StringToName (Utilities|String|Append (Utilities|String|Append "Page" (Utilities|String|ToString(Integer) {v('Page')})) (Utilities|String|Append "_Item" (Utilities|String|ToString(Integer) Item)))) :bConsumesInput true :Priority 10)))'''
graph(M,'DrawButton',body,[('Item','int',None),('Title','string',None),('Description','string',None),('X','float',None),('Y','float',None),('W','float',None),('H','float',None),('Enabled','bool',None)])
motion=f'(Class|BPEvergroveGameInstance|GetMenuMotion :self {v("Instance")})'
backdrop=f'''(fn DrawBackdrop (SizeX SizeY)
 (bind now (select {motion} (Utilities|Time|GetGameTimeinSeconds) 0.0))
 (bind zoom (* (Math|Float|Max(Float) (/ SizeX 1672.0) (/ SizeY 941.0)) (+ 1.035 (* (Math|Trig|Sin(Radians) (* now 0.11)) 0.006))))
 (bind bgWidth (* 1672.0 zoom)) (bind bgHeight (* 941.0 zoom))
 (HUD|DrawTexture :Texture "{BG}" :ScreenX (+ (/ (- SizeX bgWidth) 2.0) (* (Math|Trig|Sin(Radians) (* now 0.08)) 7.0))
  :ScreenY (+ (/ (- SizeY bgHeight) 2.0) (* (Math|Trig|Sin(Radians) (* now 0.06)) 4.0)) :ScreenW bgWidth :ScreenH bgHeight
  :TextureU 0.0 :TextureV 0.0 :TextureUWidth 1.0 :TextureVHeight 1.0 :BlendMode "BLEND_Opaque")
'''
for i in range(16):
    x=f'(- (* (Math|Float|Fraction (* (+ now {i*7.31}) 0.018)) 1360.0) 40.0)'
    y=f'(+ {float((i*83+35)%680)} (* (Math|Trig|Sin(Radians) (+ (* now 0.4) {i*1.7})) 18.0))'
    a=f'(+ 0.16 (* (Math|Trig|Sin(Radians) (+ (* now 0.8) {i*1.3})) 0.1))'
    backdrop+=rect(x,y,3,3,color(1,.78,.3,a))
    backdrop+=rect(f'(- {x} 2.0)',f'(- {y} 2.0)',7,7,color(1,.7,.24,.035))
backdrop+=')'
graph(M,'DrawBackdrop',backdrop,[('SizeX','int',None),('SizeY','int',None)])
main='(fn DrawMain ()\n'+art(LOGO,45,55,550,251)
main+=line(155,319,499,319,color(.75,.61,.34,.5))
for index,title,description in [(0,'New Game','"Begin a fresh woodland journey"'),(1,'Load Game',v('SaveSummary')),(2,'Options','"Display, sound and comfort"'),(3,'Quit Game','"Return to desktop"')]:
    main+=button(index,json.dumps(title),description,145,343+index*70,370,60,v('HasSave') if index==1 else 'true')
main+=text('"Arrows / W S   Select       Enter   Confirm"',145,646,.95,color(.85,.85,.69,.8))
main+=text(v('Status'),145,625,.85,color(.96,.74,.45))
main+=text('"F5 saves and F9 loads while exploring"',145,675,.8,color(.71,.76,.62,.65))
graph(M,'DrawMain',main+')')
options='(fn DrawOptions ()\n'+rect(0,0,1280,720,color(.012,.035,.026,.83))
options+=text('"Options"',115,73,3.3,GOLD)+text('"Fine-tune your woodland adventure"',117,125,1.1,CREAM)
quality=f'(select (== {v("OptQuality")} 0) "Low" (select (== {v("OptQuality")} 1) "Medium" (select (== {v("OptQuality")} 2) "High" (select (== {v("OptQuality")} 3) "Epic" "Custom"))))'
display=f'(select (== {v("OptDisplay")} 0) "Fullscreen" (select (== {v("OptDisplay")} 1) "Borderless" "Windowed"))'
frame=f'(select (== {v("OptFrame")} 0) "30 FPS" (select (== {v("OptFrame")} 1) "60 FPS" (select (== {v("OptFrame")} 2) "120 FPS" "Unlimited")))'
percent=lambda name:f'(Utilities|String|Append (Utilities|String|ToString(Integer) (Math|Float|Floor (+ (* {v(name)} 100.0) 0.5))) "%")'
rows=[('Display mode',display),('Graphics quality',quality),('Resolution scale',f'(Utilities|String|Append (Utilities|String|ToString(Integer) (Math|Float|Floor {v("OptScale")})) "%")'),('Frame-rate limit',frame),('VSync',f'(select {v("OptVSync")} "On" "Off")'),('Master volume',percent('OptVolume')),('Brightness',percent('OptBrightness')),('Background motion',f'(select {v("OptMotion")} "On" "Off")')]
for index,(title,value) in enumerate(rows):
    y=172+index*47
    options+=text(json.dumps(title),133,y+9,1.4,f'(select (== {v("Selected")} {index}) {GOLD} {CREAM})')
    options+=label(value,868,y+21,1.35)
    options+=label('"<"',700,y+21,1.5)+label('">"',1082,y+21,1.5)
    options+=hit(f'Option{index}_Minus',671,y,60,42)+hit(f'Option{index}_Plus',1051,y,60,42)
    options+=hit(f'Page1_Item{index}',128,y,500,42)
options+=text(v('Status'),128,560,1.05,GOLD)
options+=text('"Click a setting or its arrows  |  Arrow keys: select / adjust  |  Esc: back"',128,687,.85,CREAM)
options+=button(8,'"Apply"','"Save these settings"',112,600,310,60)+button(9,'"Back"','"Return to title"',486,600,310,60)+button(10,'"Restore Defaults"','"Select the recommended defaults"',860,600,310,60)
graph(M,'DrawOptions',options+')')
confirm='(fn DrawConfirm ()\n'+rect(0,0,1280,720,color(.012,.035,.026,.83))+label('"Begin a new journey?"',640,240,2.7)
confirm+=label('"Your existing save will stay available until you save again."',640,300,1.2)
confirm+=button(0,'"New Game"','"Start in the woodland"',260,390,330,64)+button(1,'"Back"','"Keep your current journey"',690,390,330,64)
graph(M,'DrawConfirm',confirm+')')
loading=f'''(fn DrawLoading (SizeX SizeY)
 (HUD|DrawRect :RectColor (Math|Color|MakeColor 0.025 0.06 0.04 (Math|Float|Clamp(Float) (/ {v('StartAge')} 0.3) 0.0 1.0)) :ScreenX 0.0 :ScreenY 0.0 :ScreenW SizeX :ScreenH SizeY)
 (CallFunction|DrawLabel :Value "Entering Evergrove..." :X 640.0 :Y 640.0 :TextScale 1.3))'''
graph(M,'DrawLoading',loading,[('SizeX','int',None),('SizeY','int',None)])
events=f'''(event EventBeginPlay (CallFunction|InitializeMenu))
 (event EventTick (DeltaSeconds) (CallFunction|UpdateMenu :Delta DeltaSeconds))
 (event EventReceiveDrawHUD (SizeX SizeY)
  (Variables|Default|SetUIScale (Math|Float|Min(Float) (/ SizeX 1280.0) (/ SizeY 720.0)))
  (Variables|Default|SetUIX (/ (- SizeX (* 1280.0 {v('UIScale')})) 2.0))
  (Variables|Default|SetUIY (/ (- SizeY (* 720.0 {v('UIScale')})) 2.0))
  (CallFunction|DrawBackdrop :SizeX SizeX :SizeY SizeY)
  (if (== {v('Page')} 0) (CallFunction|DrawMain))
  (if (== {v('Page')} 1) (CallFunction|DrawOptions))
  (if (== {v('Page')} 2) (CallFunction|DrawConfirm))
  (if {v('PendingStart')} (CallFunction|DrawLoading :SizeX SizeX :SizeY SizeY)))
 (event EventHitBoxClicked (BoxName) (CallFunction|HandleHit :BoxName BoxName))
 (event EventHitBoxBeginCursorOver (BoxName) (CallFunction|HandleHover :BoxName BoxName))
'''
graph(M,'EventGraph',events)
import author_intro_inputs
call('compile_blueprint',{'blueprint':ref(M),'warnings_as_errors':True})
call('save_assets',{'asset_paths':[]},ASSET)
print('EVERGROVE_ANIMATED_INTRO_ART_SAVED',flush=True)
