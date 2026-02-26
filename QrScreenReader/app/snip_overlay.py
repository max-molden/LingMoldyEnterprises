from __future__ import annotations

from PySide6.QtCore import QPoint, QRect, Qt, Signal
from PySide6.QtGui import QColor, QMouseEvent, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QWidget


class SnipOverlay(QWidget):
    snip_captured = Signal(object)
    snip_cancelled = Signal()

    def __init__(self, screen_shot: QPixmap, screen_geometry: QRect) -> None:
        super().__init__()
        self._screen_shot = screen_shot
        self._screen_geometry = screen_geometry
        self._start = QPoint()
        self._end = QPoint()
        self._selecting = False

        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self.setWindowFlag(Qt.WindowType.Tool, True)
        self.setGeometry(self._screen_geometry)
        self.setCursor(Qt.CursorShape.CrossCursor)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self._screen_shot)

        dark = QColor(0, 0, 0, 110)
        painter.fillRect(self.rect(), dark)

        selection = QRect(self._start, self._end).normalized()
        if not selection.isNull():
            painter.drawPixmap(selection, self._screen_shot, selection)
            painter.setPen(QPen(QColor("#00AEEF"), 2))
            painter.drawRect(selection)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._start = event.position().toPoint()
            self._end = self._start
            self._selecting = True
            self.update()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._selecting:
            self._end = event.position().toPoint()
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self._selecting:
            self._selecting = False
            self._end = event.position().toPoint()
            rect = QRect(self._start, self._end).normalized()

            if rect.width() < 5 or rect.height() < 5:
                self.snip_cancelled.emit()
            else:
                crop = self._screen_shot.copy(rect)
                self.snip_captured.emit(crop.toImage())

            self.close()

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self.snip_cancelled.emit()
            self.close()
