"""Import the Blender-authored woodland kit and dress the existing playable map.

Run with --import, --dress, or --verify. Does not alter gameplay Blueprints.
"""
from build_companion_combat import call, ref, ASSET, SCENE, OBJ
import json, random, sys, math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'ContentSource/Woodland'
AUDIT=ROOT/'Saved/WoodlandArtAudit'
AUDIT.mkdir(exist_ok=True)
FOLDER='/Game/Environment/Woodland'
SM='editor_toolset.toolsets.static_mesh.StaticMeshTools'
ACT='editor_toolset.toolsets.actor.ActorTools'
MAT='editor_toolset.toolsets.material.MaterialTools'
TEX='editor_toolset.toolsets.texture.TextureTools'
ATLAS=FOLDER+'/M_Woodland_PixelAtlas.M_Woodland_PixelAtlas'
TAG='WoodlandBlenderArt'

def props(obj,values):
    if not call('set_properties',{'instance':obj,'values':json.dumps(values)},OBJ):
        raise RuntimeError('Could not set '+str(values)+' on '+str(obj))

def import_kit():
    manifest=json.loads((SOURCE/'manifest.json').read_text())
    report=[]
    for item in manifest:
        print('Importing '+item['name'],flush=True)
        mesh=ref(FOLDER+'/'+item['name']+'.'+item['name'])
        imported=[mesh] if call('exists',{'path':FOLDER+'/'+item['name']},ASSET) else call('import_file',{'folder_path':FOLDER,'asset_name':item['name'],'source_file':item['file'],'import_materials':True,'import_textures':True,'combine_meshes':True},SM)
        slots=call('get_material_slots',{'mesh':mesh},SM)
        for slot in slots:call('set_material',{'mesh':mesh,'slot_name':slot,'material':ref(ATLAS)},SM)
        call('remove_collisions',{'mesh':mesh},SM)
        bounds=call('get_bounds',{'mesh':mesh},SM)
        report.append({'name':item['name'],'imported':imported,'bounds_cm':bounds})
    texture_name='T_Woodland_Atlas_Crisp'
    texture=ref(FOLDER+'/'+texture_name+'.'+texture_name) if call('exists',{'path':FOLDER+'/'+texture_name},ASSET) else call('import_file',{'folder_path':FOLDER,'asset_name':texture_name,'source_file':str(SOURCE/'T_Woodland_PixelAtlas.png')},TEX)[0]
    props(texture,{'Filter':'TF_Nearest','LODGroup':'TEXTUREGROUP_Pixels2D','NeverStream':True})
    props(ref(ATLAS),{'TwoSided':True})
    expressions=call('get_expressions',{'material_or_function':ref(ATLAS)},MAT)
    # FBX imports the image node; keep it explicitly bound to the shared atlas.
    for expr in expressions:
        cls=call('get_class',{'instance':expr},OBJ)
        if 'TextureSample' in str(cls):props(expr,{'Texture':texture['refPath']})
    rough=call('add_expression',{'material_or_function':ref(ATLAS),'expression_class':ref('/Script/Engine.MaterialExpressionConstant')},MAT)
    props(rough,{'R':.91})
    call('connect_to_output',{'expression':rough,'output_name':'','material_property':'MP_Roughness'},MAT)
    spec=call('add_expression',{'material_or_function':ref(ATLAS),'expression_class':ref('/Script/Engine.MaterialExpressionConstant')},MAT)
    props(spec,{'R':.12})
    call('connect_to_output',{'expression':spec,'output_name':'','material_property':'MP_Specular'},MAT)
    call('recompile',{'material_or_function':ref(ATLAS)},MAT)
    call('save_assets',{'asset_paths':[FOLDER+'/'+x['name'] for x in manifest]+[ATLAS,texture['refPath']]},ASSET)
    (AUDIT/'imports.json').write_text(json.dumps(report,indent=2))
    print('IMPORTED_MODELS='+str(len(report)),flush=True)

