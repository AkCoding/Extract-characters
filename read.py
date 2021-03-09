from fontTools.ttLib import TTFont
ttf = TTFont('Dataset/Recursive_VF_1.053.ttf', lazy=True)
reader = ttf.reader
tags = sorted(reader.keys())

print('Listing table info for "%s":' % input)
format = "    %4s  %10s  %8s  %8s"
print(format % ("tag ", "  checksum", "  length", "  offset"))
print(format % ("----", "----------", "--------", "--------"))
for tag in tags:
    entry = reader.tables[tag]
    if ttf.flavor == "woff2":
        # WOFF2 doesn't store table checksums, so they must be calculated
        from fontTools.ttLib.sfnt import calcChecksum

        data = entry.loadData(reader.transformBuffer)
        checkSum = calcChecksum(data)
    else:
        checkSum = int(entry.checkSum)
    if checkSum < 0:
        checkSum = checkSum + 0x100000000
    checksum = "0x%08X" % checkSum
    print(format % (tag, checksum, entry.length, entry.offset))

print()
ttf.close()

