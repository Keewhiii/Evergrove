"""Replace the NPC shelter with the Blender hall, preserving NPC quest properties."""
from build_companion_combat import call,ref,ROOT,ASSET,OBJ,SCENE,graph,var
from woodland_fx_graph import Graph,props,MAT
import json
F='/Game/Environment/GuildHall';SOURCE=ROOT/'ContentSource/GuildHall';OUT=ROOT/'Saved/GuildHallAudit';OUT.mkdir(exist_ok=True);SM='editor_toolset.toolsets.static_mesh.StaticMeshTools';TEX='editor_toolset.toolsets.texture.TextureTools';ACT='editor_toolset.toolsets.actor.ActorTools';PROG='editor_toolset.toolsets.programmatic.ProgrammaticToolset';WORLD='/Game/Game/World/BP_WoodlandWorld.BP_WoodlandWorld'
props(ref('/Script/UnrealEd.Default__EditorPerformanceSettings'),{'bThrottleCPUWhenNotForeground':False})
def linear(c):
 c=c/255;return c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4
for name in ['Roof','Timber','Plaster','Stone']:
 t='T_Guild_'+name
 if not call('exists',{'path':F+'/'+t},ASSET):call('import_file',{'folder_path':F,'asset_name':t,'source_file':str(SOURCE/(t+'.png'))},TEX)
 props(ref(F+'/'+t+'.'+t),{'Filter':'TF_Nearest','LODGroup':'TEXTUREGROUP_Pixels2D','NeverStream':True,'MipGenSettings':'TMGS_NoMipmaps'})
colors=json.loads((SOURCE/'palette.json').read_text());materials={}
for name in ['Roof','Timber','Plaster','Stone']+list(colors):
 mn='M_Guild_'+name;mat=ref(F+'/'+mn+'.'+mn)
 if not call('exists',{'path':F+'/'+mn},ASSET):call('create_material',{'folder_path':F,'asset_name':mn},MAT)
 for e in call('get_expressions',{'material_or_function':mat},MAT):call('delete_expression',{'material_or_function':mat,'expression':e},MAT)
 g=Graph(mat)
 if name in ['Roof','Timber','Plaster','Stone']:
  sample=g.n('TextureSample',Texture=F+'/T_Guild_'+name+'.T_Guild_'+name);g.output(sample,'MP_BaseColor','RGB')
 else:
  sample=g.vec('Color',[linear(c) for c in colors[name]]);g.output(sample,'MP_BaseColor')
 if name=='Glass':g.output(g.mul(sample,3),'MP_EmissiveColor')
 g.output(g.n('Constant',R=.9 if name!='Gold' else .55),'MP_Roughness')
 if name=='Gold':g.output(g.n('Constant',R=.25),'MP_Metallic')
 if name=='Banner':
  t=g.n('Time');uv=g.n('TextureCoordinate');v=g.mask(uv,'G');wave=g.sine(g.pair('Add',g.mul(t,.7),g.mul(v,1.2)));amplitude=g.pair('Multiply',g.pair('Multiply',wave,v),g.add(g.gust(t),.12));g.output(g.pair('Multiply',amplitude,g.vec('ClothWind',(5,2,0))),'MP_WorldPositionOffset')
 props(mat,{'TwoSided':True,'ShadingModel':'MSM_DefaultLit'});call('recompile',{'material_or_function':mat},MAT);materials[mn]=mat;print('GUILD_MATERIAL',name,flush=True)
for item in json.loads((SOURCE/'manifest.json').read_text()):
 name=item['name'];mesh=ref(F+'/'+name+'.'+name)
 if not call('exists',{'path':F+'/'+name},ASSET):call('import_file',{'folder_path':F,'asset_name':name,'source_file':item['file'],'import_materials':False,'import_textures':False,'combine_meshes':True},SM)
 call('remove_collisions',{'mesh':mesh},SM)
 for slot in call('get_material_slots',{'mesh':mesh},SM):call('set_material',{'mesh':mesh,'slot_name':slot,'material':materials[slot]},SM)
 existing=call('find_actors',{'name':name,'tag':'GuildHallExterior','collision_channels':[]},SCENE)
 if existing:a=existing[0]
 else:
  a=call('add_to_scene_from_asset',{'asset_path':F+'/'+name,'name':name,'xform':{'location':{'x':0,'y':-550,'z':0},'rotation':{'pitch':0,'yaw':0,'roll':0},'scale':{'x':1,'y':1,'z':1}},'snap_to_ground':False},SCENE);call('set_label',{'actor':a,'label':name},ACT);call('add_tag',{'actor':a,'tag':'GuildHallExterior'},ACT)
 c=call('get_components',{'actor':a,'component_type':ref('/Script/Engine.StaticMeshComponent')},ACT)[0];props(c,{'bUseDefaultCollision':False,'BodyInstance':{'CollisionProfileName':'NoCollision','CollisionEnabled':'NoCollision'},'bCanEverAffectNavigation':False});call('set_actor_folder',{'actor':a,'folder_path':'Woodland/Guild Hall'},SCENE)
 print('GUILD_MESH',name,call('get_triangle_count',{'mesh':mesh,'lod_index':0},SM),flush=True)

