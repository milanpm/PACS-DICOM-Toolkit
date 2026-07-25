import sys
from pathlib import Path

import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from dicom_loader import load_dicom
from windowing import apply_window


class DicomViewer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.dataset = None
        self.pixel_array = None

        self.setWindowTitle("PACS DICOM Toolkit")
        self.resize(900, 700)

        self.open_button = QPushButton("Open DICOM")
        self.open_button.clicked.connect(self.open_dicom)

        self.image_label = QLabel("Open a DICOM file")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(512, 512)
        self.image_label.setStyleSheet(
            "background-color: black; color: white; border: 1px solid gray;"
        )

        self.patient_id_label = QLabel("-")
        self.patient_name_label = QLabel("-")
        self.modality_label = QLabel("-")
        self.image_size_label = QLabel("-")
        self.pixel_range_label = QLabel("-")

        metadata_layout = QFormLayout()
        metadata_layout.addRow("Patient ID:", self.patient_id_label)
        metadata_layout.addRow("Patient Name:", self.patient_name_label)
        metadata_layout.addRow("Modality:", self.modality_label)
        metadata_layout.addRow("Image Size:", self.image_size_label)
        metadata_layout.addRow("Pixel Range:", self.pixel_range_label)

        self.window_center_spin = QSpinBox()
        self.window_center_spin.setRange(-65535, 65535)
        self.window_center_spin.setValue(32768)
        self.window_center_spin.valueChanged.connect(self.update_image)

        self.window_width_spin = QSpinBox()
        self.window_width_spin.setRange(1, 131070)
        self.window_width_spin.setValue(65536)
        self.window_width_spin.valueChanged.connect(self.update_image)

        window_layout = QFormLayout()
        window_layout.addRow("Window Center:", self.window_center_spin)
        window_layout.addRow("Window Width:", self.window_width_spin)

        control_layout = QVBoxLayout()
        control_layout.addWidget(self.open_button)
        control_layout.addLayout(metadata_layout)
        control_layout.addSpacing(20)
        control_layout.addLayout(window_layout)
        control_layout.addStretch()

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.image_label, 1)
        main_layout.addLayout(control_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def open_dicom(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open DICOM File",
            str(Path.cwd() / "samples"),
            "DICOM Files (*.dcm);;All Files (*)",
        )

        if not file_path:
            return

        try:
            self.dataset, self.pixel_array = load_dicom(file_path)
            self.update_metadata()
            self.set_initial_window()
            self.update_image()
        except Exception as error:
            QMessageBox.critical(self, "DICOM Load Error", str(error))

    def update_metadata(self):
        rows, columns = self.pixel_array.shape

        self.patient_id_label.setText(
            str(getattr(self.dataset, "PatientID", "Unknown"))
        )
        self.patient_name_label.setText(
            str(getattr(self.dataset, "PatientName", "Unknown"))
        )
        self.modality_label.setText(
            str(getattr(self.dataset, "Modality", "Unknown"))
        )
        self.image_size_label.setText(f"{columns} x {rows}")
        self.pixel_range_label.setText(
            f"{self.pixel_array.min():.0f} ~ {self.pixel_array.max():.0f}"
        )

    def set_initial_window(self):
        pixel_min = float(self.pixel_array.min())
        pixel_max = float(self.pixel_array.max())

        default_center = (pixel_min + pixel_max) / 2
        default_width = max(pixel_max - pixel_min, 1)

        window_center = float(
            getattr(self.dataset, "WindowCenter", default_center)
        )
        window_width = float(
            getattr(self.dataset, "WindowWidth", default_width)
        )

        self.window_center_spin.blockSignals(True)
        self.window_width_spin.blockSignals(True)

        self.window_center_spin.setValue(round(window_center))
        self.window_width_spin.setValue(max(round(window_width), 1))

        self.window_center_spin.blockSignals(False)
        self.window_width_spin.blockSignals(False)

    def update_image(self):
        if self.pixel_array is None:
            return

        windowed = apply_window(
            self.pixel_array,
            self.window_center_spin.value(),
            self.window_width_spin.value(),
        )

        windowed = np.ascontiguousarray(windowed)
        height, width = windowed.shape

        image = QImage(
            windowed.data,
            width,
            height,
            windowed.strides[0],
            QImage.Format_Grayscale8,
        ).copy()

        pixmap = QPixmap.fromImage(image)
        pixmap = pixmap.scaled(
            self.image_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )

        self.image_label.setPixmap(pixmap)


def main():
    app = QApplication(sys.argv)
    viewer = DicomViewer()
    viewer.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
