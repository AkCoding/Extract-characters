import sys
from itertools import chain
from fontTools.ttLib import TTFont
from fontTools.unicode import Unicode

ttf = TTFont('a.ttf')

chars = chain.from_iterable([y + (Unicode[y[0]],) for y in x.cmap.items()] for x in ttf["cmap"].tables)
chars1=(list(chars))
for i in range(len(chars1)):
    print(chars1[i])

ttf.close()