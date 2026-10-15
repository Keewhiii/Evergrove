"""Install the native Blender interior, collision, receptionist and linked automatic doors."""
from build_companion_combat import call,ref,ROOT,ASSET,OBJ,SCENE
from woodland_fx_graph import Graph,props,MAT
import json
F='/Game/Environment/GuildInterior';SOURCE=ROOT/'ContentSource/GuildInterior';OUT=ROOT/'Saved/GuildInteriorAudit';OUT.mkdir(exist_ok=True)
SM='editor_toolset.toolsets.static_mesh.StaticMeshTools';ACT='editor_toolset.toolsets.actor.ActorTools';PROG='editor_toolset.toolsets.programmatic.ProgrammaticToolset'
TEX='editor_toolset.toolsets.texture.TextureTools'
for name in ['Oak','Plaster']:
 t='T_Interior_'+name
 if not call('exists',{'path':F+'/'+t},ASSET):call('import_file',{'folder_path':F,'asset_name':t,'source_file':str(SOURCE/(t+'.png'))},TEX)
 props(ref(F+'/'+t+'.'+t),{'Filter':'TF_Nearest','LODGroup':'TEXTUREGROUP_Pixels2D','NeverStream':True})
def lin(c):
 c/=255;return c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4
for name,rgb in json.loads((SOURCE/'palette.json').read_text()).items():
 mn='M_Interior_'+name;m=ref(F+'/'+mn+'.'+mn)
 if not call('exists',{'path':F+'/'+mn},ASSET):call('create_material',{'folder_path':F,'asset_name':mn},MAT)
 for e in call('get_expressions',{'material_or_function':m},MAT):call('delete_expression',{'material_or_function':m,'expression':e},MAT)
 g=Graph(m);color=g.vec('Color',[lin(c) for c in rgb])
 if name in ['FloorA','FloorB','FloorC','Trim','Cream']:
  texname='Plaster' if name=='Cream' else 'Oak';sample=g.n('TextureSample',Texture=F+'/T_Interior_'+texname+'.T_Interior_'+texname);mix=g.n('LinearInterpolate',ConstAlpha=.6 if name=='Cream' else (.20 if name=='Trim' else .35));g.wire(color,mix,'A');g.wire(sample,mix,'B','RGB');color=mix
 g.output(color,'MP_BaseColor');g.output(g.n('Constant',R=.95),'MP_Roughness');g.output(g.n('Constant',R=0),'MP_Specular')
 # A modest painted fill keeps furniture readable under the open cutaway gallery.
 g.output(g.mul(color,2 if name in ['Glass','LampGlass'] else .25),'MP_EmissiveColor');props(m,{'TwoSided':True,'ShadingModel':'MSM_DefaultLit'});call('recompile',{'material_or_function':m},MAT)
 print('INTERIOR_MATERIAL',name,flush=True)
for item in json.loads((SOURCE/'manifest.json').read_text()):
 name=item['name'];m=ref(F+'/'+name+'.'+name)
 if not call('exists',{'path':F+'/'+name},ASSET):call('import_file',{'folder_path':F,'asset_name':name,'source_file':item['file'],'import_materials':False,'import_textures':False,'combine_meshes':True},SM)
 call('remove_collisions',{'mesh':m},SM)
 for slot in call('get_material_slots',{'mesh':m},SM):
  folder='/Game/Environment/GuildHall' if slot.startswith('M_Guild_') else F
  call('set_material',{'mesh':m,'slot_name':slot,'material':ref(folder+'/'+slot+'.'+slot)},SM)
 print('INTERIOR_MESH',name,call('get_triangle_count',{'mesh':m,'lod_index':0},SM),flush=True)
def place(name,asset,pos,scale=(1,1,1),yaw=0):
 existing=call('find_actors',{'name':name,'tag':'','collision_channels':[]},SCENE)
 if existing:return existing[0]
 a=call('add_to_scene_from_asset',{'asset_path':asset,'name':name,'xform':{'location':dict(zip('xyz',pos)),'rotation':{'pitch':0,'yaw':yaw,'roll':0},'scale':dict(zip('xyz',scale))},'snap_to_ground':False},SCENE);call('set_label',{'actor':a,'label':name},ACT);call('set_actor_folder',{'actor':a,'folder_path':'Woodland/Guild Interior'},SCENE);return a
def tag(a,name):
 if a not in call('find_actors',{'name':'','tag':name,'collision_channels':[]},SCENE):call('add_tag',{'actor':a,'tag':name},ACT)
for group in ['Architecture','Furniture','Details']:
 meshname='SM_Guild_'+group+'_Roomy'
 a=place('GuildInterior_'+group,F+'/'+meshname,(0,-6000,0));tag(a,'GuildInterior')
 for c in call('get_components',{'actor':a,'component_type':ref('/Script/Engine.StaticMeshComponent')},ACT):props(c,{'StaticMesh':F+'/'+meshname+'.'+meshname,'OverrideMaterials':[],'bUseDefaultCollision':False,'BodyInstance':{'CollisionProfileName':'NoCollision','CollisionEnabled':'NoCollision'},'bCanEverAffectNavigation':False})
# Swap only the ornament mesh: the shell/roof/porch remain the authored exterior.
for a in call('find_actors',{'name':'SM_GuildHall_Ornaments','tag':'GuildHallExterior','collision_channels':[]},SCENE):
 c=call('get_components',{'actor':a,'component_type':ref('/Script/Engine.StaticMeshComponent')},ACT)[0];props(c,{'StaticMesh':F+'/SM_Guild_FacadeOpen_Detailed.SM_Guild_FacadeOpen_Detailed','OverrideMaterials':[]})
