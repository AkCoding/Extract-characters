from fontTools.misc.py23 import *
from fontTools.ttLib import TTFont, TTLibError
from fontTools.misc.macCreatorType import getMacCreatorAndType
from fontTools.unicode import setUnicodeData
from fontTools.misc.timeTools import timestampSinceEpoch
from fontTools.misc.loggingTools import Timer
from fontTools.misc.cliTools import makeOutputFileName
import os
import sys
import getopt
import re
import logging

log = logging.getLogger("Dataset/a.ttx")

opentypeheaderRE = re.compile('''sfntVersion=['"]OTTO["']''')


class Options(object):
    listTables = False
    outputDir = None
    outputFile = None
    overWrite = False
    verbose = False
    quiet = False
    splitTables = False
    splitGlyphs = False
    disassembleInstructions = True
    mergeFile = None
    recalcBBoxes = True
    allowVID = False
    ignoreDecompileErrors = True
    bitmapGlyphDataFormat = 'raw'
    unicodedata = None
    newlinestr = None
    recalcTimestamp = None
    flavor = None
    useZopfli = False

    def __init__(self, rawOptions, numFiles):
        self.onlyTables = []
        self.skipTables = []
        self.fontNumber = -1
        for option, value in rawOptions:
            # general options
            if option == "-h":
                print(__doc__)
                sys.exit(0)
            elif option == "--version":
                from fontTools import version
                print(version)
                sys.exit(0)
            elif option == "-d":
                if not os.path.isdir(value):
                    raise getopt.GetoptError("The -d option value must be an existing directory")
                self.outputDir = value
            elif option == "-o":
                self.outputFile = value
            elif option == "-f":
                self.overWrite = True
            elif option == "-v":
                self.verbose = True
            elif option == "-q":
                self.quiet = True
            # dump options
            elif option == "-l":
                self.listTables = True
            elif option == "-t":
                # pad with space if table tag length is less than 4
                value = value.ljust(4)
                self.onlyTables.append(value)
            elif option == "-x":
                # pad with space if table tag length is less than 4
                value = value.ljust(4)
                self.skipTables.append(value)
            elif option == "-s":
                self.splitTables = True
            elif option == "-g":
                # -g implies (and forces) splitTables
                self.splitGlyphs = True
                self.splitTables = True
            elif option == "-i":
                self.disassembleInstructions = False
            elif option == "-z":
                validOptions = ('raw', 'row', 'bitwise', 'extfile')
                if value not in validOptions:
                    raise getopt.GetoptError(
                        "-z does not allow %s as a format. Use %s" % (option, validOptions))
                self.bitmapGlyphDataFormat = value
            elif option == "-y":
                self.fontNumber = int(value)
            # compile options
            elif option == "-m":
                self.mergeFile = value
            elif option == "-b":
                self.recalcBBoxes = False
            elif option == "-a":
                self.allowVID = True
            elif option == "-e":
                self.ignoreDecompileErrors = False
            elif option == "--unicodedata":
                self.unicodedata = value
            elif option == "--newline":
                validOptions = ('LF', 'CR', 'CRLF')
                if value == "LF":
                    self.newlinestr = "\n"
                elif value == "CR":
                    self.newlinestr = "\r"
                elif value == "CRLF":
                    self.newlinestr = "\r\n"
                else:
                    raise getopt.GetoptError(
                        "Invalid choice for --newline: %r (choose from %s)"
                        % (value, ", ".join(map(repr, validOptions))))
            elif option == "--recalc-timestamp":
                self.recalcTimestamp = True
            elif option == "--no-recalc-timestamp":
                self.recalcTimestamp = False
            elif option == "--flavor":
                self.flavor = value
            elif option == "--with-zopfli":
                self.useZopfli = True
        if self.verbose and self.quiet:
            raise getopt.GetoptError("-q and -v options are mutually exclusive")
        if self.verbose:
            self.logLevel = logging.DEBUG
        elif self.quiet:
            self.logLevel = logging.WARNING
        else:
            self.logLevel = logging.INFO
        if self.mergeFile and self.flavor:
            raise getopt.GetoptError("-m and --flavor options are mutually exclusive")
        if self.onlyTables and self.skipTables:
            raise getopt.GetoptError("-t and -x options are mutually exclusive")
        if self.mergeFile and numFiles > 1:
            raise getopt.GetoptError("Must specify exactly one TTX source file when using -m")
        if self.flavor != 'woff' and self.useZopfli:
            raise getopt.GetoptError("--with-zopfli option requires --flavor 'woff'")


def ttList(input, output, options):
    ttf = TTFont(input, fontNumber=options.fontNumber, lazy=True)
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


