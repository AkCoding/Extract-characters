
# from fontTools.ttLib import TTFont
# font = TTFont('a.ttf')
# print(font)




import fontforge
F = fontforge.open("a.ttf")
for name in F:
    filename = name + ".png"
    # print name
    F[name].export(filename)


































# from fontTools.ttLib import TTFont
#
# fontpath = 'a.ttf'
# font = TTFont(fontpath)   # specify the path to the font in question
#
#
# def char_in_font(unicode_char, font):
#     for cmap in font['cmap'].tables:
#         if cmap.isUnicode():
#             if ord(unicode_char) in cmap.cmap:
#                 return True
#     return False
# char_in_font()

# from itertools import chain
# import sys
#
# from fontTools.ttLib import TTFont
# from fontTools.unicode import Unicode
#
# ttf = TTFont(fontpath, 0, verbose=0, allowVID=0,
#                 ignoreDecompileErrors=True,
#                 fontNumber=-1)
#
# chars = chain.from_iterable([y + (Unicode[y[0]],) for y in x.cmap.items()] for x in ttf["cmap"].tables)
# print(list(chars))

# Use this for just checking if the font contains the codepoint given as
# second argument:
#char = int(sys.argv[2], 0)
#print(Unicode[char])
#print(char in (x[0] for x in chars))

# ttf.close()



# from fontTools.ttLib import TTFont
# import sys
#
# char = int(fontpath, base=0)
#
# print("Looking for U+%X (%c)" % (char, chr(char)))
#
# for arg in sys.argv[2:]:
#     try:
#         font = TTFont(arg)
#
#         for cmap in font['cmap'].tables:
#             if cmap.isUnicode():
#                 if char in cmap.cmap:
#                     print("Found in", arg)
#                     break
#     except Exception as e:
#         print("Failed to read", arg)
#         print(e)
#
#
#














# from fontTools.ttLib import TTFont
# from fontTools.unicode import Unicode
# from ttfquery import ttfgroups
# from fontTools.ttLib.tables import _c_m_a_p
# from itertools import chain
#
# ttfgroups.buildTable()
# ttf = TTFont(sys.argv[1], 0, verbose=0, allowVID=0,
#              ignoreDecompileErrors=True,
#              fontNumber=-1)
#
# chars = chain.from_iterable([y + (Unicode[y[0]],) for y in x.cmap.items()] for x in ttf["cmap"].tables)
# print(list(chars))
# `