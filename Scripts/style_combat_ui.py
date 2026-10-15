"""Author distinct woodland exploration and combat HUDs through Unreal."""
from build_companion_combat import *

ATLAS = '/Game/Game/Combat/UI/T_CombatHUD_Atlas_v1.T_CombatHUD_Atlas_v1'
PLAYER_SHEET = '/Game/Game/Characters/Player/Sprites/chibi_idle_UE5_2048x1024_exact_grid.chibi_idle_UE5_2048x1024_exact_grid'
REGIONS = json.loads((ROOT / 'ContentSource/UI/CombatHUD_Atlas_v1.json').read_text())
BROWN = '(R=0.12,G=0.055,B=0.022,A=1)'
CREAM = '(R=1,G=0.91,B=0.72,A=1)'
GREEN = '(R=0.27,G=0.48,B=0.22,A=1)'


def coord(value):
    return f'(* {value} ui)'


def rect(x, y, w, h, color):
    return f'(HUD|DrawRect :RectColor "{color}" :ScreenX {coord(x)} :ScreenY {coord(y)} :ScreenW {coord(w)} :ScreenH {coord(h)})\n'


def text(value, x, y, scale=1.0, color=BROWN):
    return f'(HUD|DrawText :Text {value} :TextColor "{color}" :ScreenX {coord(x)} :ScreenY {coord(y)} :Font "/Engine/EngineFonts/Roboto.Roboto" :Scale (* {scale} ui))\n'


def art(region, x, y, w, h):
    left, top, right, bottom = REGIONS['regions'][region]
    u, v = left / REGIONS['width'], top / REGIONS['height']
    uw, vh = (right-left) / REGIONS['width'], (bottom-top) / REGIONS['height']
    return f'(HUD|DrawTexture :Texture "{ATLAS}" :ScreenX {coord(x)} :ScreenY {coord(y)} :ScreenW {coord(w)} :ScreenH {coord(h)} :TextureU {u} :TextureV {v} :TextureUWidth {uw} :TextureVHeight {vh} :BlendMode "BLEND_Translucent")\n'


def get(name):
    return f'(Class|BPCompanionCombat|Get{name} :self director)'


def health(key, maximum, x, y, width, color):
    fraction = f'(Math|Float|Clamp(Float) (/ {get(key)} {maximum}.0) 0.0 1.0)'
    fill_width = f'(* {width-2} {fraction})'
    return (rect(x, y, width, 6, BROWN)
            + rect(f'(+ {x} 1.0)', f'(+ {y} 1.0)', width-2, 4, '(R=0.23,G=0.15,B=0.085,A=1)')
            + rect(f'(+ {x} 1.0)', f'(+ {y} 1.0)', fill_width, 4, color)
            + rect(f'(+ {x} 1.0)', f'(+ {y} 1.0)', fill_width, 1, '(R=1,G=0.9,B=0.65,A=0.28)'))


def centered(value, x, y, scale=.95):
    return f'(CallFunction|DrawCenteredLabel :Value {value} :CenterX {x} :CenterY {y} :UIScale ui :TextScale {scale})\n'


def player_face(x, y, size):
    # Face/shoulders from the front-facing idle sprite (source cell starts 28,22).
    # Reuse the actual player art and transparency, without introducing a variant.
    return f'''(HUD|DrawTexture :Texture "{PLAYER_SHEET}"
     :ScreenX {coord(x)} :ScreenY {coord(y)} :ScreenW {coord(size)} :ScreenH {coord(f'(* {size} 0.9)')}
     :TextureU {28/2048} :TextureV {22/1024} :TextureUWidth {200/2048} :TextureVHeight {180/1024}
     :BlendMode "BLEND_Translucent")\n'''


def status_card(key, maximum, y, title, icon, color):
    # Separate the round medallion from the nameplate so it cannot stretch.
    body = art('toast', 88, f'(+ {y} 10.0)', 242, 60)
    body += art('ring', 24, y, 80, 80)
    body += (player_face(37, f'(+ {y} 16.0)', 54) if icon == 'player'
             else art(icon, 42, f'(+ {y} 18.0)', 44, 44))
    body += centered(json.dumps(title), 164, f'(+ {y} 36.0)')
    amount = f'(Utilities|String|Append (Utilities|String|ToString(Integer) (Math|Float|Truncate {get(key)})) " / {maximum}")'
    body += centered(amount, 258, f'(+ {y} 36.0)')
    body += health(key, maximum, 112, f'(+ {y} 50.0)', 194, color)
    return body


