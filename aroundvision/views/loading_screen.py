
from PyQt5.QtCore import Qt, QTimer, QRect, pyqtSignal
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QLabel, QDialog, QVBoxLayout


class LoadingScreen(QDialog):
    """
    Loading Screen: create a qmovie with the animation gif received
    during the display time in seconds.

    Methods
    -------
    create_qmovie()
        Create a QMovie with the loading_gif_filename.
    adjust_loading_position(parent_geometry: QRect)
        Adjust loading position with parent geometry.
    start_animation()
        Start the animation.
    stop_animation()
        Stop the animation.
    get_x_position(parent_width: int)
        Get x position to move the animation gif.
    get_y_position(parent_height: int)
        Get y position to move the animation gif.
    """

    # Signals
    close_signal = pyqtSignal()

    def __init__(self, parent=None, loading_gif_filename=None, display_time=None):
        """
        Parameters
        ----------
        parent : QWidget
            Parent who call LoadingScreen
        loading_gif_filename : str
            Filename with animation gif
        display_time : int
            Animation display time in milliseconds
        """
        super(LoadingScreen, self).__init__(parent)
        # Variables
        self.parent = parent
        self.loading_gif_filename = loading_gif_filename
        self.label_animation = None
        self.movie = None

        # widget configurations
        self.setFixedSize(115, 115)  # size based on animation gif sized
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.CustomizeWindowHint)
        self.setLayout(QVBoxLayout())

        self.create_qmovie()

        # Start animation
        timer = QTimer(self)
        self.start_animation()
        timer.singleShot(display_time, self.stop_animation)

    def create_qmovie(self) -> None:
        """Create a QMovie with the loading_gif_filename."""
        self.label_animation = QLabel(self)
        self.movie = QMovie(self.loading_gif_filename)
        self.label_animation.setMovie(self.movie)
        self.layout().addWidget(self.label_animation)
        # Add text to label..
        self.layout().addWidget(QLabel("Loading ..."))
        self.adjustSize()
        # center loading gif in parent center..
        self.move(self.get_x_position(self.parent.geometry().width()),
                  self.get_y_position(self.parent.geometry().height()))

    def adjust_loading_position(self, parent_geometry: QRect) -> None:
        """Adjust loading position with parent geometry."""
        self.move(self.get_x_position(parent_geometry.width()),
                  self.get_y_position(parent_geometry.height()))

    def start_animation(self) -> None:
        """Start the animation."""
        self.movie.start()

    def stop_animation(self) -> None:
        """Stop the animation.

        When the animation is closed this emit a signal if parent
        want to do something with this ..
        """
        self.movie.stop()
        self.close()
        self.close_signal.emit()  # emit signal if parent want to do something..

    def get_x_position(self, parent_width: int) -> int:
        """Get x position to move the animation gif.

        parent_width : int
            parent width used to compute x center position ..
        """
        return int(((parent_width - self.width()) / 2) + 17)  # 17 -> just to stay on the center

    def get_y_position(self, parent_height: int) -> int:
        """Get y position to move the animation gif.

        Parameters
        ----------
        parent_height : int
            parent height used to compute y center position ..
        """
        return int((parent_height - self.height()) / 2)
