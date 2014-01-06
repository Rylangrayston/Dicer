class MoveModes:
    RAPID = 'rapid'
    FEED = 'feed'

class GcodeWriter(object):
    """Takes layer information from the Blender slicer and saves it to a file in GCODE format."""
    def __init__(self, file, feed_rate, rapid_rate):
        self._file = file
        self._feed_rate = feed_rate
        self._rapid_rate = rapid_rate
        self._move_mode = None
        self._current_height = None
        self._current_location = None

    def moveToHeight(self, height):
        if self._current_height is not None:
            if height < self._current_height:
                raise AssertionError('Requested to move back down from height %f to height %f!' % (
                    self._current_height, height
                ))
            if height == self._current_height:
                return
        self._set_move_mode(MoveModes.RAPID)
        self._file.write('G1 Z%.2f F%.2f\n' % (height, self._rapid_rate))
        self._current_height = height

    def drawPath(self, path):
        if self._current_location is None or self._current_location != path[0]:
            self._set_move_mode(MoveModes.RAPID)
            self._move_to_location(path[0])
        self._set_move_mode(MoveModes.FEED)
        for location in path[1:]:
            self._move_to_location(location)

    def _set_move_mode(self, mode):
        if self._move_mode != mode:
            if mode == MoveModes.RAPID:
                self._file.write('M103\n')
            elif mode == MoveModes.FEED:
                self._file.write('M101\n')
            else:
                raise AssertionError('Unknown move mode "%s"' % mode)
            self._move_mode = mode

    def _move_to_location(self, location):
        if location == self._current_location:
            return
        if self._move_mode == MoveModes.FEED:
            rate = self._feed_rate
        elif self._move_mode == MoveModes.RAPID:
            rate = self._rapid_rate
        else:
            raise AssertionError('Unexpected move mode "%s"' % self._move_mode)
        self._file.write('G1 X%.2f Y%.2f F%.2f\n' % (location[0], location[1], rate))
        self._current_location = location
