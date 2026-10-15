"""Import and apply the user's pixel woodland revision through Unreal editor tools."""
from build_companion_combat import call, ref, ROOT, ASSET, OBJ, SCENE
import json, sys

FOLDER='/Game/Environment/PixelWoodland'
SM='editor_toolset.toolsets.static_mesh.StaticMeshTools'
MAT='editor_toolset.toolsets.material.MaterialTools'
PROG='editor_toolset.toolsets.programmatic.ProgrammaticToolset'
SOURCE=ROOT/'ContentSource/PixelWoodland'
AUDIT=ROOT/'Saved/PixelWoodlandAudit'
AUDIT.mkdir(exist_ok=True)

def import_assets():
    for item in json.loads((SOURCE/'manifest.json').read_text()):
        item['name']+= '_Leafy' if 'Tree_' in item['name'] or item['name'].endswith('Bush') else ''
        print('Import '+item['name'],flush=True)
        if not call('exists',{'path':FOLDER+'/'+item['name']},ASSET):
            call('import_file',{'folder_path':FOLDER,'asset_name':item['name'],'source_file':item['file'],'import_materials':True,'import_textures':True,'combine_meshes':True},SM)
        call('remove_collisions',{'mesh':ref(FOLDER+'/'+item['name']+'.'+item['name'])},SM)
    atlas=ref(FOLDER+'/M_PixelWoodland.M_PixelWoodland')
    texture=ref(FOLDER+'/T_PixelWoodland_Palette.T_PixelWoodland_Palette')
    call('set_properties',{'instance':texture,'values':json.dumps({'Filter':'TF_Nearest','LODGroup':'TEXTUREGROUP_Pixels2D','NeverStream':True})},OBJ)
    call('set_properties',{'instance':atlas,'values':json.dumps({'TwoSided':True})},OBJ)
    # No texture noise, specular glare, or normal-map detail.
    for prop,value in [('MP_Roughness',1),('MP_Specular',0)]:
        node=call('add_expression',{'material_or_function':atlas,'expression_class':ref('/Script/Engine.MaterialExpressionConstant')},MAT)
        call('set_properties',{'instance':node,'values':json.dumps({'R':value})},OBJ)
        call('connect_to_output',{'expression':node,'output_name':'','material_property':prop},MAT)
    call('recompile',{'material_or_function':atlas},MAT)
    call('save_assets',{'asset_paths':[]},ASSET)