def portrait(species, x, y, size):
    return ''.join(f'(if (== {species} "{name}") {art(name,x,y,size,size)})\n'
                   for name in ['Mossling', 'Emberfox', 'Rivercub', 'Moonmoth'])


def action(icon, key, title, x, y, ready=None):
    body = art('ring', x, y, 64, 64) + art(icon, f'(+ {x} 14.0)', f'(+ {y} 10.0)', 36, 38)
    body += art('toast', f'(- {x} 12.0)', f'(+ {y} 53.0)', 88, 27)
    body += text(json.dumps(key), f'(+ {x} 22.0)', f'(+ {y} 55.0)', .85)
    body += art('toast', f'(- {x} 17.0)', f'(+ {y} 79.0)', 98, 25)
    body += text(title, f'(- {x} 1.0)', f'(+ {y} 82.0)', .82)
    if ready:
        body += f'(if (< now {get(ready)}) ' + text('"Resting"', f'(+ {x} 2.0)', f'(+ {y} 28.0)', .75, CREAM) + ')\n'
        if ready == 'HealReadyAt':
            body += rect(x, f'(+ {y} 48.0)', f'(* 64.0 (Math|Float|Clamp(Float) (- 1.0 (/ (- {get(ready)} now) 8.0)) 0.0 1.0))', 3, GREEN)
    return body


