from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QGraphicsPixmapItem, QGraphicsScene, QGraphicsView


class ImageView(QGraphicsView):
    """DICOM 이미지의 확대, 축소 및 이동을 담당하는 뷰."""

    zoom_changed = pyqtSignal(int)
    window_changed = pyqtSignal(float, float)
    pixel_position_changed = pyqtSignal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        self.pixmap_item = QGraphicsPixmapItem()
        self.scene.addItem(self.pixmap_item)

        self.zoom_factor = 1.0
        self.zoom_step = 1.25
        self.min_zoom = 0.1
        self.max_zoom = 10.0

        self.window_center = 0.0
        self.window_width = 1.0
        self.default_window_center = 0.0
        self.default_window_width = 1.0

        self.adjusting_window = False
        self.window_drag_start = None
        self.drag_start_center = 0.0
        self.drag_start_width = 1.0

        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        self.setRenderHint(QPainter.SmoothPixmapTransform)

        self.setAlignment(Qt.AlignCenter)
        self.setBackgroundBrush(Qt.black)
        self.setMouseTracking(True)

    def set_pixmap(self, pixmap, fit=False):
        """표시할 이미지를 설정하며 필요할 때만 화면에 맞춘다."""
        self.pixmap_item.setPixmap(pixmap)
        self.scene.setSceneRect(self.pixmap_item.boundingRect())

        if fit:
            self.fit_to_view()

    def set_window_values(self, center, width, set_default=False):
        """현재 Window Center/Width 값을 저장한다."""
        self.window_center = float(center)
        self.window_width = max(float(width), 1.0)

        if set_default:
            self.default_window_center = self.window_center
            self.default_window_width = self.window_width

    def reset_window(self):
        """DICOM을 열었을 때의 Window 값으로 되돌린다."""
        self.set_window_values(
            self.default_window_center,
            self.default_window_width,
        )
        self.window_changed.emit(
            self.window_center,
            self.window_width,
        )

    def mousePressEvent(self, event):
        """오른쪽 버튼을 누르면 Window 조절을 시작한다."""
        if (
            event.button() == Qt.RightButton
            and not self.pixmap_item.pixmap().isNull()
        ):
            self.adjusting_window = True
            self.window_drag_start = event.pos()
            self.drag_start_center = self.window_center
            self.drag_start_width = self.window_width
            self.setDragMode(QGraphicsView.NoDrag)
            self.setCursor(Qt.SizeAllCursor)
            event.accept()
            return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """마우스 이동을 처리하고 우클릭 드래그 시 WW/WL을 조절한다."""
        if self.adjusting_window and self.window_drag_start is not None:
            delta = event.pos() - self.window_drag_start
            scale = max(abs(self.drag_start_width) / 500.0, 1.0)

            center = self.drag_start_center - delta.y() * scale
            width = max(
                1.0,
                self.drag_start_width + delta.x() * scale,
            )

            self.set_window_values(center, width)
            self.window_changed.emit(center, width)
            event.accept()
            return

        if not self.pixmap_item.pixmap().isNull():
            scene_pos = self.mapToScene(event.pos())
            image_pos = self.pixmap_item.mapFromScene(scene_pos)

            x = int(image_pos.x())
            y = int(image_pos.y())

            pixmap = self.pixmap_item.pixmap()

            if 0 <= x < pixmap.width() and 0 <= y < pixmap.height():
                self.pixel_position_changed.emit(x, y)

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """오른쪽 버튼을 놓으면 Window 조절을 종료한다."""
        if event.button() == Qt.RightButton and self.adjusting_window:
            self.adjusting_window = False
            self.window_drag_start = None
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self.unsetCursor()
            event.accept()
            return

        super().mouseReleaseEvent(event)

    def wheelEvent(self, event):
        """마우스 휠로 이미지를 확대하거나 축소한다."""
        if self.pixmap_item.pixmap().isNull():
            return

        if event.angleDelta().y() > 0:
            new_zoom = self.zoom_factor * self.zoom_step
            scale_factor = self.zoom_step
        else:
            new_zoom = self.zoom_factor / self.zoom_step
            scale_factor = 1 / self.zoom_step

        if self.min_zoom <= new_zoom <= self.max_zoom:
            self.scale(scale_factor, scale_factor)
            self.zoom_factor = new_zoom
            self.zoom_changed.emit(self.get_zoom_percentage())

    def fit_to_view(self):
        """이미지를 현재 화면 크기에 맞춘다."""
        if self.pixmap_item.pixmap().isNull():
            return

        self.resetTransform()
        self.fitInView(self.pixmap_item, Qt.KeepAspectRatio)
        self.zoom_factor = self.transform().m11()
        self.zoom_changed.emit(self.get_zoom_percentage())

    def reset_view(self):
        """확대/축소 및 이동 상태를 초기화한다."""
        self.fit_to_view()

    def get_zoom_percentage(self):
        """현재 확대 배율을 백분율로 반환한다."""
        return round(self.zoom_factor * 100)
