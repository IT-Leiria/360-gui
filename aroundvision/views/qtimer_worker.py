
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QTimer


class TimerWorker(QObject):
    """TimerWorker is just a simple timer with start and stop.

    :param frame_rate: loop every x seconds
    :type frame_rate: int
    :param show_frame: method called when timeout..
    :type show_frame: function
    """
    # Signals
    processed = pyqtSignal()

    def __init__(self, frame_rate=None, show_frame=None):
        """Constructor for TimerWorker."""
        super().__init__()
        self.frame_rate = frame_rate
        self.show_frame = show_frame
        self._timer = None

    @pyqtSlot()
    def start(self):
        """Start timer and connect with the slot received!"""
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.show_frame)
        self._timer.start(self.frame_rate)

    @pyqtSlot()
    def stop(self):
        """If we have timer stop it!"""
        if self._timer:
            self._timer.stop()