script='''import json
def tool(n,a):return execute_tool(n,json.dumps(a))['returnValue']
def run():
 old=[];moved=[];npcs=[]
 for a in tool('editor_toolset.toolsets.scene.SceneTools.find_actors',{'name':'Woodland_Guild','tag':'','collision_channels':[]}):
  for c in tool('editor_toolset.toolsets.actor.ActorTools.get_components',{'actor':a,'component_type':{'refPath':'/Script/Engine.StaticMeshComponent'}}):
   before=json.loads(tool('editor_toolset.toolsets.object.ObjectTools.get_properties',{'instance':c,'properties':['bVisible','bHiddenInGame']}));old.append({'actor':a,'component':c,'properties':before})
   tool('editor_toolset.toolsets.object.ObjectTools.set_properties',{'instance':c,'values':json.dumps({'bVisible':False,'bHiddenInGame':True})})
 for tag in ['WoodlandBlenderArt','PixelWoodland']:
  for a in tool('editor_toolset.toolsets.scene.SceneTools.find_actors',{'name':'','tag':tag,'collision_channels':[]}):
   cs=tool('editor_toolset.toolsets.actor.ActorTools.get_components',{'actor':a,'component_type':{'refPath':'/Script/Engine.StaticMeshComponent'}})
   if not cs:continue
   p=json.loads(tool('editor_toolset.toolsets.object.ObjectTools.get_properties',{'instance':cs[0],'properties':['StaticMesh']}));xf=tool('editor_toolset.toolsets.actor.ActorTools.get_actor_transform',{'actor':a});loc=xf['location']
   if 'Tree' in p['StaticMesh']['refPath'] and abs(loc['x'])<1100 and loc['y']<-500:
    moved.append({'actor':a,'transform':json.loads(json.dumps(xf))});xf['location']={'x':-1240 if loc['x']<0 else 1240,'y':loc['y'],'z':loc['z']};tool('editor_toolset.toolsets.actor.ActorTools.set_actor_transform',{'actor':a,'xform':xf,'worldspace':True})
 for label,x in [('Woodland_Luna',-250),('Woodland_Rein',250)]:
  a=tool('editor_toolset.toolsets.scene.SceneTools.find_actors',{'name':label,'tag':'','collision_channels':[]})[0]
  xf=tool('editor_toolset.toolsets.actor.ActorTools.get_actor_transform',{'actor':a});npcs.append({'actor':a,'label':label,'transform':json.loads(json.dumps(xf)),'properties':json.loads(tool('editor_toolset.toolsets.object.ObjectTools.get_properties',{'instance':a,'properties':['NPCName','NPCDialogueText','HasChoices','CompletesQuestOnInteract','QuestToComplete','QuestNPCID']}))})
  xf['location']={'x':x,'y':-300,'z':100};tool('editor_toolset.toolsets.actor.ActorTools.set_actor_transform',{'actor':a,'xform':xf,'worldspace':True})
 return {'hidden_shelter':old,'moved_tree_edges':moved,'npcs':npcs}
'''
report=json.loads(call('execute_tool_script',{'script':script},PROG))
if not (OUT/'before_replacement.json').exists():(OUT/'before_replacement.json').write_text(json.dumps(report,indent=2))
def support(name,pos,size,material,visible):
 actors=call('find_actors',{'name':name,'tag':'','collision_channels':[]},SCENE)
 if actors:a=actors[0]
 else:
  a=call('add_to_scene_from_asset',{'asset_path':'/Engine/BasicShapes/Cube','name':name,'xform':{'location':dict(zip(['x','y','z'],pos)),'scale':dict(zip(['x','y','z'],size))},'snap_to_ground':False},SCENE);call('set_label',{'actor':a,'label':name},ACT)
 c=call('get_components',{'actor':a,'component_type':ref('/Script/Engine.StaticMeshComponent')},ACT)[0];props(c,{'bVisible':visible,'bHiddenInGame':not visible,'OverrideMaterials':[material],'bUseDefaultCollision':False,'BodyInstance':{'CollisionProfileName':'BlockAll','CollisionEnabled':'QueryAndPhysics'},'bCanEverAffectNavigation':True});return a
support('GuildHall_FoundationGround',(0,-1290,-30),(25,20,.50),'/Game/Game/Combat/M_Woodland_Meadow.M_Woodland_Meadow',True)
support('GuildHall_ClosedFrontCollision',(0,-550,400),(19.1,.30,8),F+'/M_Guild_Dark.M_Guild_Dark',False)

# Stale saves from inside the previous open shelter arrive safely in front of the new exterior.
var(WORLD,'GuildArrivalChecked','bool')
graph(WORLD,'EnsureGuildArrival','''(fn EnsureGuildArrival ()
 (if (Variables|Default|GetGuildArrivalChecked) (return))
 (bind player (Game|GetPlayerCharacter 0))
 (if (not (CallFunction|Valid :Object player)) (return))
 (Variables|Default|SetGuildArrivalChecked true)
 (bind (x y z) (Math|Vector|BreakVector (Transformation|GetActorLocation :self player)))
 (if (and (and (> x -950.0) (< x 950.0)) (and (< y -500.0) (> y -2100.0)))
  (Transformation|SetActorLocation :self player :NewLocation (Math|Vector|MakeVector 0.0 -80.0 120.0) :bTeleport true)))''')
source=(ROOT/'Saved/CombatAudit/UpdateCamera.dsl').read_text(encoding='utf-8')
if '(CallFunction|EnsureGuildArrival)' not in source:source=source.replace('(fn UpdateCamera (Delta)','(fn UpdateCamera (Delta)\n (CallFunction|EnsureGuildArrival)',1)
graph(WORLD,'UpdateCamera',source,[('Delta','float',None)])
call('save_assets',{'asset_paths':[]},ASSET);report['building_origin']={'x':0,'y':-550,'z':0};report['width_m']=19.7;report['height_m']=18
(OUT/'replacement.json').write_text(json.dumps(report,indent=2));print('GUILD_EXTERIOR_INSTALLED',len(report['hidden_shelter']),len(report['moved_tree_edges']),flush=True)
