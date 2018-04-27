class Point(object):
    """
    Point is a class that keeps an x-y pair of possibly-floating-point values and allows approximate comparison of those
    points by rounding them to only two decimal places without actually affecting their full precision.
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __hash__(self):
        return hash("{:.2f}{:.2f}".format(self.x, self.y))

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()


class PathBuilder(object):
    """
    The PathBuilder object collects a set of add_segment calls and then can reduce those to the
    smallest set of connected paths, closing them if possible.
    """
    def __init__(self):
        self.paths = []
        self.firsts = set()

    def add_segment(self, x0, y0, x1, y1):
        p1 = Point(x0, y0)
        p2 = Point(x1, y1)
        # make a line segment
        seg = [p1, p2]
        # but if two segments are known to start with the same value, reverse the new one
        if p1 in self.firsts:
            seg = [p2, p1]
        self.paths.append(seg)
        # We may still have overlapping firsts but that's OK; we're just using this to
        # accelerate some decision-making
        self.firsts.add(seg[0])

    def emit_paths(self, doc):
        """
        Walk the list of paths and emit them as either closed or open depending
        on if the endpoints are the same point.
        """
        for p in self.paths:
            pointsonly = [(pt.x, pt.y) for pt in p]
            if p[0] == p[-1]:
                doc.drawClosedPath(pointsonly)
            else:
                doc.drawOpenPath(pointsonly)

    def join_paths(self):
        """ Call _join_paths_1 repeatedly until it doesn't change any more. """
        while True:
            count = len(self.paths)
            paths = self._join_paths_1()
            self.paths = paths
            if len(paths) == count:
                break

    def _join_paths_1(self):
        """
        Create a new copy of the paths that concatenates some of them together if they can be joined.
        This doesn't attempt to find all paths, only to make the output list of paths shorter.

        Algorithm:
            While the list is not empty:
                Pop the last path off the list.
                Attempt to find a path elsewhere on the list to append it to, either as-is or reversed.
                If found:
                    remove the matching path from the input list,
                    concatenate the other one
                    put the combined result into the output.
                Else:
                    put the popped path into the output.
            Return the new list
        """
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

