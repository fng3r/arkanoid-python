import sys
import os.path

from PyQt5.QtCore import QUrl
from PyQt5.QtMultimedia import QMediaContent
from PyQt5.QtWidgets import (
    QApplication,
    QPushButton,
    QVBoxLayout,
    QStackedLayout,
    QWidget,
    QDesktopWidget,
    QMessageBox,
    QGroupBox,
    QSlider)
from PyQt5.QtGui import QPainter, QImage, QBrush, QPalette, QFont, QColor
from PyQt5.QtCore import Qt, QRectF, QTimer
from PyQt5.QtMultimedia import QMediaPlayer, QMediaPlaylist
from PyQt5.QtWidgets import QLabel
from game import GameModel
from core import Size, BallState


class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.screen = QDesktopWidget().screenGeometry()

        self.started = False
        self.paused = False
        self.left = False
        self.right = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        self.setWindowTitle('Arkanoid')

        self.main_menu = QWidget(self)
        self.settings = QWidget(self)
        self.game_widget = QWidget(self)
        self.game_widget.setMouseTracking(True)
        self.game_widget.mouseMoveEvent = self.mouse_move_event

        palette = QPalette()
        palette.setBrush(self.backgroundRole(),
                         QBrush(QImage(os.path.join('images', 'space.png'))))
        self.setPalette(palette)
        self.logo = QImage(os.path.join('images', 'logo.png'))

        self.media_player = QMediaPlayer()
        playlist = QMediaPlaylist()
        playlist.addMedia(QMediaContent(QUrl('space_music.mp3')))
        playlist.addMedia(QMediaContent(QUrl('space.mp3')))
        # self.media_player.setPlaylist(playlist)
        self.media_player.setMedia(QMediaContent(QUrl('space_music.mp3')))
        self.media_player.play()

        self.game = GameModel(Size(self.screen.width(), self.screen.height()))

        self.painter = QPainter()

        self.stacked = QStackedLayout(self)
        self.stacked.addWidget(self.game_widget)
        self.stacked.addWidget(self.settings)
        self.set_main_menu_layout()
        self.set_settings_layout()
        self.stacked.setCurrentWidget(self.main_menu)

        self.showFullScreen()

    def start(self):
        if not self.started:
            self.game = GameModel(Size(self.width(), self.height()))
            self.started = True
        self.left = self.right = False
        self.timer.start(12)
        self.change_current_widget(self.game_widget)

    def try_restart(self):
        reply = QMessageBox.question(
            self, 'Restart', 'Your score: %s. Do you want to restart?'
            % self.game.player.score, QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.start()
        else:
            self.go_to_main_menu()

    def notify_win(self):
        QMessageBox.information(self, 'Win', 'You win. Your score: %s'
                                % self.game.player.score)
        self.started = False
        self.go_to_main_menu()

    def go_to_main_menu(self):
        self.timer.stop()
        self.change_current_widget(self.main_menu)

    def quit(self):
        reply = QMessageBox.question(
            self, 'Quit', 'Do you really want to quit the game?',
            QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            APP.quit()

    def tick(self):
        if self.game.gameover:
            self.started = False
            self.try_restart()
        if self.game.won:
            self.notify_win()
        turn_rate = 1 if self.right else -1 if self.left else 0
        self.game.tick(turn_rate)
        self.repaint()

    def change_current_widget(self, widget):
        self.stacked.setCurrentWidget(widget)
        self.update()

    def set_main_menu_layout(self):
        vbox = QVBoxLayout(self.main_menu)

        self.add_button('Start', self.start, vbox)
        self.add_button('Settings', lambda: self.change_current_widget(
            self.settings), vbox)
        self.add_button('Quit', self.quit, vbox)

        vbox.setAlignment(Qt.AlignCenter)
        self.stacked.addWidget(self.main_menu)

    def set_settings_layout(self):
        vbox = QVBoxLayout(self.settings)
        groupbox = QGroupBox(self.settings)
        groupbox.setLayout(QVBoxLayout(groupbox))
        slider = QSlider(Qt.Horizontal)
        slider.setRange(10, 35)
        slider.setTickPosition(QSlider.TicksLeft)
        slider.setValue(self.game.settings.ball_velocity)
        label = QLabel('Ball speed')
        label.setStyleSheet('QLabel {color: gold;}')
        slider.valueChanged.connect(
            lambda: self.change_ball_velocity(slider.value()))
        groupbox.layout().addWidget(label, alignment=Qt.AlignCenter)
        groupbox.layout().addWidget(slider, alignment=Qt.AlignCenter)
        vbox.addWidget(groupbox)
        vbox.setAlignment(Qt.AlignCenter)

    def change_ball_velocity(self, value):
        self.game.settings.ball_velocity = value
        for ball in self.game.balls:
            ball.velocity = value

    def mouse_move_event(self, event):
        current_mouse_x = event.x()
        old_x = self.game.ship.x
        self.game.ship.location = (current_mouse_x, self.game.ship.y)
        delta_x = self.game.ship.x - old_x
        for ball in self.game.balls:
            if ball.state == BallState.Caught:
                ball.move(delta_x)

    def mousePressEvent(self, event):
        if not self.game.release_ball():
            self.game.shooting()

    def keyPressEvent(self, event):
        key = event.key()
        self.left = key == Qt.Key_Left
        self.right = key == Qt.Key_Right
        if key == Qt.Key_Escape:
            self.timer.stop()
            self.go_to_main_menu()
        if key == Qt.Key_Space:
            self.game.release_ball()
        if key == Qt.Key_X:
            self.game.shooting()
        if key == Qt.Key_P:
            self.paused = not self.paused
            if self.paused:
                self.timer.stop()
            else:
                self.timer.start()

    def keyReleaseEvent(self, event):
        key = event.key()
        if key == Qt.Key_Left:
            self.left = False
        elif key == Qt.Key_Right:
            self.right = False

    def paintEvent(self, event):
        self.painter.begin(self)
        self.draw()
        self.painter.end()

    def draw(self):
        if self.stacked.currentWidget() == self.main_menu:
            self.painter.drawImage((self.width() - self.logo.width()) / 2, 50,
                                   self.logo)

        if self.stacked.currentWidget() != self.game_widget or self.game.won:
            return

        self.painter.setRenderHint(self.painter.Antialiasing)
        self.painter.setFont(QFont('Times New Roman', 20))
        self.painter.setPen(QColor('gold'))

        self.painter.drawText(0, 20, 'Scores: %s'
                              % str(self.game.player.score))

        game = self.game
        self.painter.drawLine(game.frame.left, game.deadly_height,
                              game.frame.right, game.deadly_height)

        life_img = QImage(os.path.join('images', 'lifebonus.png'))
        draw_x = self.width() - life_img.width()
        draw_y = 0
        for _ in range(self.game.player.lives):
            self.painter.drawImage(draw_x, draw_y, life_img)
            draw_x -= life_img.width()

        self.draw_game_elements()

    def draw_game_elements(self):
        for entity in self.game.get_entities():
            self.painter.drawImage(
                QRectF(*entity.location, entity.width, entity.height),
                QImage(entity.get_image()))

    @staticmethod
    def add_button(text, callback, layout, alignment=Qt.AlignCenter):
        button = QPushButton(text)
        button.setFixedSize(400, 50)
        button.pressed.connect(callback)
        button.setStyleSheet(
            'QPushButton {'
            'font-size: 20px;}'
            'QPushButton:focus {'
            'color: rgb(255, 215, 0);'
            'background-color: rgb(0, 0, 255, 80);}')
        button.setAutoDefault(True)
        layout.addWidget(button, alignment=alignment)
        return button


if __name__ == '__main__':
    APP = QApplication(sys.argv)
    WINDOW = Window()
    APP.setOverrideCursor(Qt.BlankCursor)
    APP.exec_()
