import logging
import time
from reportlab.lib.units import mm
from reportlab.lib.colors import black
from boxmaker.dxf import DXFDoc
from boxmaker.svg import SVGDoc
from boxmaker.pdf import PDFDoc
from boxmaker.pathbuilder import PathBuilder, Point
import boxmaker

DOC_CLASSES = {
    'pdf': PDFDoc,
    'dxf': DXFDoc,
    'svg': SVGDoc,
}


# Find and return the closest odd number to the one passed in
def _closest_odd(number):
    num = int(float(number)+0.5)
    if num % 2 == 0:
        closest_odd = num-1
    else:
        closest_odd = num
    return float(closest_odd)


class Box:
    '''
    Handles actually drawing of the notched box to a file.  This class passes everything around
    in millimeters until it actually draws it at the low level.  It renders a files like this:

    legend: === (no joint), --- (joint)

    <pre>

              ( 5--------6
                |  w x d |
                8--------7 )
                5========6
                |  w x h |
                |        |
                1--------2
     4-------1  1--------2  2-------3
     | d x h |  |  w x d |  | d x h |
     8=======5  4--------3  6=======7
                3--------4
                |  w x h |
                |        |
                7========8
    </pre>
    '''

    def __init__(self, file_path, width, height, depth, thickness, cut_width, notch_length, bounding_box,
                 file_type, tray):
        self._logger = logging.getLogger(__name__)
        self._file_path = file_path
        self._desired_size = {'w': float(width), 'h': float(height), 'd': float(depth)}
        self._logger.debug(" desired box size: (w=%.2f, h=%.2f, d=%.2f)" %
                           (self._desired_size['w'], self._desired_size['h'], self._desired_size['d']))
        self._thickness = float(thickness)
        self._cut_width = float(cut_width)
        self._desired_notch_length = float(notch_length)
        self._bounding_box = bounding_box
        self._doc_cls = DOC_CLASSES[file_type]
        self._tray = tray
        self.paths = PathBuilder()

    def render(self):
        # set things up
        self._compute_dimensions()
        self._initialize_document()
        if self._bounding_box:
            self._draw_bounding_box()
        # 1. a W x H side (the back)
        self._draw_back()
        # 2. a D x H side (the left side)
        self._draw_left()
        # 3. a W X D side (the bottom)
        self._draw_bottom()
        # 4. a D x H side (the right side)
        self._draw_right()
        # 5. a W x H side (the front)
        self._draw_front()
        # 6. a W X D side (the top)
        if not self._tray:
            self._draw_top()        # and write out the file
        self.paths.join_paths()
        self.paths.emit_paths(self._doc)
        self._doc.save()

    def _draw_top(self):
        x0 = self._size['d'] + self._margin*2.0
        y0 = self._size['h']*2.0 + self._size['d'] + self._margin*4.0
        self._draw_horizontal_line(x0, y0,
                                   self._notch_length['w'], self._num_notches['w'],
                                   self._thickness, -1*self._cut_width/2.0, True, True)
        self._draw_horizontal_line(x0, y0+self._size['d']-self._thickness,
                                   self._notch_length['w'], self._num_notches['w'],
                                   self._thickness, -1*self._cut_width/2.0, False, True)
        self._draw_vertical_line(x0, y0,
                                 self._notch_length['d'], self._num_notches['d'],
                                 self._thickness, -1*self._cut_width/2.0, True, True)
        self._draw_vertical_line(x0+self._size['w']-self._thickness, y0,
                                 self._notch_length['d'], self._num_notches['d'],
                                 self._thickness, -1*self._cut_width/2.0, False, True)

    def _draw_back(self):
        x0, y0 = self._size['d'] + self._margin*2.0, self._margin
        if self._tray:
            self._draw_line(x0, y0, x0+self._size['w']-self._thickness, y0)
        else:
            self._draw_horizontal_line(x0, y0,
                                       self._notch_length['w'], self._num_notches['w'],
                                       self._thickness, self._cut_width/2.0, False, False)
        self._draw_horizontal_line(x0, y0+self._size['h']-self._thickness,
                                   self._notch_length['w'], self._num_notches['w'],
                                   self._thickness, self._cut_width/2.0, True, False)
        self._draw_vertical_line(x0, y0,
                                 self._notch_length['h'], self._num_notches['h'],
                                 self._thickness, -1*self._cut_width/2.0, False, False)
        self._draw_vertical_line(x0+self._size['w']-self._thickness, y0,
                                 self._notch_length['h'], self._num_notches['h'],
                                 self._thickness, -1*self._cut_width/2.0, False, False)

    def _draw_left(self):
        x0, y0 = self._margin, self._size['h'] + self._margin*2.0
        if self._tray:
            self._draw_line(x0, y0, x0+self._size['d']-self._thickness, y0)
        else:
            self._draw_horizontal_line(x0, y0,
                                       self._notch_length['d'], self._num_notches['d'],
                                       self._thickness, self._cut_width/2, False, False)
        self._draw_horizontal_line(x0, y0+self._size['h']-self._thickness,
                                   self._notch_length['d'], self._num_notches['d'],
                                   self._thickness, self._cut_width/2.0, True, False)
        self._draw_vertical_line(x0, y0, self._notch_length['h'], self._num_notches['h'],
                                 self._thickness, self._cut_width/2.0, False, False)
        self._draw_vertical_line(x0+self._size['d']-self._thickness, y0,
                                 self._notch_length['h'], self._num_notches['h'],
                                 self._thickness, -1*self._cut_width/2.0, False, False)

    def _draw_bottom(self):
        x0 = self._size['d'] + self._margin*2.0
        y0 = self._size['h'] + self._margin*2.0
        self._draw_horizontal_line(x0, y0,
                                   self._notch_length['w'], self._num_notches['w'],
                                   self._thickness, -1*self._cut_width/2.0, True, True)
        self._draw_horizontal_line(x0, y0+self._size['d']-self._thickness,
                                   self._notch_length['w'], self._num_notches['w'],
                                   self._thickness, -1*self._cut_width/2.0, False, True)
        self._draw_vertical_line(x0, y0,
                                 self._notch_length['d'], self._num_notches['d'],
                                 self._thickness, -1*self._cut_width/2.0, True, True)
        self._draw_vertical_line(x0+self._size['w']-self._thickness, y0,
                                 self._notch_length['d'], self._num_notches['d'],
                                 self._thickness, -1*self._cut_width/2.0, False, True)

    def _draw_right(self):
        x0 = self._size['d'] + self._size['w'] + self._margin*3.0
        y0 = self._size['h'] + self._margin*2.0
        if self._tray:
            self._draw_line(x0, y0, x0+self._size['d']-self._thickness, y0)
        else:
            self._draw_horizontal_line(x0, y0,
                                       self._notch_length['d'], self._num_notches['d'],
                                       self._thickness, self._cut_width/2, False, False)
        self._draw_horizontal_line(x0, y0+self._size['h']-self._thickness,
                                   self._notch_length['d'], self._num_notches['d'],
                                   self._thickness, self._cut_width/2.0, True, False)
        self._draw_vertical_line(x0, y0, self._notch_length['h'], self._num_notches['h'],
                                 self._thickness, self._cut_width/2.0, False, False)
        self._draw_vertical_line(x0+self._size['d']-self._thickness, y0,
                                 self._notch_length['h'], self._num_notches['h'],
                                 self._thickness, -1*self._cut_width/2.0, False, False)

    def _draw_front(self):
        x0 = self._size['d'] + self._margin*2.0
        y0 = self._size['h'] + self._size['d'] + self._margin*3.0
        self._draw_horizontal_line(x0, y0,
                                   self._notch_length['w'], self._num_notches['w'],
                                   self._thickness, self._cut_width/2.0, False, False)
        if self._tray:
            self._draw_line(x0, y0+self._size['h'],
                            x0+self._size['w']-self._thickness,
                            y0+self._size['h'])
        else:
            self._draw_horizontal_line(x0, y0+self._size['h']-self._thickness,
                                       self._notch_length['w'], self._num_notches['w'],
                                       self._thickness, self._cut_width/2.0, True, False)
        self._draw_vertical_line(x0, y0,
                                 self._notch_length['h'], self._num_notches['h'],
                                 self._thickness, -1*self._cut_width/2.0, False, False)
        self._draw_vertical_line(x0+self._size['w']-self._thickness, y0,
                                 self._notch_length['h'], self._num_notches['h'],
                                 self._thickness, -1*self._cut_width/2.0, False, False)

    def _compute_dimensions(self):
        # first enlarge the box to compensate for cut width
        self._size = {'w': self._desired_size['w'] + self._cut_width,
                      'h': self._desired_size['h'] + self._cut_width,
                      'd': self._desired_size['d'] + self._cut_width}
        # figure out how many notches for each side, trying to make notches about the right length.
        self._num_notches = {'w': _closest_odd(self._desired_size['w'] / self._desired_notch_length),
                             'h': _closest_odd(self._desired_size['h'] / self._desired_notch_length),
                             'd': _closest_odd(self._desired_size['d'] / self._desired_notch_length)}
        self._logger.debug(" notch count: (w=%d, h=%d, d=%d)" % (self._num_notches['w'], self._num_notches['h'],
                                                                 self._num_notches['d']))
        # compute exact notch lengths
        self._notch_length = {'w': self._size['w'] / self._num_notches['w'],
                              'h': self._size['h'] / self._num_notches['h'],
                              'd': self._size['d'] / self._num_notches['d']}
        self._logger.debug(" notch length: (w=%.2f, h=%.2f, d=%.2f)" % (self._notch_length['w'],
                                                                        self._notch_length['h'],
                                                                        self._notch_length['d']))
        # and compute the new width based on that (should be a NO-OP)
        self._margin = 10.0 + self._cut_width
        self._logger.debug(" margin: %.2f" % self._margin)
        self._size = {'w': self._num_notches['w'] * self._notch_length['w'],
                      'h': self._num_notches['h'] * self._notch_length['h'],
                      'd': self._num_notches['d'] * self._notch_length['d']}
        self._logger.debug(" box size: (w=%.2f, h=%.2f, d=%.2f)" % (self._size['w'], self._size['h'],
                                                                    self._size['d']))
        # compute how big the document will be based on the layout of the pieces
        self._box_pieces_size = {'w': self._size['d']*2.0 + self._size['w'],
                                 'h': self._size['h']*2.0 + self._size['d']*2.0}
        self._doc_size = {'w': self._box_pieces_size['w']+self._margin*4,
                          'h': self._box_pieces_size['h']+self._margin*5}
        # compute a bounding box size, in case we need to render it
        self._bounding_box_size = {'w': self._box_pieces_size['w']+self._margin*2,
                                   'h': self._box_pieces_size['h']+self._margin*3}

    def _initialize_document(self):
        # initialize the pdf file (based on layout of pieces)
        self._doc = self._doc_cls(self._file_path)
        self._doc.setPageSize([self._doc_size['w']*mm, self._doc_size['h']*mm])
        self._doc.setAuthor(boxmaker.APP_NAME+" "+boxmaker.APP_VERSION)
        self._doc.setStrokeColor(black)
        self._doc.setLineWidth(0.1)
        # print out some summary info for good record keeping purposes
        self._doc.drawString(15*mm, 35*mm, "Cut Width: %.4fmm" % self._cut_width)
        self._doc.drawString(15*mm, 30*mm, "Material Thickness: %.4fmm" % self._thickness)
        self._doc.drawString(15*mm, 25*mm, "W x D x H: %.2fmm x %.2fmm x %.2fmm" %
                             (self._size['w'], self._size['d'], self._size['h']))
        self._doc.drawString(15*mm, 20*mm, "Produced by "+boxmaker.APP_NAME+" v"+boxmaker.APP_VERSION +
                             " on "+time.strftime("%m/%d/%Y")+" at "+time.strftime("%H:%M:%S"))
        self._doc.drawString(15*mm, 15*mm, boxmaker.WEBSITE_URL)

    def _draw_bounding_box(self):
        # render a box around the whole thing to make resizing easier when imports fail in 3rd party tools
        self._doc.rect(self._margin*mm, self._margin*mm, self._bounding_box_size['w']*mm,
                       self._bounding_box_size['h']*mm)
        self._doc.drawString(15*mm, self._doc_size['h']*mm - 20*mm, "Bounding Box: %.2fmm x %.2fmm" %
                             (self._bounding_box_size['w'], self._bounding_box_size['h']))

    def _draw_horizontal_line(self, x0, y0, notch_width, notch_count, notch_height, cut_width, flip, smallside):
        x = x0
        for step in range(0, int(notch_count)):
            y = y0 if (((step % 2) == 0) ^ flip) else y0+notch_height
            if step == 0:  # start first edge in the right place
                if smallside:
                    self._draw_line(x+notch_height, y, x+notch_width+cut_width, y)
                else:
                    self._draw_line(x, y, x+notch_width+cut_width, y)
            elif step == (notch_count-1):  # shorter last edge
                self._draw_line(x-cut_width, y, x+notch_width-notch_height, y)
            elif step % 2 == 0:
                self._draw_line(x-cut_width, y, x+notch_width+cut_width, y)
            else:
                self._draw_line(x+cut_width, y, x+notch_width-cut_width, y)
            if step < (notch_count-1):
                if step % 2 == 0:
                    self._draw_line(x+notch_width+cut_width, y0+notch_height, x+notch_width+cut_width, y0)
                else:
                    self._draw_line(x+notch_width-cut_width, y0+notch_height, x+notch_width-cut_width, y0)
            x = x + notch_width

    def _draw_vertical_line(self, x0, y0, notch_width, notch_count, notch_height, cut_width, flip, smallside):
        y = y0
        for step in range(0, int(notch_count)):
            x = x0 if (((step % 2) == 0) ^ flip) else x0+notch_height
            if step == 0:
                if smallside:
                    self._draw_line(x, y+notch_height, x, y+notch_width+cut_width)
                else:
                    self._draw_line(x, y, x, y+notch_width+cut_width)
            elif step == (notch_count-1):
                if smallside:
                    self._draw_line(x, y-cut_width, x, y+notch_width-notch_height)
                else:
                    self._draw_line(x, y-cut_width, x, y+notch_width)
            elif step % 2 == 0:
                self._draw_line(x, y-cut_width, x, y+notch_width+cut_width)
            else:
                self._draw_line(x, y+cut_width, x, y+notch_width-cut_width)
            if step < (notch_count-1):
                if step % 2 == 0:
                    self._draw_line(x0+notch_height, y+notch_width+cut_width, x0, y+notch_width+cut_width)
                else:
                    self._draw_line(x0+notch_height, y+notch_width-cut_width, x0, y+notch_width-cut_width)
            y = y+notch_width

    def _draw_line(self, from_x, from_y, to_x, to_y):
        self.paths.add_segment(from_x*mm, from_y*mm, to_x*mm, to_y*mm)