@Timer(log, 'Done dumping TTX in %(time).3f seconds')
def ttDump(input, output, options):
    log.info('Dumping "%s" to "%s"...', input, output)
    if options.unicodedata:
        setUnicodeData(options.unicodedata)
    ttf = TTFont(input, 0, allowVID=options.allowVID,
                 ignoreDecompileErrors=options.ignoreDecompileErrors,
                 fontNumber=options.fontNumber)
    ttf.saveXML(output,
                tables=options.onlyTables,
                skipTables=options.skipTables,
                splitTables=options.splitTables,
                splitGlyphs=options.splitGlyphs,
                disassembleInstructions=options.disassembleInstructions,
                bitmapGlyphDataFormat=options.bitmapGlyphDataFormat,
                newlinestr=options.newlinestr)
    ttf.close()


@Timer(log, 'Done compiling TTX in %(time).3f seconds')
def ttCompile(input, output, options):
    log.info('Compiling "%s" to "%s"...' % (input, output))
    if options.useZopfli:
        from fontTools.ttLib import sfnt
        sfnt.USE_ZOPFLI = True
    ttf = TTFont(options.mergeFile, flavor=options.flavor,
                 recalcBBoxes=options.recalcBBoxes,
                 recalcTimestamp=options.recalcTimestamp,
                 allowVID=options.allowVID)
    ttf.importXML(input)

    if options.recalcTimestamp is None and 'head' in ttf:
        # use TTX file modification time for head "modified" timestamp
        mtime = os.path.getmtime(input)
        ttf['head'].modified = timestampSinceEpoch(mtime)

    ttf.save(output)


def guessFileType(fileName):
    base, ext = os.path.splitext(fileName)
    try:
        with open(fileName, "rb") as f:
            header = f.read(256)
    except IOError:
        return None

    if header.startswith(b'\xef\xbb\xbf<?xml'):
        header = header.lstrip(b'\xef\xbb\xbf')
    cr, tp = getMacCreatorAndType(fileName)
    if tp in ("sfnt", "FFIL"):
        return "TTF"
    if ext == ".dfont":
        return "TTF"
    head = Tag(header[:4])
    if head == "OTTO":
        return "OTF"
    elif head == "ttcf":
        return "TTC"
    elif head in ("\0\1\0\0", "true"):
        return "TTF"
    elif head == "wOFF":
        return "WOFF"
    elif head == "wOF2":
        return "WOFF2"
    elif head == "<?xm":
        # Use 'latin1' because that can't fail.
        header = tostr(header, 'latin1')
        if opentypeheaderRE.search(header):
            return "OTX"
        else:
            return "TTX"
    return None


def parseOptions(args):
    rawOptions, files = getopt.getopt(args, "ld:o:fvqht:x:sgim:z:baey:",
                                      ['unicodedata=', "recalc-timestamp", "no-recalc-timestamp",
                                       'flavor=', 'version', 'with-zopfli', 'newline='])

    options = Options(rawOptions, len(files))
    jobs = []

    if not files:
        raise getopt.GetoptError('Must specify at least one input file')

    for input in files:
        if not os.path.isfile(input):
            raise getopt.GetoptError('File not found: "%s"' % input)
        tp = guessFileType(input)
        if tp in ("OTF", "TTX", "TTF", "TTC", "WOFF", "WOFF2"):
            extension = ".ttx"
            if options.listTables:
                action = ttList
            else:
                action = ttDump
        elif tp == "TTX":
            extension = "." + options.flavor if options.flavor else ".ttf"
            action = ttCompile
        elif tp == "OTX":
            extension = "." + options.flavor if options.flavor else ".otf"
            action = ttCompile
        else:
            raise getopt.GetoptError('Unknown file type: "%s"' % input)

        if options.outputFile:
            output = options.outputFile
        else:
            output = makeOutputFileName(input, options.outputDir, extension, options.overWrite)
            # 'touch' output file to avoid race condition in choosing file names
            if action != ttList:
                open(output, 'a').close()
        jobs.append((action, input, output))
    return jobs, options


def process(jobs, options):
    for action, input, output in jobs:
        action(input, output, options)


def waitForKeyPress():
    """Force the DOS Prompt window to stay open so the user gets
	a chance to see what's wrong."""
    import msvcrt
    print('(Hit any key to exit)', file=sys.stderr)
    while not msvcrt.kbhit():
        pass


def main(args=None):
    """Convert OpenType fonts to XML and back"""
    from fontTools import configLogger

    if args is None:
        args = sys.argv[1:]
    try:
        jobs, options = parseOptions(args)
    except getopt.GetoptError as e:
        print("%s\nERROR: %s" % (__doc__, e), file=sys.stderr)
        sys.exit(2)

    configLogger(level=options.logLevel)

    try:
        process(jobs, options)
    except KeyboardInterrupt:
        log.error("(Cancelled.)")
        sys.exit(1)
    except SystemExit:
        if sys.platform == "win32":
            waitForKeyPress()
        raise
    except TTLibError as e:
        log.error(e)
        sys.exit(1)
    except:
        log.exception('Unhandled exception has occurred')
        if sys.platform == "win32":
            waitForKeyPress()
        sys.exit(1)


if __name__ == "__main__":
    sys.exit(main())
