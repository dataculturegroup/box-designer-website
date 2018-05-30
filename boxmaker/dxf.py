# By Asher Blum, May 2016
# Crude DXF writer; outputs lines and text

FONT_SIZE = 8.0
TEXT_WIDTH_FACTOR = 0.75


class DXFDoc(object):

    def __init__(self, filename):
        self.chunks = []
        self.filename = filename
        self.add_head()
        self.has_tail = False

    def setPageSize(self, _):
        pass

    def setAuthor(self, _):
        pass

    def setStrokeColor(self, _):
        pass

    def setLineWidth(self, _):
        pass

    def drawString(self, x, y, st):
        # String must be free of metacharacters
        pairs = [
                (0, 'TEXT'),
                (5, '4D'),
                (8, 0),
                (6, 'BYBLOCK'),
                (10, x),
                (20, y),
                (30, 0),
                (40, FONT_SIZE),
                (41, TEXT_WIDTH_FACTOR),
                (1, st),
        ]
        self._add_ent(pairs)

    def rect(self, x, y, w, h):
        points = [(x, y), (x+w, y), (x+w, y+h), (x, y+h)]
        for i, pt in enumerate(points):
            self._line((pt, points[(i+1) % 4]))

    def drawClosedPath(self, p):
        # just draw all the segments
        start = p[0]
        for end in p[1:]:
            self._line((start, end))
            start = end

    def drawOpenPath(self, p):
        # same as the closed path ones since we're just drawing segments
        self.drawClosedPath(p)

    def save(self):
        if not self.has_tail:
            self.add_tail()
            self.has_tail = True
        ofh = open(self.filename, 'w')
        for chunk in self.chunks:
            ofh.write(chunk)

    # end public API

    def _line(self, line):
        # Given line=((x,y), (x,y)) add line
        pairs = [
                (0, 'LINE'),
                (5, '4D'),
                (8,    0),
                (10, line[0][0]),
                (20, line[0][1]),
                (30, 0.0),
                (11, line[1][0]),
                (21, line[1][1]),
                (31, 0.0),
        ]
        self._add_ent(pairs)

    def _add_ent(self, pairs):
        pairs = [('%3d' % a, str(b)) for a, b in pairs]
        lines = ["\r\n".join(p) for p in pairs]
        obuf = "\r\n".join(lines) + "\r\n"
        self.chunks.append(obuf)

    def add_tail(self):
        # DXF footer; place after last entity
        pairs = [
            (0, 'ENDSEC'),
            (0, 'EOF'),
        ]
        self._add_ent(pairs)

    def add_head(self):
        # Add a minimal DXF header. Entities should follow immediately
        pairs = [
            (0, 'SECTION'),
            (2, 'HEADER'),
            (9, '$ACADVER'),
            (1, 'AC1009'),
            (0, 'ENDSEC'),
            (0, 'SECTION'),
            (2, 'TABLES'),
            (0, 'TABLE'),
            (2, 'VPORT'),
            (70, 1),
            (0, 'VPORT'),
            (2, '*ACTIVE'),
            (70, 0),
            (10, 0.0),
            (20, 0.0),
            (11, 1.0),
            (21, 1.0),
            (12, 344.1869158878504),
            (22, 148.5),
            (13, 0.0),
            (23, 0.0),
            (14, 10.0),
            (24, 10.0),
            (15, 10.0),
            (25, 10.0),
            (16, 0.0),
            (26, 0.0),
            (36, 1.0),
            (17, -134.1869158878504),
            (27, 0.0),
            (37, 0.0),
            (40, 385.2),
            (41, 1.11214953271028),
            (42, 50.0),
            (43, 0.0),
            (44, 0.0),
            (50, 0.0),
            (51, 0.0),
            (71, 16),
            (72, 1000),
            (73, 1),
            (74, 3),
            (75, 0),
            (76, 0),
            (77, 0),
            (78, 0),
            (0, 'ENDTAB'),
            (0, 'TABLE'),
            (2, 'LTYPE'),
            (70, 1),
            (0, 'LTYPE'),
            (2, 'CONTINUOUS'),
            (70, 0),
            (3, 'Solid line'),
            (72, 65),
            (73, 0),
            (40, 0.0),
            (0, 'ENDTAB'),
            (0, 'TABLE'),
            (2, 'LAYER'),
            (70, 1),
            (0, 'LAYER'),
            (2, '0'),
            (70, 0),
            (62, 7),
            (6, 'CONTINUOUS'),
            (0, 'ENDTAB'),
            (0, 'TABLE'),
            (2, 'STYLE'),
            (70, 1),
            (0, 'STYLE'),
            (2, 'STANDARD'),
            (70, 0),
            (40, 0.0),
            (41, 1.0),
            (50, 0.0),
            (71, 0),
            (42, 2.5),
            (3, 'arial.ttf'),
            (4, ''),
            (0, 'ENDTAB'),
            (0, 'TABLE'),
            (2, 'VIEW'),
            (70, 0),
            (0, 'ENDTAB'),
            (0, 'TABLE'),
            (2, 'UCS'),
            (70, 0),
            (0, 'ENDTAB'),
            (0, 'TABLE'),
            (2, 'APPID'),
            (70, 1),
            (0, 'APPID'),
            (2, 'ACAD'),
            (70, 0),
            (0, 'ENDTAB'),
            (0, 'TABLE'),
            (2, 'DIMSTYLE'),
            (70, 1),
            (0, 'ENDTAB'),
            (0, 'ENDSEC'),
            (0, 'SECTION'),
            (2, 'BLOCKS'),
            (0, 'ENDSEC'),
            (0, 'SECTION'),
            (2, 'ENTITIES'),
        ]
        self._add_ent(pairs)