# Keep a solid facade as a safety boundary, and open/teleport before the capsule touches it.
for old in call('find_actors',{'name':'GuildDoor_','tag':'','collision_channels':[]},SCENE):
 if 'BP_AutoDoor' in str(call('get_class',{'instance':old},OBJ)):call('remove_from_scene',{'actor':old},SCENE)
leaves={}
for side,x in [('Left',-150),('Right',150)]:
 a=place('GuildExterior_Door'+side,F+'/SM_Guild_Door'+side+'_Detailed',(x,-510,0));props(a,{'bIsSpatiallyLoaded':False});leaves[side]=a
 c=call('get_components',{'actor':a,'component_type':ref('/Script/Engine.StaticMeshComponent')},ACT)[0];props(c,{'Mobility':'Movable','bUseDefaultCollision':False,'BodyInstance':{'CollisionProfileName':'NoCollision','CollisionEnabled':'NoCollision'},'bCanEverAffectNavigation':False})
for name,y,yaw,dest,dyaw in [('GuildDoor_Entrance',-510,0,(0,-6250,100),180),('GuildDoor_Exit',-6000,180,(0,-260,100),0)]:
 a=place(name,'/Game/Game/World/BP_WalkThroughDoor',(0,y,0),yaw=yaw);xf=call('get_actor_transform',{'actor':a},ACT);xf['location']={'x':0,'y':y,'z':0};call('set_actor_transform',{'actor':a,'xform':xf,'worldspace':True},ACT);props(a,{'Destination':dict(zip('xyz',dest)),'DestinationYaw':dyaw,'TriggerWidth':105,'TriggerDepth':110,'bIsSpatiallyLoaded':False,'LeftLeaf':leaves['Left']['refPath'] if name=='GuildDoor_Entrance' else None,'RightLeaf':leaves['Right']['refPath'] if name=='GuildDoor_Entrance' else None});tag(a,'GuildPortal')
# Collision cubes are deliberately simple, independent of decorative pixel geometry.
colliders=json.loads((SOURCE/'collision.json').read_text())
script='''import json
def tool(n,a):return execute_tool(n,json.dumps(a))['returnValue']
def run():
 count=0
 for i,item in enumerate(COLLIDERS):
  name='GuildInterior_Collision_'+str(i)+'_'+item['name']
  old=tool('editor_toolset.toolsets.scene.SceneTools.find_actors',{'name':name,'tag':'','collision_channels':[]})
  x,y,z=item['center'];sx,sy,sz=item['size']
  if old:a=old[0]
  else:
   a=tool('editor_toolset.toolsets.scene.SceneTools.add_to_scene_from_asset',{'asset_path':'/Engine/BasicShapes/Cube','name':name,'xform':{'location':{'x':x*100,'y':-6000-y*100,'z':z*100},'scale':{'x':sx,'y':sy,'z':sz}},'snap_to_ground':False})
   tool('editor_toolset.toolsets.actor.ActorTools.set_label',{'actor':a,'label':name})
   tool('editor_toolset.toolsets.scene.SceneTools.set_actor_folder',{'actor':a,'folder_path':'Woodland/Guild Interior/Collision'})
  tool('editor_toolset.toolsets.actor.ActorTools.set_actor_transform',{'actor':a,'xform':{'location':{'x':x*100,'y':-6000-y*100,'z':z*100},'rotation':{'pitch':0,'yaw':0,'roll':0},'scale':{'x':sx,'y':sy,'z':sz}},'worldspace':True})
  c=tool('editor_toolset.toolsets.actor.ActorTools.get_components',{'actor':a,'component_type':{'refPath':'/Script/Engine.StaticMeshComponent'}})[0]
  tool('editor_toolset.toolsets.object.ObjectTools.set_properties',{'instance':c,'values':json.dumps({'bVisible':False,'bHiddenInGame':True,'bUseDefaultCollision':False,'BodyInstance':{'CollisionProfileName':'BlockAll','CollisionEnabled':'QueryAndPhysics'},'bCanEverAffectNavigation':True})});count+=1
 return {'colliders':count}
'''.replace('COLLIDERS',repr(colliders))
report=json.loads(call('execute_tool_script',{'script':script},PROG))
report['npcs']=[]
for label,pos in [('Woodland_Luna',(0,-7603.333333,100)),('Woodland_Rein',(-650,-7530,100))]:
 a=call('find_actors',{'name':label,'tag':'','collision_channels':[]},SCENE)[0];xf=call('get_actor_transform',{'actor':a},ACT)
 report['npcs'].append({'actor':a,'before_transform':xf,'before_properties':json.loads(call('get_properties',{'instance':a,'properties':['NPCName','NPCDialogueText','HasChoices','CompletesQuestOnInteract','QuestToComplete','QuestNPCID']},OBJ))});xf=json.loads(json.dumps(xf));xf['location']=dict(zip('xyz',pos));call('set_actor_transform',{'actor':a,'xform':xf,'worldspace':True},ACT)
 # World partition must keep the receptionist available when the room is entered.
 props(a,{'bIsSpatiallyLoaded':False})
if not (OUT/'installation_before.json').exists():(OUT/'installation_before.json').write_text(json.dumps(report,indent=2))
for a in call('find_actors',{'name':'GuildInterior_','tag':'','collision_channels':[]},SCENE):props(a,{'bIsSpatiallyLoaded':False})
call('save_assets',{'asset_paths':[]},ASSET);(OUT/'installation.json').write_text(json.dumps(report,indent=2));print('GUILD_INTERIOR_INSTALLED',report['colliders'],flush=True)
