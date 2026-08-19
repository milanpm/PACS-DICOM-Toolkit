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
from image_view import ImageView


class DicomViewer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.dataset = None
        self.pixel_array = None
        self.current_file_path = None
        self.measurement_points = []

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
        self.image_view = ImageView()
        self.image_view.setMinimumSize(512, 512)

        # View 초기화 버튼
        self.reset_view_button = QPushButton("Reset View")
        self.reset_view_button.clicked.connect(
            self.image_view.reset_view
        )

        self.reset_window_button = QPushButton("Reset Window")
        self.reset_window_button.clicked.connect(
            self.image_view.reset_window
        )

        self.clear_roi_button = QPushButton("Clear ROI")
        self.clear_roi_button.clicked.connect(
            self.clear_roi_measurement
        )

        # Zoom 배율 표시
        self.zoom_label = QLabel("Zoom: 100%")
        self.window_label = QLabel("WC: -  WW: -")
        self.pixel_info_label = QLabel(
            "X: -  Y: -  Pixel: -  HU: -"
        )
        self.distance_label = QLabel("Distance: -")
        self.roi_label = QLabel("ROI: Ctrl + Left Drag")

        self.image_view.zoom_changed.connect(
            self.update_zoom_label
        )
        self.image_view.window_changed.connect(
            self.update_window_controls
        )
        self.image_view.pixel_position_changed.connect(
            self.update_pixel_info
        )
        self.image_view.measurement_point_selected.connect(
            self.add_measurement_point
        )
        self.image_view.roi_selected.connect(
            self.update_roi_measurement
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
        self.window_center_spin.valueChanged.connect(
            self.on_window_controls_changed
        )

        # Window Width
        self.window_width_spin = QSpinBox()
        self.window_width_spin.setRange(1, 131070)
        self.window_width_spin.setValue(65536)
        self.window_width_spin.valueChanged.connect(
            self.on_window_controls_changed
        )

        window_layout = QFormLayout()
        window_layout.addRow("Window Center:", self.window_center_spin)
        window_layout.addRow("Window Width:", self.window_width_spin)

        # 오른쪽 제어 영역
        control_layout = QVBoxLayout()
        control_layout.addWidget(self.open_button)
        control_layout.addWidget(self.save_png_button)
        control_layout.addWidget(self.anonymize_button)
        control_layout.addWidget(self.reset_view_button)
        control_layout.addWidget(self.reset_window_button)
        control_layout.addWidget(self.clear_roi_button)

        control_layout.addWidget(self.zoom_label)
        control_layout.addWidget(self.window_label)
        control_layout.addWidget(self.pixel_info_label)
        control_layout.addWidget(self.distance_label)
        control_layout.addWidget(self.roi_label)

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
        main_layout.addWidget(self.image_view, 1)
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

            self.measurement_points.clear()
            self.distance_label.setText("Distance: -")
            self.image_view.clear_measurement()
            self.roi_label.setText("ROI: Ctrl + Left Drag")
            self.image_view.clear_roi()

            self.save_png_button.setEnabled(True)
            self.anonymize_button.setEnabled(True)

            self.update_metadata()
            self.set_initial_window()
            self.update_image()
            self.image_view.fit_to_view()

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

        self.image_view.set_window_values(
            self.window_center_spin.value(),
            self.window_width_spin.value(),
            set_default=True,
        )
        self.update_window_label()

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

    def update_zoom_label(self, percentage):
        """현재 Zoom 배율을 표시합니다."""
        self.zoom_label.setText(f"Zoom: {percentage}%")

    def update_pixel_info(self, x, y):
        """현재 마우스 위치의 Raw Pixel 값과 HU 값을 표시합니다."""
        if self.dataset is None or self.pixel_array is None:
            return

        raw_pixel_array = self.dataset.pixel_array

        if not (
            0 <= y < raw_pixel_array.shape[0]
            and 0 <= x < raw_pixel_array.shape[1]
        ):
            return

        raw_value = raw_pixel_array[y, x]
        hu_value = self.pixel_array[y, x]

        self.pixel_info_label.setText(
            f"X: {x}  Y: {y}  "
            f"Pixel: {raw_value}  "
            f"HU: {hu_value:.0f}"
        )

    def update_window_label(self):
        """현재 Window Center/Width를 표시합니다."""
        self.window_label.setText(
            f"WC: {self.window_center_spin.value()}  "
            f"WW: {self.window_width_spin.value()}"
        )

    def on_window_controls_changed(self, _value=None):
        """SpinBox 변경값을 ImageView와 영상에 반영합니다."""
        center = self.window_center_spin.value()
        width = self.window_width_spin.value()

        self.image_view.set_window_values(center, width)
        self.update_window_label()
        self.update_image()

    def update_window_controls(self, center, width):
        """ImageView에서 전달된 Window 값을 SpinBox에 반영합니다."""
        center = max(
            self.window_center_spin.minimum(),
            min(round(center), self.window_center_spin.maximum()),
        )
        width = max(
            self.window_width_spin.minimum(),
            min(round(width), self.window_width_spin.maximum()),
        )

        self.window_center_spin.blockSignals(True)
        self.window_width_spin.blockSignals(True)
        self.window_center_spin.setValue(center)
        self.window_width_spin.setValue(width)
        self.window_center_spin.blockSignals(False)
        self.window_width_spin.blockSignals(False)

        self.image_view.set_window_values(center, width)
        self.update_window_label()
        self.update_image()

    def update_image(self):
        """Window Center/Width를 적용하여 영상을 갱신합니다."""
        if self.pixel_array is None:
            return

        windowed = apply_window(
            pixel_array=self.pixel_array,
            window_center=self.window_center_spin.value(),
            window_width=self.window_width_spin.value(),
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
        self.image_view.set_pixmap(pixmap)

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
            pixel_array=self.pixel_array,
            window_center=self.window_center_spin.value(),
            window_width=self.window_width_spin.value(),
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


    def add_measurement_point(self, x, y):
        """두 측정 포인트 사이의 거리를 pixel 또는 mm 단위로 표시합니다."""
        if self.dataset is None:
            return

        if len(self.measurement_points) == 2:
            self.measurement_points.clear()
            self.image_view.clear_measurement()

        self.measurement_points.append((x, y))

        if len(self.measurement_points) == 1:
            self.distance_label.setText(
                f"Point 1: ({x}, {y})"
            )
            return

        (x1, y1), (x2, y2) = self.measurement_points

        self.image_view.show_measurement(
            (x1, y1),
            (x2, y2),
        )

        dx = x2 - x1
        dy = y2 - y1

        pixel_spacing = getattr(
            self.dataset,
            "PixelSpacing",
            None,
        )

        if pixel_spacing is None or len(pixel_spacing) < 2:
            distance = np.sqrt(dx ** 2 + dy ** 2)
            self.distance_label.setText(
                f"Distance: {distance:.2f} px"
            )
            return

        row_spacing = float(pixel_spacing[0])
        column_spacing = float(pixel_spacing[1])

        distance_mm = np.sqrt(
            (dx * column_spacing) ** 2
            + (dy * row_spacing) ** 2
        )

        self.distance_label.setText(
            f"Distance: {distance_mm:.2f} mm"
        )

    def update_roi_measurement(self, x1, y1, x2, y2):
        """선택한 사각형 ROI의 Mean/Min/Max HU를 표시합니다."""
        if self.pixel_array is None:
            return

        height, width = self.pixel_array.shape[:2]
        x1 = max(0, min(x1, width - 1))
        x2 = max(0, min(x2, width - 1))
        y1 = max(0, min(y1, height - 1))
        y2 = max(0, min(y2, height - 1))

        roi = self.pixel_array[y1:y2 + 1, x1:x2 + 1]

        if roi.size == 0:
            self.roi_label.setText("ROI: -")
            return

        self.roi_label.setText(
            f"ROI: {roi.shape[1]} x {roi.shape[0]} px\n"
            f"Mean: {np.mean(roi):.2f} HU\n"
            f"Min: {np.min(roi):.2f} HU\n"
            f"Max: {np.max(roi):.2f} HU"
        )

    def clear_roi_measurement(self):
        """ROI 사각형과 측정 결과를 초기화합니다."""
        self.image_view.clear_roi()
        self.roi_label.setText("ROI: Ctrl + Left Drag")


def main():
    app = QApplication(sys.argv)

    viewer = DicomViewer()
    viewer.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
