from validate_cozy_outing import *
APP='EditorToolset.EditorAppToolset'
if '--stop' in sys.argv:
    if call('IsPIERunning',{},APP):call('StopPIE',{},APP)
    marker=q.AUDIT/'cozy_test_actor.json'
    if marker.exists():
        call('remove_from_scene',{'actor':json.loads(marker.read_text())},SCENE)
        marker.unlink()
else:
    if call('IsPIERunning',{},APP):raise RuntimeError('Stop the existing session first')
    if LEVEL not in str(call('get_current_level',{},SCENE)):raise RuntimeError('Open woodland map')
    a=actor(TEST+'_C','Cozy_TemporaryValidation',(0,0,0))
    (q.AUDIT/'cozy_test_actor.json').write_text(json.dumps(a))
    try:call('StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InEditorFloating','warmupSeconds':0}},APP)
    except RuntimeError as e:
        if 'PIE ended before warmup' not in str(e):raise
    print('PIE',call('IsPIERunning',{},APP),flush=True)
