"""Editor-only MCP orchestration helpers; never edits Unreal binary assets directly."""
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'Saved'))
import mcp_dialogue_audit as m
m.SESSION = (ROOT / 'Saved/quest_session.txt').read_text()
BANK = '/Game/Game/Quests/Blueprints/BP_QuestBank.BP_QuestBank'
PLAYER = '/Game/Game/Characters/Player/Blueprints/BP_Player.BP_Player'
TABLE = '/Game/Game/Quests/Blueprints/DT_Quests.DT_Quests'
AUDIT = ROOT / 'Saved/QuestBankAudit'
AUDIT.mkdir(exist_ok=True)

def call(name, args, ts='editor_toolset.toolsets.blueprint.BlueprintTools'):
    return m.call(name, args, ts).get('returnValue')

def function(name, inputs, outputs, locals=()):
    graph = call('add_function_graph', {'blueprint': {'refPath': BANK}, 'graph_name': name})
    nodes = call('find_nodes', {'graph': graph, 'title': ''})
    infos = call('get_node_infos', {'nodes': nodes})
    input_names = {p['name'] for n in infos if 'FunctionEntry' in n['node']['refPath'] for p in n['output_pins']}
    output_names = {p['name'] for n in infos if 'FunctionResult' in n['node']['refPath'] for p in n['input_pins']}
    for input_param, fields in [(True, inputs), (False, outputs)]:
        for param, typ, container in fields:
            if param in (input_names if input_param else output_names): continue
            args = {'graph': graph, 'param_name': param, 'input_param': input_param}
            if container: args['container_type'] = container
            if typ.startswith('/'):
                args['object_class'] = {'refPath': typ}
                call('add_object_function_param', args)
            else:
                args['param_type'] = typ
                call('add_function_param', args)
    existing_locals = call('list_variables', {'blueprint': {'refPath': BANK}, 'graph': graph})
    for name, typ, container in locals:
        if name in existing_locals: continue
        args = {'blueprint': {'refPath': BANK}, 'graph': graph, 'name': name, 'type_name': typ}
        if container: args['container_type'] = container
        call('add_variable', args)
    return graph

def write(graph, code):
    (AUDIT / (graph['refPath'].split(':')[-1] + '.dsl')).write_text(code, encoding='utf-8')
    try:
        call('write_graph_dsl', {'graph': graph, 'code': code})
    except RuntimeError as error:
        if '|AddReturnNode... does not exist' not in str(error):
            raise
        # This editor build exposes the return-node action with two leading pipes.
        # Use its discovered action ID and the function's actual output pin names.
        infos = call('get_node_infos', {'nodes': call('find_nodes', {'graph': graph, 'title': ''})})
        result = next((n for n in infos if 'FunctionResult' in n['node']['refPath']), None)
        outputs = [p['name'] for p in result['input_pins'] if p['name'] != 'execute'] if result else []
        tokens = []
        index = 0
        while index < len(code):
            char = code[index]
            if char.isspace():
                index += 1; continue
            if char in '()':
                tokens.append(char); index += 1; continue
            begin = index
            if char == '"':
                index += 1
                while index < len(code):
                    if code[index] == '\\':
                        index += 2; continue
                    if code[index] == '"':
                        index += 1; break
                    index += 1
            else:
                embedded = 0
                while index < len(code) and not code[index].isspace():
                    if code[index] == '(':
                        embedded += 1
                    elif code[index] == ')':
                        if not embedded: break
                        embedded -= 1
                    index += 1
            tokens.append(code[begin:index])
        cursor = 0
        def parse():
            nonlocal cursor
            token = tokens[cursor]; cursor += 1
            if token != '(':
                return token
            values = []
            while tokens[cursor] != ')':
                values.append(parse())
            cursor += 1
            return values
        def emit(value):
            if not isinstance(value, list):
                return value
            if value and value[0] == 'return':
                if len(value) - 1 > len(outputs):
                    raise RuntimeError('Return output signature mismatch: ' + str(outputs))
                value = ['||AddReturnNode...'] + [part for name, expr in zip(outputs, value[1:]) for part in (':' + name, expr)]
            return '(' + ' '.join(emit(part) for part in value) + ')'
        forms = []
        while cursor < len(tokens):
            forms.append(parse())
        call('write_graph_dsl', {'graph': graph, 'code': '\n'.join(emit(form) for form in forms)})
    call('compile_blueprint', {'blueprint': {'refPath': BANK}, 'warnings_as_errors': True})
    print('Compiled:', graph['refPath'].split(':')[-1], flush=True)

if __name__ == '__main__':
    print("Editor audit helper only. Import its functions with an active Unreal MCP session; no gameplay changes are performed by running this file.")
