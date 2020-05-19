
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QTimer


class TimerWorker(QObject):
    """
    TimerWorker is just a simple timer with start and stop.
    - frame_rate: loop every x seconds
    - show_frame: method called when timeout..
    """
    processed = pyqtSignal()

    def __init__(self, frame_rate, show_frame):
        super().__init__()
        self.frame_rate = frame_rate
        self.show_frame = show_frame

    @pyqtSlot()
    def start(self):
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.show_frame)
        self._timer.start(self.frame_rate)

    @pyqtSlot()
    def stop(self):
        self._timer.stop()
