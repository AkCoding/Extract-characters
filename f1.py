import gftools.fonts_public_pb2 as fonts_pb2
from fontTools.ttLib import TTFont

ttf = TTFont('a.ttf', lazy=True)
ttf.saveXML("a.xml")