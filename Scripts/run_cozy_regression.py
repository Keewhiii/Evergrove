"""Run existing woodland/party/trail suites separately; never save test actors."""
from build_woodland_blockout import *
import time,re
APP='EditorToolset.EditorAppToolset'
results={}
for suite,path in [('WOODLAND','/Game/Tests/World/BP_WoodlandValidation.BP_WoodlandValidation'),('PARTY','/Game/Tests/Combat/BP_PartyCombatValidation.BP_PartyCombatValidation'),('TRAIL_AI','/Game/Tests/World/BP_TrailAIValidation.BP_TrailAIValidation')]:
    offset=(ROOT/'Saved/Logs/AdventureRPG.log').stat().st_size
    a=actor(path+'_C','Cozy_TemporaryRegression',(0,0,0))
    try:
        options={'bSimulate':False,'playMode':'PlayMode_InEditorFloating','warmupSeconds':0}
        # Party tests assume a combat-capable location, outside the safe guild.
        if suite=='PARTY':options['startTransform']={'location':{'x':2300,'y':0,'z':110},'rotation':{'pitch':0,'yaw':180,'roll':0},'scale':{'x':1,'y':1,'z':1}}
        try:call('StartPIE',{'options':options},APP)
        except RuntimeError as e:
            if 'PIE ended before warmup' not in str(e):raise
        time.sleep(14)
        with (ROOT/'Saved/Logs/AdventureRPG.log').open('rb') as f:f.seek(offset);log=f.read().decode('utf-8',errors='replace')
        finals=re.findall(suite+r'_FINAL_FAILURES=(\d+)',log)
        results[suite]={'passes':len(re.findall(suite+r'_PASS ',log)),'failures':int(finals[-1]) if finals else 'missing final'}
        print(suite,results[suite],flush=True)
    finally:
        if call('IsPIERunning',{},APP):call('StopPIE',{},APP)
        call('remove_from_scene',{'actor':a},SCENE)
(q.AUDIT/'CozyRegressionResults.json').write_text(json.dumps(results,indent=2))
if any(v['failures']!=0 for v in results.values()):raise RuntimeError(results)
