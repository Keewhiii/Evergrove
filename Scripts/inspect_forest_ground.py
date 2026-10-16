from build_companion_combat import *
M='/Game/Environment/CartoonGround/M_PaintedGrass.M_PaintedGrass'
print(call('get_properties',{'instance':ref(M),'properties':['ShadingModel','BlendMode']},OBJ))
