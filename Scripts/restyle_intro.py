"""Update typography and text-only layouts while preserving menu input bindings."""
from pathlib import Path
source=Path(__file__).with_name('author_intro_art.py').read_text()
source=source[:source.index('events=f')]+"\ncall('compile_blueprint',{'blueprint':ref(M),'warnings_as_errors':True})\ncall('save_assets',{'asset_paths':[M]},ASSET)\n"
source=source.replace('from build_companion_combat import *','''from build_companion_combat import *
original_graph=graph
def graph(path,name,*args,**kwargs):
 if name!='DrawBackdrop':return original_graph(path,name,*args,**kwargs)
''',1)
exec(source)