def art(name,mesh,x,y,z=2,scale=1,yaw=0):
    a=call('add_to_scene_from_asset',{'asset_path':FOLDER+'/SM_Woodland_'+mesh,'name':'WoodlandArt_'+name,'xform':{'location':{'x':x,'y':y,'z':z},'rotation':{'pitch':0,'yaw':yaw,'roll':0},'scale':{'x':scale,'y':scale,'z':scale}},'snap_to_ground':False},SCENE)
    if not a:raise RuntimeError('Failed to place '+name)
    call('set_label',{'actor':a,'label':'WoodlandArt_'+name},ACT)
    call('add_tag',{'actor':a,'tag':TAG},ACT)
    call('set_actor_folder',{'actor':a,'folder_path':'Woodland/Blender Art'},SCENE)
    c=call('get_components',{'actor':a,'component_type':ref('/Script/Engine.StaticMeshComponent')},ACT)[0]
    props(c,{'bUseDefaultCollision':False,'BodyInstance':{'CollisionProfileName':'NoCollision','CollisionEnabled':'NoCollision'},'bCanEverAffectNavigation':False})
    return a

def dress():
    if call('get_current_level',{},SCENE)!='/Game/Maps/L_WoodlandBlockout':raise RuntimeError('Open the woodland map first')
    if call('find_actors',{'name':'','tag':TAG,'collision_channels':[]},SCENE):raise RuntimeError('Art already placed; inspect before rebuilding')
    actors=call('find_actors',{'name':'','tag':'','collision_channels':[]},SCENE)
    snapshot=[];trees=[];rocks=[]
    for a in actors:
        label=call('get_label',{'actor':a},ACT)
        xf=call('get_actor_transform',{'actor':a},ACT)
        snapshot.append({'actor':a,'label':label,'transform':xf})
        if label.startswith('Woodland_Trunk_'):trees.append((label,xf['location']))
        if label.startswith('Woodland_Rock_'):rocks.append((label,xf['location']))
        hidden=(label.startswith(('Woodland_Trunk_','Woodland_Crown_','Woodland_Rock_','Woodland_Clearing')) or label in ['Woodland_ForestGround','Woodland_HubGround','Woodland_Trail','Woodland_HubWalk','Woodland_Boundary'])
        if hidden:
            components=call('get_components',{'actor':a,'component_type':ref('/Script/Engine.StaticMeshComponent')},ACT)
            for c in components:
                old=call('get_properties',{'instance':c,'properties':['bVisible','bHiddenInGame','CastShadow']},OBJ)
                snapshot[-1]['component_before']={'component':c,'properties':json.loads(old)}
                props(c,{'bVisible':False,'bHiddenInGame':True,'CastShadow':False})
    (AUDIT/'scene_before.json').write_text(json.dumps(snapshot,indent=2))
    rng=random.Random(104);created=[]
    created.append(art('Ground','GroundSkin',1600,0,.8))
    created.append(art('Trail','TrailSkin',0,0,6))
    for i,(label,p) in enumerate(sorted(trees)):
        scale=rng.uniform(.78,1.04)
        # Near-side trees are shorter, keeping the fixed game camera readable.
        if p['y']>600:scale*=.68
        created.append(art('Tree_'+label.rsplit('_',1)[-1],'Broadleaf_'+chr(65+i%3),p['x'],p['y'],3,scale,rng.uniform(0,360)))
    for i,(label,p) in enumerate(sorted(rocks)):
        created.append(art('Rock_'+str(i),'MossRock_'+chr(65+i%2),p['x'],p['y'],2,.68,rng.uniform(0,360)))
    # Dense overlapping backdrop crowns; these are beyond the collision boundary.
    for row in range(2):
        for i,x in enumerate(range(-1250,4651,280)):
            y=-1210-row*330+rng.uniform(-70,70)
            if -700<x<700:continue  # Leave the guild front and NPCs readable.
            created.append(art('BackTree_'+str(row)+'_'+str(i),'Broadleaf_'+chr(65+(i+row)%3),x+rng.uniform(-65,65),y,2,rng.uniform(.9,1.25),rng.uniform(0,360)))
    for i,x in enumerate(range(-1300,4651,350)):
        created.append(art('FrontTree_'+str(i),'Broadleaf_'+chr(65+i%3),x,1450+rng.uniform(-35,35),2,rng.uniform(.58,.76),rng.uniform(0,360)))
    for side,x in enumerate([-1280,4540]):
        for i,y in enumerate(range(-1150,1301,330)):
            created.append(art('SideTree_'+str(side)+'_'+str(i),'Broadleaf_'+chr(65+i%3),x,y,2,rng.uniform(.75,.98),rng.uniform(0,360)))
    # Low border vegetation hides the collision rails without closing the lanes.
    for i,x in enumerate(range(-1000,4351,190)):
        for side,y in enumerate([-1080,1100]):
            if -720<x<720 and y<0:continue
            created.append(art('BorderBush_'+str(i)+'_'+str(side),'Bush',x+rng.uniform(-40,40),y,2,rng.uniform(.7,1.05),rng.uniform(0,360)))
    # A handful of landmarks around each clearing; objective spawn rows stay open.
    for i,(x,y,mesh,scale) in enumerate([(1380,-780,'FallenLog',1),(2330,780,'Stump',1),(3240,-910,'FallenLog',.9),(3970,780,'MossRock_A',1.05),(-800,630,'Stump',.8)]):
        created.append(art('Landmark_'+str(i),mesh,x,y,3,scale,rng.uniform(0,360)))
    for i in range(200):
        x=rng.uniform(1150,4180);y=rng.choice([-1,1])*rng.uniform(800,1160)
        mesh='Fern' if i%5==0 else 'Wildflowers' if i%11==0 else 'Grass'
        created.append(art('Undergrowth_'+str(i),mesh,x,y,3,rng.uniform(.6,1.25),rng.uniform(0,360)))
    # Ragged grass edges define a clean, walkable dirt trail.
    for i,x in enumerate(range(550,4151,105)):
        for side in [-1,1]:
            created.append(art('TrailGrass_'+str(i)+'_'+str(side),'Grass',x+rng.uniform(-30,30),side*rng.uniform(180,240),6,rng.uniform(.35,.65),rng.uniform(0,360)))
    (AUDIT/'created_actors.json').write_text(json.dumps(created,indent=2))
    print('PLACED_ART_ACTORS='+str(len(created)),flush=True)
    call('save_assets',{'asset_paths':[]},ASSET)
    print('Saved all dirty packages, including World Partition external actors.',flush=True)

def verify():
    arts=call('find_actors',{'name':'','tag':TAG,'collision_channels':[]},SCENE)
    problems=[];counts={}
    for a in arts:
        c=call('get_components',{'actor':a,'component_type':ref('/Script/Engine.StaticMeshComponent')},ACT)[0]
        p=json.loads(call('get_properties',{'instance':c,'properties':['StaticMesh','bCanEverAffectNavigation','BodyInstance']},OBJ))
        name=str(p['StaticMesh']);counts[name]=counts.get(name,0)+1
        if p['bCanEverAffectNavigation']:problems.append({'actor':a,'reason':'Decorative art affects navigation'})
        if p['BodyInstance'].get('collisionEnabled')!='NoCollision':problems.append({'actor':a,'reason':'Decorative art has collision'})
    report={'level':call('get_current_level',{},SCENE),'art_actor_count':len(arts),'mesh_instances':counts,'problems':problems}
    (AUDIT/'validation.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2),flush=True)
    if problems:raise RuntimeError('Woodland art validation failed')

if __name__=='__main__':
    if '--import' in sys.argv:import_kit()
    if '--dress' in sys.argv:dress()
    if '--verify' in sys.argv:verify()
