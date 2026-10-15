"""Idempotent editor setup. Finish with Unreal Save All before reloading/cooking."""
from build_woodland_blockout import *

def configure():
    if call('IsPIERunning',{},'EditorToolset.EditorAppToolset'):raise RuntimeError('Stop Play first.')
    if call('get_current_level',{},SCENE)!=LEVEL:raise RuntimeError('Load '+LEVEL)
    found=call('find_actors',{'name':'Woodland_NavigationBounds','tag':'','collision_channels':[]},SCENE)
    bounds=found[0] if found else actor('/Script/NavigationSystem.NavMeshBoundsVolume','Woodland_NavigationBounds',(1600,0,300),(28,13,5))
    properties(bounds,{'bIsSpatiallyLoaded':False})
    for a in call('find_actors',{'name':'RecastNavMesh','tag':'','collision_channels':[]},SCENE):
        properties(a,{'RuntimeGeneration':'Dynamic','bForceRebuildOnLoad':True})
    count=0
    for prefix in ['Woodland_Crown','Woodland_HubWalk','Woodland_Trail','Woodland_Clearing']:
        for a in call('find_actors',{'name':prefix,'tag':'WoodlandBlockout','collision_channels':[]},SCENE):
            c=call('get_components',{'actor':a,'component_type':ref('/Script/Engine.StaticMeshComponent')},ACTOR)[0]
            properties(c,{'bUseDefaultCollision':False,'BodyInstance':{'CollisionProfileName':'NoCollision','CollisionEnabled':'NoCollision'},'bCanEverAffectNavigation':False})
            count+=1
    print('Configured navigation bounds and',count,'decorative components. Use Unreal Save All (Ctrl+Shift+S) to persist external actor packages.')

if __name__=='__main__':configure()
