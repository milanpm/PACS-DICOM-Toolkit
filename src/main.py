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
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from anonymizer import save_anonymized_dicom
from dicom_loader import extract_metadata, load_dicom
from windowing import apply_window


class DicomViewer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.dataset = None
        self.pixel_array = None
        self.current_file_path = None

        self.setWindowTitle("PACS DICOM Toolkit")
        self.resize(900, 700)

        # DICOM 열기 버튼
        self.open_button = QPushButton("Open DICOM")
        self.open_button.clicked.connect(self.open_dicom)

        # PNG 저장 버튼
        self.save_png_button = QPushButton("Save PNG")
        self.save_png_button.setEnabled(False)
        self.save_png_button.clicked.connect(self.save_png)

        # 익명화 저장 버튼
        self.anonymize_button = QPushButton("Save Anonymized DICOM")
        self.anonymize_button.setEnabled(False)
        self.anonymize_button.clicked.connect(self.save_anonymized)

        # 영상 표시 영역
        self.image_label = QLabel("Open a DICOM file")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(512, 512)
        self.image_label.setStyleSheet(
            "background-color: black;"
            "color: white;"
            "border: 1px solid gray;"
        )

        # 메타데이터 표시
        self.patient_id_label = QLabel("-")
        self.patient_name_label = QLabel("-")
        self.study_date_label = QLabel("-")
        self.modality_label = QLabel("-")
        self.image_size_label = QLabel("-")
        self.pixel_spacing_label = QLabel("-")
        self.pixel_range_label = QLabel("-")

        metadata_layout = QFormLayout()
        metadata_layout.addRow("Patient ID:", self.patient_id_label)
        metadata_layout.addRow("Patient Name:", self.patient_name_label)
        metadata_layout.addRow("Study Date:", self.study_date_label)
        metadata_layout.addRow("Modality:", self.modality_label)
        metadata_layout.addRow("Image Size:", self.image_size_label)
        metadata_layout.addRow("Pixel Spacing:", self.pixel_spacing_label)
        metadata_layout.addRow("Pixel Range:", self.pixel_range_label)

        # 메타데이터 검색
        self.metadata_search_input = QLineEdit()
        self.metadata_search_input.setPlaceholderText(
            "Enter tag name or keyword"
        )

        self.metadata_search_button = QPushButton("Search")
        self.metadata_search_button.clicked.connect(
            self.search_metadata
        )

        self.metadata_search_result = QTextEdit()
        self.metadata_search_result.setReadOnly(True)
        self.metadata_search_result.setMinimumHeight(120)

        # Window Center
        self.window_center_spin = QSpinBox()
        self.window_center_spin.setRange(-65535, 65535)
        self.window_center_spin.setValue(32768)
        self.window_center_spin.valueChanged.connect(self.update_image)

        # Window Width
        self.window_width_spin = QSpinBox()
        self.window_width_spin.setRange(1, 131070)
        self.window_width_spin.setValue(65536)
        self.window_width_spin.valueChanged.connect(self.update_image)

        window_layout = QFormLayout()
        window_layout.addRow("Window Center:", self.window_center_spin)
        window_layout.addRow("Window Width:", self.window_width_spin)

        # 오른쪽 제어 영역
        control_layout = QVBoxLayout()
        control_layout.addWidget(self.open_button)
        control_layout.addWidget(self.save_png_button)
        control_layout.addWidget(self.anonymize_button)
        control_layout.addLayout(metadata_layout)
        control_layout.addWidget(QLabel("Metadata Search"))

        search_layout = QHBoxLayout()
        search_layout.addWidget(self.metadata_search_input)
        search_layout.addWidget(self.metadata_search_button)

        control_layout.addLayout(search_layout)
        control_layout.addWidget(self.metadata_search_result)
        control_layout.addSpacing(20)
        control_layout.addLayout(window_layout)
        control_layout.addStretch()

        # 전체 화면 구성
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.image_label, 1)
        main_layout.addLayout(control_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def open_dicom(self):
        """DICOM 파일을 선택하고 화면에 표시합니다."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open DICOM File",
            str(Path.cwd() / "samples"),
            "DICOM Files (*.dcm);;All Files (*)",
        )

        if not file_path:
            return

        try:
            dataset, pixel_array = load_dicom(file_path)

            self.dataset = dataset
            self.pixel_array = pixel_array
            self.current_file_path = file_path

            self.save_png_button.setEnabled(True)
            self.anonymize_button.setEnabled(True)

            self.update_metadata()
            self.set_initial_window()
            self.update_image()

        except Exception as error:
            QMessageBox.critical(
                self,
                "DICOM Load Error",
                str(error),
            )

    def update_metadata(self):
        """현재 DICOM의 주요 정보를 화면에 표시합니다."""
        if self.dataset is None or self.pixel_array is None:
            return

        metadata = extract_metadata(self.dataset)

        self.patient_id_label.setText(metadata["Patient ID"])
        self.patient_name_label.setText(metadata["Patient Name"])
        self.study_date_label.setText(metadata["Study Date"])
        self.modality_label.setText(metadata["Modality"])
        self.image_size_label.setText(
            f'{metadata["Columns"]} x {metadata["Rows"]}'
        )
        self.pixel_spacing_label.setText(metadata["Pixel Spacing"])
        self.pixel_range_label.setText(
            f"{self.pixel_array.min():.0f} ~ "
            f"{self.pixel_array.max():.0f}"
        )

    def search_metadata(self):
        """태그 이름 또는 키워드로 DICOM 메타데이터를 검색합니다."""
        if self.dataset is None:
            self.metadata_search_result.setText(
                "Please open a DICOM file first."
            )
            return

        keyword = self.metadata_search_input.text().strip().lower()

        if not keyword:
            self.metadata_search_result.setText(
                "Please enter a search keyword."
            )
            return

        results = []

        for element in self.dataset:
            tag_name = element.name.lower()
            tag_keyword = element.keyword.lower()

            if keyword in tag_name or keyword in tag_keyword:
                results.append(
                    f"{element.tag} {element.name}: {element.value}"
                )

        if results:
            self.metadata_search_result.setText("\n".join(results))
        else:
            self.metadata_search_result.setText(
                "No matching metadata found."
            )

    def set_initial_window(self):
        """DICOM 또는 픽셀 범위를 이용해 초기 Window 값을 설정합니다."""
        if self.pixel_array is None:
            return

        pixel_min = float(self.pixel_array.min())
        pixel_max = float(self.pixel_array.max())

        default_center = (pixel_min + pixel_max) / 2
        default_width = max(pixel_max - pixel_min, 1)

        window_center = self.get_numeric_value(
            getattr(
                self.dataset,
                "WindowCenter",
                default_center,
            ),
            default_center,
        )

        window_width = self.get_numeric_value(
            getattr(
                self.dataset,
                "WindowWidth",
                default_width,
            ),
            default_width,
        )

        self.window_center_spin.blockSignals(True)
        self.window_width_spin.blockSignals(True)

        self.window_center_spin.setValue(
            round(window_center)
        )
        self.window_width_spin.setValue(
            max(round(window_width), 1)
        )

        self.window_center_spin.blockSignals(False)
        self.window_width_spin.blockSignals(False)

    @staticmethod
    def get_numeric_value(value, default):
        """단일 값 또는 여러 DICOM 값 중 첫 번째 값을 숫자로 변환합니다."""
        try:
            if isinstance(value, (list, tuple)):
                value = value[0]

            if hasattr(value, "__len__") and not isinstance(
                value,
                (str, bytes),
            ):
                value = value[0]

            return float(value)

        except (TypeError, ValueError, IndexError):
            return float(default)

    def update_image(self):
        """Window Center/Width를 적용하여 영상을 갱신합니다."""
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

    def save_png(self):
        """현재 Window 설정이 적용된 영상을 PNG로 저장합니다."""
        if self.pixel_array is None or not self.current_file_path:
            QMessageBox.warning(
                self,
                "No DICOM File",
                "Please open a DICOM file first.",
            )
            return

        source_path = Path(self.current_file_path)
        default_output_path = source_path.with_suffix(".png")

        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save PNG Image",
            str(default_output_path),
            "PNG Images (*.png);;All Files (*)",
        )

        if not output_path:
            return

        if not Path(output_path).suffix:
            output_path += ".png"

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

        if image.save(output_path, "PNG"):
            QMessageBox.information(
                self,
                "PNG Save Complete",
                f"PNG image saved:\n{output_path}",
            )
        else:
            QMessageBox.critical(
                self,
                "PNG Save Error",
                "Failed to save the PNG image.",
            )

    def save_anonymized(self):
        """현재 DICOM을 익명화하여 새 파일로 저장합니다."""
        if not self.current_file_path:
            QMessageBox.warning(
                self,
                "No DICOM File",
                "Please open a DICOM file first.",
            )
            return

        source_path = Path(self.current_file_path)

        default_output_path = source_path.with_name(
            f"{source_path.stem}_anonymized{source_path.suffix}"
        )

        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Anonymized DICOM",
            str(default_output_path),
            "DICOM Files (*.dcm);;All Files (*)",
        )

        if not output_path:
            return

        if not Path(output_path).suffix:
            output_path += ".dcm"

        try:
            saved_path = save_anonymized_dicom(
                self.current_file_path,
                output_path,
            )

            QMessageBox.information(
                self,
                "Anonymization Complete",
                f"Anonymized DICOM saved:\n{saved_path}",
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Anonymization Error",
                str(error),
            )

    def resizeEvent(self, event):
        """창 크기가 변경되면 영상도 다시 맞춥니다."""
        super().resizeEvent(event)

        if self.pixel_array is not None:
            self.update_image()


def main():
    app = QApplication(sys.argv)

    viewer = DicomViewer()
    viewer.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()