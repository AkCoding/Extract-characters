from fontTools.ttLib import TTFont


def emoji(file):
    chars = []
    with TTFont(file, 0, ignoreDecompileErrors=True) as ttf:
        for x in ttf["cmap"].tables:
            [chars.append(chr(code)) for (code, _) in x.cmap.items() if chr(code) not in chars]
    # return chars


    print(chars)
    print(f"length is {len(chars)}")
file = "Dataset/Recursive_VF_1.053.ttf"
emoji(file)
# for s in chars:
  # print(f"{s} \t {s.encode('unicode_escape')}")
  # print(f"{s} \t {s.encode('utf-8')}")
  # print(f"{s} \t {s.encode('unicode_escape')}")
