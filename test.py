from fontTools.pens.boundsPen import ControlBoundsPen


# ----
# Info
# ----


# --------
# Outlines
# --------

def extractOpenTypeGlyphs(source, destination):
    # grab the cmap
    cmap = source["cmap"]
    vmtx = source.get("vmtx")
    vorg = source.get("VORG")
    preferred = [
        (3, 10, 12),
        (3, 10, 4),
        (3, 1, 12),
        (3, 1, 4),
        (0, 3, 12),
        (0, 3, 4),
        (3, 0, 12),
        (3, 0, 4),
        (1, 0, 12),
        (1, 0, 4)
    ]
    found = {}
    for table in cmap.tables:
        found[table.platformID, table.platEncID, table.format] = table
        table = None
    for key in preferred:
        if key not in found:
            continue
        table = found[key]
        break
    reversedMapping = {}
    if table is not None:
        for uniValue, glyphName in table.cmap.items():
            reversedMapping[glyphName] = uniValue
    # grab the glyphs
    glyphSet = source.getGlyphSet()
    for glyphName in glyphSet.keys():
        sourceGlyph = glyphSet[glyphName]
        # make the new glyph
        destination.newGlyph(glyphName)
        destinationGlyph = destination[glyphName]
        # outlines
        pen = destinationGlyph.getPen()
        sourceGlyph.draw(pen)
        # width
        destinationGlyph.width = sourceGlyph.width
        # height and vertical origin
        if vmtx is not None and glyphName in vmtx.metrics:
            destinationGlyph.height = vmtx[glyphName][0]
            if vorg is not None:
                if glyphName in vorg.VOriginRecords:
                    destinationGlyph.verticalOrigin = vorg[glyphName]
                else:
                    destinationGlyph.verticalOrigin = vorg.defaultVertOriginY
            else:
                tsb = vmtx[glyphName][1]
                bounds_pen = ControlBoundsPen(glyphSet)
                sourceGlyph.draw(bounds_pen)
                if bounds_pen.bounds is None:
                    continue
                xMin, yMin, xMax, yMax = bounds_pen.bounds
                destinationGlyph.verticalOrigin = tsb + yMax
        # unicode
        destinationGlyph.unicode = reversedMapping.get(glyphName)


def extractFontFromTTX(pathOrFile, destination, doGlyphs=True, doInfo=True, doKerning=True, customFunctions=[]):
    from fontTools.ttLib import TTFont, TTLibError
    source = TTFont()
    source.importXML(pathOrFile)
    if doGlyphs:
        extractOpenTypeGlyphs(source, destination)
    # if doKerning:
    #     kerning, groups = extractOpenTypeKerning(source, destination)
    #     destination.groups.update(groups)
    #     destination.kerning.clear()
    #     destination.kerning.update(kerning)
    for function in customFunctions:
        function(source, destination)
    source.close()


import os

if __name__ == '__main__':
    INPUT_DIR = os.path.join(os.curdir, 'a.ttf')
    OUTPUT_DIR = os.curdir
    extractFontFromTTX(INPUT_DIR, OUTPUT_DIR, doGlyphs=True, doInfo=False, doKerning=False, customFunctions=[])
