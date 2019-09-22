import HazapModules
pos1=HazapModules.Coordinates()
pos1.lat=31.760254
pos1.lon=131.080396
pos2=HazapModules.Coordinates()
pos2.lat=31.770254
pos2.lon=131.080396
x=HazapModules.Calculatedistance(pos1,pos2)
print(x)
