from PySide import QtCore, QtGui

from ..support.tuple_math import TupleMath

class QtFramelessUi(QtGui.QLineEdit):
    """
    QT frameless widget base class
    """

    def __init__(self, window):
        """
        Constructor

        window - reference to Gui.getMainWindow()
        """

        super(QtFramelessUi, self).__init__(window)

        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.FramelessWindowHint)
        self.offset = (0.0, 0.0)
        self.position = (0.0, 0.0)

    def set_signal_callback(self, callback):
        """
        callback
        """

        self.editingFinished.connect(callback)

    def set_position(self, position=None):
        """
        Set the widget position.

        Position is a 2-tuple relative to GUI view X/Y coordinates
        """

        if not position:
            position = self.position

        self.position = position[:2]

        _pos = TupleMath.add(position, self.offset)

        self.move(position[0], position[1])

    def set_offset(self, offset):
        """
        Set the widget offset.

        Offset is specified as a 2-tuple in pixels
        """

        self.offset = offset[:2]
        self.set_position()

    def show(self, text=None, position=None):
        """
        Display the label with the provided text
        """

        self.set_position(position)

        if text:
            self.setText(text)

        print('show()')
        super().show()

    def hide(self):
        """
        Hide the widget
        """

        super().hide()
