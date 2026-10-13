"""Fit the training beasts/treats inside the existing prototype room."""
from build_companion_combat import *
if __name__=='__main__':
    code=(q.AUDIT/'Setup.dsl').read_text()
    for i,x in enumerate([-400,-150,150,400]):
        code=code.replace(f'MakeVector {300+i*180}.0 -450.0 0.0',f'MakeVector {x}.0 -250.0 0.0')
    for i in range(8):
        code=code.replace(f'MakeVector {250+(i%4)*140}.0 {300+(i//4)*160}.0 -35.0',f'MakeVector {[-350,-150,150,350][i%4]}.0 {100+(i//4)*130}.0 -35.0')
    q.BANK=DIRECTOR;q.write(ref(DIRECTOR+':Setup'),code)
    call('save_assets',{'asset_paths':[DIRECTOR]},ASSET)
