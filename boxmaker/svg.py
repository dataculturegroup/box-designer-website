# By Kent Quirk, April 2018
# SVG writer; outputs lines and text

# Although SVG is an XML-based language, XML manipulation is annoyingly complicated for what we need
# to do here, so we're just going to treat set things up with a template and embed strings.

# This system exists generate SVG files -- in particular to use with the Glowforge laser cutter. One thing that
# makes using the Glowforge UI work better is for SVGs to use closed paths rather than a semi-random selection of
# lines. Consequently, what this driver does is collect all of the line commands and record them; on the
# save call it concatenates them together into a set of paths.

from string import Template

tmpl_svg = Template("""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg width="${point_width}pt" height="${point_height}pt" version="1.1"
    viewBox="0 0 ${point_width} ${point_height}"
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

PIXEL_TO_POINT = 0.75


class SVGDoc(object):

    def __init__(self, filename):
        self.comments = []
        self.elements = []
        self.paths = []
        self.firsts = set()
        self.filename = filename
        self.stroke_color = "black"
        self.line_width = 0.5  # default is mm so we need to convert
        self.page_size = [0, 0]
        self.author = ''

    def setPageSize(self, page_size):
        self.page_size = page_size

    def setAuthor(self, author):
        self.author = author

    def setStrokeColor(self, col):
        self.stroke_color = col

    def setLineWidth(self, lw):
        self.line_width = lw

    def drawString(self, x, y, st):
        # String must be free of metacharacters
        self.comments.append((x, y, st))

    def rect(self, x, y, w, h):
        self.elements.append(tmpl_rect.substitute(dict(x=self._sc(x), y=self._sc(y), w=self._sc(w), h=self._sc(h))))

    def drawClosedPath(self, p):
        s = "M{},{}".format(self._sc(p[0][0]), self._sc(p[0][1]))
        s += ''.join(["L{},{}".format(self._sc(pt[0]), self._sc(pt[1])) for pt in p[1:-1]])
        s += 'Z'
        self.elements.append(tmpl_path.substitute(dict(
            path=s,
            stroke_color=self._col(self.stroke_color),
            stroke_pixels=self._sc(self.line_width)
            )))

    def drawOpenPath(self, p):
        s = "M{},{}".format(self._sc(p[0][0]), self._sc(p[0][1]))
        s += ''.join(["L{},{}".format(self._sc(pt[0]), self._sc(pt[1])) for pt in p[1:]])
        self.elements.append(tmpl_path.substitute(dict(
            path=s,
            stroke_color=self._col(self.stroke_color),
            stroke_pixels=self._sc(self.line_width)
            )))

    def save(self):
        s = ''.join([e for e in self.elements])
        pgw, pgh = self._sc(self.page_size[0]), self._sc(self.page_size[1])
        # To support different DPI viewers, we shoudl encode the page size in points, not pixels.  This makes it work
        #  in both InkScape and Illustrator.
        svg = tmpl_svg.substitute(dict(
            point_width=self._pixel_to_point(pgw),
            point_height=self._pixel_to_point(pgh),
            contents=s))
        ofh = open(self.filename, 'w')
        ofh.write(svg)
        ofh.close()

    # end public API

    @staticmethod
    def _sc(v):
        # converts from mm to pixels as a numeric string
        return "{:.2f}".format(v)  # * 96 / 25.4)

    @staticmethod
    def _col(color):
        # generates a CSS color from a reportlab color
        return '#'+color.hexval()[2:]

    @staticmethod
    def _pixel_to_point(pixels):
        return "{:.2f}".format(float(pixels) * PIXEL_TO_POINT)
