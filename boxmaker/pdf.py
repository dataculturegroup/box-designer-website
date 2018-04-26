# By Kent Quirk, April 2018
# PDF writer; outputs lines and text

# Although SVG is an XML-based language, XML manipulation is annoyingly complicated for what we need
# to do here, so we're just going to treat set things up with a template and embed strings.

# This system exists generate SVG files -- in particular to use with the Glowforge laser cutter. One thing that
# makes using the Glowforge UI work better is for SVGs to use closed paths rather than a semi-random selection of
# lines. Consequently, what this driver does is collect all of the line commands and record them; on the
# save call it concatenates them together into a set of paths.

from reportlab.pdfgen import canvas
import reportlab.lib.colors as colors
from string import Template


class PDFDoc(object):

    def __init__(self, filename):
        self.canvas = canvas.Canvas(filename)

    def setPageSize(self, pageSize):
        self.canvas.setPageSize(pageSize)

    def setAuthor(self, author):
        self.canvas.setAuthor(author)

    def setStrokeColor(self, col):
        self.canvas.setStrokeColor(col)

    def setLineWidth(self, lw):
        self.canvas.setLineWidth(lw)

    def drawString(self, x, y, st):
        self.canvas.drawString(x, y, st)

    def rect(self, x, y, w, h):
        self.canvas.rect(x, y, w, h)

    def drawClosedPath(self, p):
        path = self.canvas.beginPath()
        path.moveTo(p[0][0], p[0][1])
        for pt in p[1:-1]:
            path.lineTo(pt[0], pt[1])
        path.close()
        self.canvas.drawPath(path)

    def drawOpenPath(self, p):
        path = self.canvas.beginPath()
        path.moveTo(p[0][0], p[0][1])
        for pt in p[1:]:
            path.lineTo(pt[0], pt[1])
        self.canvas.drawPath(path)

    def save(self):
        self.canvas.save()
