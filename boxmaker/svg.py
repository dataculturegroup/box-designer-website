# By Kent Quirk, April 2018
# SVG writer; outputs lines and text

# Although SVG is an XML-based language, XML manipulation is annoyingly complicated for what we need
# to do here, so we're just going to treat set things up with a template and embed strings.

# This system exists generate SVG files -- in particular to use with the Glowforge laser cutter. One thing that
# makes using the Glowforge UI work better is for SVGs to use closed paths rather than a semi-random selection of
# lines. Consequently, what this driver does is collect all of the line commands and record them; on the
# save call it concatenates them together into a set of paths.

import reportlab.lib.colors as colors
from string import Template

tmpl_svg = Template("""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg width="${pixel_width}px" height="${pixel_height}px" version="1.1"
    xmlns="http://www.w3.org/2000/svg"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xml:space="preserve"
    xmlns:serif="http://www.serif.com/"
    style="fill-rule:evenodd;clip-rule:evenodd;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:1.5;">
${contents}
</svg>
""")

tmpl_path = Template("""        <path d="${path}" style="fill:none;stroke:${stroke_color};stroke-width:${stroke_pixels}px;"/>
""")

tmpl_rect = Template("""        <rect x="${x}" y="${y}" width="${w}" height="${h}"/>
""")


class SVGDoc(object):

    def __init__(self, filename):
        self.comments = []
        self.elements = []
        self.paths = []
        self.firsts = set()
        self.filename = filename
        self.strokeColor = "black"
        self.lineWidth = 0.5  # default is mm so we need to convert
        self.pageSize = [0, 0]
        self.author = ''

    def setPageSize(self, pageSize):
        self.pageSize = pageSize

    def setAuthor(self, author):
        self.author = author

    def setStrokeColor(self, col):
        self.strokeColor = col

    def setLineWidth(self, lw):
        self.lineWidth = lw

    def drawString(self, x, y, st):
        # String must be free of metacharacters
        self.comments.append((x, y, st))

    def rect(self, x, y, w, h):
        self.elements.append(tmpl_rect.substitute(dict(x=self._sc(x), y=self._sc(y), w=self._sc(w), h=self._sc(h))))

    def line(self, x0, y0, x1, y1):
        self._line(x0, y0, x1, y1)

    def beginPath(self):
        pass

    def moveTo(self, x, y):
        pass

    def lineTo(self, x, y):
        pass

    def drawPath(self):
        pass

    def save(self):
        self._join_paths()
        self._generateElements()
        s = ''.join([e for e in self.elements])
        pgw, pgh = self._sc(self.pageSize[0]), self._sc(self.pageSize[1])
        svg = tmpl_svg.substitute(dict(
            pixel_width=pgw,
            pixel_height=pgh,
            contents=s))
        ofh = open(self.filename, 'w')
        ofh.write(svg)
        ofh.close()


    # end public API

    def _sc(self, v):
        "converts from mm to pixels as a numeric string"
        return "{:.1f}".format(v)# * 96 / 25.4)

    def _col(self, color):
        "generates a CSS color from a reportlab color"
        return '#'+color.hexval()[2:]

    def _generateElements(self):
        for p in self.paths:
            s = ''
            if p[0] == p[-1]:
                # generate closed path
                s = "M{},{}".format(p[0][0], p[0][1])
                s += ''.join(["L{},{}".format(pt[0], pt[1]) for pt in p[1:-1]])
                s += 'Z'
            else:
                # generate open path
                s = "M{},{}".format(p[0][0], p[0][1])
                s += ''.join(["L{},{}".format(pt[0], pt[1]) for pt in p[1:]])
            self.elements.append(tmpl_path.substitute(dict(
                path=s,
                stroke_color=self._col(self.strokeColor),
                stroke_pixels=self._sc(self.lineWidth)
                )))

    def _join_paths_1(self):
        oldpaths = self.paths[:]
        newpaths = []
        while len(oldpaths):
            start = -1
            it = oldpaths.pop()
            for pi in range(len(oldpaths)):
                if oldpaths[pi][-1] == it[0]:
                    start = pi
                    break
                if oldpaths[pi][-1] == it[-1]:
                    start = pi
                    it.reverse()
                    break
            if start == -1:
                newpaths.append(it)
            else:
                newpaths.append(oldpaths[start] + it[1:])
                del oldpaths[start]
        return newpaths

    def _join_paths(self):
        while True:
            count = len(self.paths)
            paths = self._join_paths_1()
            self.paths = paths
            if len(paths) == count:
                break

    def _line(self, x0, y0, x1, y1):
        p1 = (self._sc(x0), self._sc(y0))
        p2 = (self._sc(x1), self._sc(y1))
        seg = [p1, p2]
        if p1 in self.firsts:
            seg = [p2, p1]
        self.paths.append(seg)
        self.firsts.add(seg[0])
