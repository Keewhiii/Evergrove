"""Remove duplicate live execution links left by DSL input-event migrations."""
from build_companion_combat import *

def deduplicate():
    g=ref(DIRECTOR+':EventGraph')
    ns=call('get_node_infos',{'nodes':call('find_nodes',{'graph':g,'title':''})})
    groups={}
    for n in ns:
        if n['type_id'].startswith(('Input|KeyboardEvents|','Input|MouseEvents|')):
            if any(p['connected_pins'] for p in n['output_pins'] if p['type_id']=='Exec'):
                groups.setdefault(n['type_id'],[]).append(n)
    for key,nodes in groups.items():
        for n in nodes[:-1]:
            for p in n['output_pins']:
                if p['type_id']=='Exec':
                    for dest in p['connected_pins']:
                        call('break_pins',{'output_pin':p['pin_id'],'input_pin':dest})
        if len(nodes)>1:print('Deduplicated',key,flush=True)
    call('compile_blueprint',{'blueprint':ref(DIRECTOR),'warnings_as_errors':True})
    call('save_assets',{'asset_paths':[DIRECTOR]},ASSET)

if __name__=='__main__':deduplicate()
