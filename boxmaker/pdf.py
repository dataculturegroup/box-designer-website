# By Kent Quirk, April 2018
# PDF writer

# The dxf object was originally designed to emulate canvas.Canvas -- but that has proved a little too limiting.
# So instead of pdfs rendering directly to canvas.Canvas, we have specific drivers for different file types.
# This file implements the pdf-specific rendering.

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