BATCH=r'''
import json, math

def find(tag='',name=''):
    return execute_tool('editor_toolset.toolsets.scene.SceneTools.find_actors',json.dumps({'name':name,'tag':tag,'collision_channels':[]}))['returnValue']
def components(a):
    return execute_tool('editor_toolset.toolsets.actor.ActorTools.get_components',json.dumps({'actor':a,'component_type':{'refPath':'/Script/Engine.StaticMeshComponent'}}))['returnValue']
def properties(c,names):
    return json.loads(execute_tool('editor_toolset.toolsets.object.ObjectTools.get_properties',json.dumps({'instance':c,'properties':names}))['returnValue'])
def setprops(c,values):
    result=execute_tool('editor_toolset.toolsets.object.ObjectTools.set_properties',json.dumps({'instance':c,'values':json.dumps(values)}))['returnValue']
    if not result:raise RuntimeError(str(values))
def add(name,mesh,x,y,scale=1,z=3):
    a=execute_tool('editor_toolset.toolsets.scene.SceneTools.add_to_scene_from_asset',json.dumps({'asset_path':'/Game/Environment/PixelWoodland/SM_Pixel_'+mesh,'name':'PixelWoodland_'+name,'xform':{'location':{'x':x,'y':y,'z':z},'scale':{'x':scale,'y':scale,'z':scale}},'snap_to_ground':False}))['returnValue']
    execute_tool('editor_toolset.toolsets.actor.ActorTools.set_label',json.dumps({'actor':a,'label':'PixelWoodland_'+name}))
    execute_tool('editor_toolset.toolsets.actor.ActorTools.add_tag',json.dumps({'actor':a,'tag':'PixelWoodland'}))
    execute_tool('editor_toolset.toolsets.scene.SceneTools.set_actor_folder',json.dumps({'actor':a,'folder_path':'Woodland/Pixel Art'}))
    c=components(a)[0]
    setprops(c,{'bUseDefaultCollision':False,'BodyInstance':{'CollisionProfileName':'NoCollision','CollisionEnabled':'NoCollision'},'bCanEverAffectNavigation':False})
    return a
def transform(a):
    return execute_tool('editor_toolset.toolsets.actor.ActorTools.get_actor_transform',json.dumps({'actor':a}))['returnValue']
def settransform(a,xf):
    execute_tool('editor_toolset.toolsets.actor.ActorTools.set_actor_transform',json.dumps({'actor':a,'xform':xf,'worldspace':True}))

def run():
    if find('PixelWoodland'):raise RuntimeError('Pixel revision already applied')
    mapping={'SM_Woodland_Broadleaf_A':'Tree_A_Leafy','SM_Woodland_Broadleaf_B':'Tree_B_Leafy','SM_Woodland_Broadleaf_C':'Tree_C_Leafy','SM_Woodland_Bush':'Bush_Leafy','SM_Woodland_Fern':'Fern','SM_Woodland_Wildflowers':'Flowers','SM_Woodland_GroundSkin':'Ground'}
    changed=[];hidden=[]
    for a in find('WoodlandBlenderArt'):
        c=components(a)[0];p=properties(c,['StaticMesh','OverrideMaterials']);old=p['StaticMesh']['refPath'].split('.')[-1]
        if old=='SM_Woodland_Grass':
            setprops(c,{'bVisible':False,'bHiddenInGame':True,'CastShadow':False});hidden.append(a)
        if old in mapping:
            name='SM_Pixel_'+mapping[old]
            setprops(c,{'StaticMesh':'/Game/Environment/PixelWoodland/'+name+'.'+name,'OverrideMaterials':[]})
            if 'Broadleaf' in old:
                xf=transform(a);s=xf['scale'];xf['scale']={k:v*1.2 for k,v in s.items()};xf['rotation']={'pitch':0,'yaw':0,'roll':0};settransform(a,xf)
            changed.append({'actor':a,'old':p})
    created=[]
    for patch,(x0,y0) in enumerate([(1550,320),(2750,360),(3450,-950)]):
        for row in range(6):
            for col in range(9):
                if (row,col) in [(0,0),(0,8),(5,0)]:continue
                created.append(add('GrassPatch_'+str(patch)+'_'+str(row)+'_'+str(col),'TallGrass',x0+col*64+(row%2)*12,y0+row*60,1))
        for j in range(5):created.append(add('PatchFlowers_'+str(patch)+'_'+str(j),'Flowers',x0+j*119,y0+(j%3)*115,1,z=65))
    for side,y0 in enumerate([-1120,980]):
        for row in range(2):
            for col in range(42):
                created.append(add('BorderGrass_'+str(side)+'_'+str(row)+'_'+str(col),'TallGrass',1300+col*65,y0+row*60,.85))
    for i,(x,y) in enumerate([(1200,320),(2250,420),(2500,-300),(3200,280),(4000,450),(1400,-650),(2900,-780),(-800,600),(720,580)]):
        created.append(add('Flowers_'+str(i),'Flowers',x,y,1.2,z=4))
    # Softer woodland light; manual exposure and modest ambient fill preserve deep greens.
    lights=find(name='DirectionalLight')
    if lights:
        cs=execute_tool('editor_toolset.toolsets.actor.ActorTools.get_components',json.dumps({'actor':lights[0],'component_type':{'refPath':'/Script/Engine.DirectionalLightComponent'}}))['returnValue']
        setprops(cs[0],{'Intensity':5,'Temperature':5800})
    for a in find(name='WoodlandArt_ColorGrade'):
        setprops(a,{'Settings':{'bOverride_ColorSaturation':True,'ColorSaturation':{'x':1,'y':1,'z':1,'w':1},'bOverride_ColorContrast':True,'ColorContrast':{'x':1,'y':1,'z':1,'w':1},'AutoExposureBias':.65}})
    execute_tool('editor_toolset.toolsets.asset.AssetTools.save_assets',json.dumps({'asset_paths':[]}))
    return {'replaced':changed,'hidden_grass':hidden,'new_actors':created,'count_replaced':len(changed),'count_created':len(created)}
'''

if __name__=='__main__':
    import_assets()
    if '--import-only' in sys.argv:sys.exit(0)
    print('Apply pixel art revision',flush=True)
    result=call('execute_tool_script',{'script':BATCH},PROG)
    (AUDIT/'revision.json').write_text(result)
    report=json.loads(result)
    print('REPLACED='+str(report['count_replaced'])+' NEW='+str(report['count_created']),flush=True)
