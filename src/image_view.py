from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QGraphicsPixmapItem, QGraphicsScene, QGraphicsView


class ImageView(QGraphicsView):
    """DICOM 이미지의 확대, 축소 및 이동을 담당하는 뷰."""
    
    zoom_changed = pyqtSignal(int)

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

        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        self.setRenderHint(QPainter.SmoothPixmapTransform)

        self.setAlignment(Qt.AlignCenter)
        self.setBackgroundBrush(Qt.black)

    def set_pixmap(self, pixmap):
        """표시할 이미지를 설정하고 화면에 맞춘다."""
        self.pixmap_item.setPixmap(pixmap)
        self.scene.setSceneRect(self.pixmap_item.boundingRect())
        self.fit_to_view()

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
