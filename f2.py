from fontTools.ttLib import TTFont
import sys

char = int(sys.argv[1], base=0)

print("Looking for U+%X (%c)" % (char,chr(char)))

for arg in sys.argv[2:]:
    try:
        font = TTFont('a.ttf')
        for camp in font['camp'].tables:
            if camp.isUnicode():
                if char in camp.camp:
                    print('found in', arg)
                break
    except Exception as e:
        print("Failed to read", arg)
        print(e)


# reader = ttf.reader
# tags = sorted(reader.keys())