def author():
    backup(HUD, 'EventGraph')
    # UI-only observation: no changes to damage, healing, saves or combat timing.
    for name, typ in [('HealthSampled','bool'), ('LastSeenPlayerHealth','float'),
                      ('LastSeenHealReadyAt','float'), ('HealthRevealUntil','float')]:
        var(HUD, name, typ)
    graph(HUD, 'DrawCenteredLabel', '''(fn DrawCenteredLabel (Value CenterX CenterY UIScale TextScale)
    (bind (width height) (HUD|GetTextSize :Text Value :Font "/Engine/EngineFonts/Roboto.Roboto" :Scale (* UIScale TextScale)))
    (HUD|DrawText :Text Value :TextColor "(R=0.12,G=0.055,B=0.022,A=1)"
     :ScreenX (- (* CenterX UIScale) (/ width 2.0))
     :ScreenY (- (* CenterY UIScale) (/ height 2.0))
     :Font "/Engine/EngineFonts/Roboto.Roboto" :Scale (* UIScale TextScale)))''',
          [('Value','string',None),('CenterX','float',None),('CenterY','float',None),
           ('UIScale','float',None),('TextScale','float',None)])
    body = '''(bind ui (Math|Float|Min(Float) 1.25 (Math|Float|Min(Float) (/ SizeX 1280.0) (/ SizeY 720.0))))
    (bind bottom (- (/ SizeY ui) 24.0))
    (bind right (- (/ SizeX ui) 24.0))
    (bind now (Utilities|Time|GetGameTimeinSeconds))
    '''
    body += f'''(if (not (Variables|Default|GetHealthSampled))
     (Variables|Default|SetHealthSampled true)
     (Variables|Default|SetLastSeenPlayerHealth {get('PlayerHealth')})
     (Variables|Default|SetLastSeenHealReadyAt {get('HealReadyAt')})
     (else (if (or (!= {get('PlayerHealth')} (Variables|Default|GetLastSeenPlayerHealth))
                   (!= {get('HealReadyAt')} (Variables|Default|GetLastSeenHealReadyAt)))
      (Variables|Default|SetHealthRevealUntil (+ now 4.0))
      (Variables|Default|SetLastSeenPlayerHealth {get('PlayerHealth')})
      (Variables|Default|SetLastSeenHealReadyAt {get('HealReadyAt')}))))'''
    # Combat always has vitals. Exploration reveals HP briefly after changes,
    # then keeps only a small reminder at half health or below.
    body += f'(if {get("InCombat")} '
    for key, maximum, y, title, icon, color in [
        ('PlayerHealth', 100, '(- bottom 250.0)', 'You', 'player', '(R=0.58,G=0.20,B=0.16,A=1)'),
        ('CompanionHealth', 60, '(- bottom 160.0)', 'Party HP', 'command', GREEN),
    ]:
        body += status_card(key, maximum, y, title, icon, color)
    body += f'(if (> {get("RetreatUntil")} now) ' + centered('"Recovering"', 209, '(- bottom 82.0)', .75) + ')'
    body += '(else (if (< now (Variables|Default|GetHealthRevealUntil)) '
    body += status_card('PlayerHealth', 100, '(- bottom 160.0)', 'You', 'player', '(R=0.58,G=0.20,B=0.16,A=1)')
    body += f'(else (if (<= {get("PlayerHealth")} 50.0) '
    body += art('toast', 132, '(- bottom 126.0)', 124, 40)
    body += art('ring', 98, '(- bottom 129.0)', 46, 46)
    body += player_face(104, '(- bottom 121.3)', 34)
    body += centered(f'(Utilities|String|Append (Utilities|String|ToString(Integer) (Math|Float|Truncate {get("PlayerHealth")})) " / 100")', 194, '(- bottom 107.0)', .82)
    body += health('PlayerHealth', 100, 152, '(- bottom 97.0)', 84, '(R=0.58,G=0.20,B=0.16,A=1)') + ')))))'
    for i in range(3):
        # Ring centers are 79, 177 and 275: symmetric about the card's 177.
        x = 50.5 + i*98
        body += art('ring', x, '(- bottom 66.0)', 57, 57)
        occupied = f'(> (Utilities|Array|Length {get("Roster")}) {i})'
        species = f'(Utilities|Array|Get(acopy) {get("Roster")} {i})'
        body += f'(if {occupied} ' + portrait(species, x+8.5, '(- bottom 57.5)', 40)
        body += '(else ' + text('"+"', x+23, '(- bottom 49.0)', 1.1, CREAM) + '))'
        body += art('toast', x+16.5, '(- bottom 22.0)', 24, 22)
        body += centered(json.dumps(str(i+1)), x+28.5, '(- bottom 11.0)', .85)
        active = f'(and {occupied} (or {get("InCombat")} (== {get("ActiveIndex")} {i})))'
        body += f'(if {active} ' + rect(x+14.5, '(+ bottom 5.0)', 28, 2, GREEN) + ')'
    # An action diamond maps directly to the prototype's existing controls.
    body += f'(if {get("InCombat")} '
    body += action('command', 'Q', '"Command"', '(- right 204.0)', '(- bottom 162.0)')
    body += action('heal', 'H', '"Heal"', '(- right 64.0)', '(- bottom 162.0)', 'HealReadyAt')
    body += f'(if {get("UseSpell")} ' + action('frost', 'LMB', '"Frost bolt"', '(- right 134.0)', '(- bottom 239.0)', 'AttackReadyAt')
    body += '(else ' + action('sword', 'LMB', '"Sword"', '(- right 134.0)', '(- bottom 239.0)', 'AttackReadyAt') + '))'
    body += f'(if {get("UseSpell")} ' + action('sword', 'V', '"To sword"', '(- right 134.0)', '(- bottom 85.0)')
    body += '(else ' + action('frost', 'V', '"To frost"', '(- right 134.0)', '(- bottom 85.0)') + '))'
    body += ')'
    body += f'(if (< now {get("MessageUntil")}) '
    body += art('toast', '(- (/ right 2.0) 300.0)', 59, 624, 78)
    body += text(f'(Utilities|String|GetSubstring :SourceString {get("Message")} :StartIndex 0 :Length 74)', '(- (/ right 2.0) 190.0)', 80, .88)
    body += text(f'(Utilities|String|GetSubstring :SourceString {get("Message")} :StartIndex 74 :Length 74)', '(- (/ right 2.0) 190.0)', 99, .88) + ')'
    code = f'''(event EventReceiveDrawHUD (SizeX SizeY)
    (for actor (Actor|GetAllActorsOfClass :ActorClass "{DIRECTOR}_C")
     (bind director (Utilities|Casting|CastToBP_CompanionCombat :Object actor)
      (:then (if (Class|BPCompanionCombat|CanAct :self director) {body})) (:CastFailed))))'''
    graph(HUD, 'EventGraph', code)
    call('compile_blueprint', {'blueprint': ref(HUD), 'warnings_as_errors': True})
    print('Saved combat HUD:', call('save_assets', {'asset_paths': [HUD]}, ASSET))


if __name__ == '__main__':
    author()
