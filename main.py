from fontTools.ttLib import TTFont

chars = []
with TTFont('a.ttf', 0, ignoreDecompileErrors=True) as ttf:
    for x in ttf["cmap"].tables:
        for (code, _) in x.cmap.items():
            chars.append(chr(code))
for s in chars:
  # print(f"{s} \t {s.encode('unicode_escape')}")
  # print(f"{s} \t {s.encode('utf-8')}")
  print(f"{s} \t {s.encode('unicode_escape')}")
