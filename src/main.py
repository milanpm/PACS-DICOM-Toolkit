"""
File Name: main.py
Created Date: 2026-08-24
Modified Date: 2026-09-01
Author: Alex
Description:
    Provides the PyQt5 user interface for viewing, inspecting,
    processing, querying, and retrieving DICOM files using the
    PACS DICOM Toolkit.
"""

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
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from anonymizer import save_anonymized_dicom
from dicom_loader import extract_metadata, load_dicom
from dicom_network import (
    find_instances,
    find_series,
    find_studies,
    get_instances,
    move_instances,
    send_dicom_file,
    start_storage_scp,
    verify_connection,
)
from windowing import apply_window
from image_view import ImageView

class DicomViewer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initialize_state()
        self.setup_ui()
        self.connect_signals()


    def initialize_state(self):
        """Initialize DICOM data and measurement state."""
        self.dataset = None
        self.pixel_array = None
        self.current_file_path = None
        self.measurement_points = []
        self.storage_server = None


    def connect_signals(self):
        """Connect UI events to viewer actions."""
        self.open_button.clicked.connect(self.open_dicom)
        self.save_png_button.clicked.connect(self.save_png)
        self.anonymize_button.clicked.connect(self.save_anonymized)
        self.reset_view_button.clicked.connect(
            self.image_view.reset_view
        )
        self.reset_window_button.clicked.connect(
            self.image_view.reset_window
        )
        self.clear_roi_button.clicked.connect(
            self.clear_roi_measurement
        )
        self.metadata_search_button.clicked.connect(
            self.search_metadata
        )
        self.window_center_spin.valueChanged.connect(
            self.on_window_controls_changed
        )
        self.window_width_spin.valueChanged.connect(
            self.on_window_controls_changed
        )

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
        self.echo_button.clicked.connect(
            self.send_c_echo
        )
        self.store_button.clicked.connect(
            self.send_c_store
        )
        self.start_scp_button.clicked.connect(
            self.start_storage_server
        )
        self.stop_scp_button.clicked.connect(
            self.stop_storage_server
        )
        self.find_button.clicked.connect(
            self.send_c_find
        )
        self.find_series_button.clicked.connect(
            self.send_series_find
        )
        self.find_instances_button.clicked.connect(
            self.send_instance_find
        )
        self.move_study_button.clicked.connect(
            self.send_study_move
        )
        self.move_series_button.clicked.connect(
            self.send_series_move
        )
        self.get_study_button.clicked.connect(
            self.send_study_get
        )
        self.get_series_button.clicked.connect(
            self.send_series_get
        )


    def setup_ui(self):
        """Create and arrange viewer widgets."""
        self.setWindowTitle("PACS DICOM Toolkit")
        self.resize(900, 700)

        # DICOM 열기 버튼
        self.open_button = QPushButton("Open DICOM")

        # PNG 저장 버튼
        self.save_png_button = QPushButton("Save PNG")
        self.save_png_button.setEnabled(False)

        # 익명화 저장 버튼
        self.anonymize_button = QPushButton("Save Anonymized DICOM")
        self.anonymize_button.setEnabled(False)

        # 영상 표시 영역
        self.image_view = ImageView()
        self.image_view.setMinimumSize(512, 512)

        # View 초기화 버튼
        self.reset_view_button = QPushButton("Reset View")
        self.reset_window_button = QPushButton("Reset Window")
        self.clear_roi_button = QPushButton("Clear ROI")

        # Zoom 배율 표시
        self.zoom_label = QLabel("Zoom: 100%")
        self.window_label = QLabel("WC: -  WW: -")
        self.pixel_info_label = QLabel(
            "X: -  Y: -  Pixel: -  HU: -"
        )
        self.distance_label = QLabel("Distance: -")
        self.roi_label = QLabel("ROI: Ctrl + Left Drag")

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
        self.metadata_search_result = QTextEdit()
        self.metadata_search_result.setReadOnly(True)
        self.metadata_search_result.setMinimumHeight(120)

        # Window Center
        self.window_center_spin = QSpinBox()
        self.window_center_spin.setRange(-65535, 65535)
        self.window_center_spin.setValue(32768)

        # Window Width
        self.window_width_spin = QSpinBox()
        self.window_width_spin.setRange(1, 131070)
        self.window_width_spin.setValue(65536)

        # DICOM Network configuration
        self.local_ae_input = QLineEdit("PACS_TOOLKIT")
        self.local_ae_input.setMaxLength(16)

        self.remote_ae_input = QLineEdit("ANY-SCP")
        self.remote_ae_input.setMaxLength(16)

        self.remote_ip_input = QLineEdit("127.0.0.1")

        self.remote_port_spin = QSpinBox()
        self.remote_port_spin.setRange(1, 65535)
        self.remote_port_spin.setValue(11112)

        self.echo_button = QPushButton("Send C-ECHO")

        self.store_button = QPushButton("Send C-STORE")
        self.store_button.setEnabled(False)

        self.scp_port_spin = QSpinBox()
        self.scp_port_spin.setRange(1, 65535)
        self.scp_port_spin.setValue(11113)

        self.start_scp_button = QPushButton("Start Storage SCP")
        self.stop_scp_button = QPushButton("Stop Storage SCP")
        self.stop_scp_button.setEnabled(False)

        self.network_status_label = QLabel("Network: Not tested")

        self.find_patient_id_input = QLineEdit()
        self.find_patient_id_input.setPlaceholderText("Patient ID")

        self.find_patient_name_input = QLineEdit()
        self.find_patient_name_input.setPlaceholderText("Patient Name")

        self.find_study_date_input = QLineEdit()
        self.find_study_date_input.setPlaceholderText("YYYYMMDD")

        self.find_button = QPushButton("Search Studies (C-FIND)")
        self.move_study_button = QPushButton(
            "Retrieve Study (C-MOVE)"
        )
        self.get_study_button = QPushButton(
            "Retrieve Study (C-GET)"
        )
        self.find_study_uid_input = QLineEdit()
        self.find_study_uid_input.setPlaceholderText(
            "Study Instance UID"
        )

        self.find_series_button = QPushButton(
            "Search Series (C-FIND)"
        )
        self.move_series_button = QPushButton(
            "Retrieve Series (C-MOVE)"
        )
        self.move_series_button = QPushButton(
            "Retrieve Series (C-MOVE)"
        )
        self.get_series_button = QPushButton(
            "Retrieve Series (C-GET)"
        )
        self.find_series_uid_input = QLineEdit()
        self.find_series_uid_input.setPlaceholderText(
            "Series Instance UID"
        )

        self.find_instances_button = QPushButton(
            "Search Instances (C-FIND)"
        )

        self.find_result = QTextEdit()
        self.find_result.setReadOnly(True)
        self.find_result.setMinimumHeight(180)

        network_layout = QFormLayout()
        network_layout.addRow(
            "Local AE Title:",
            self.local_ae_input,
        )
        network_layout.addRow(
            "Remote AE Title:",
            self.remote_ae_input,
        )
        network_layout.addRow(
            "Remote IP:",
            self.remote_ip_input,
        )
        network_layout.addRow(
            "Remote Port:",
            self.remote_port_spin,
        )
        network_layout.addRow(self.echo_button)
        network_layout.addRow(self.store_button)
        network_layout.addRow(
            "Storage SCP Port:",
            self.scp_port_spin,
        )
        network_layout.addRow(self.start_scp_button)
        network_layout.addRow(self.stop_scp_button)
        network_layout.addRow(self.network_status_label)

        network_layout.addRow(QLabel("Study Query"))
        network_layout.addRow(
            "Patient ID:",
            self.find_patient_id_input,
        )
        network_layout.addRow(
            "Patient Name:",
            self.find_patient_name_input,
        )
        network_layout.addRow(
            "Study Date:",
            self.find_study_date_input,
        )
        network_layout.addRow(self.find_button)

        network_layout.addRow(QLabel("Series Query"))
        network_layout.addRow(
            "Study Instance UID:",
            self.find_study_uid_input,
        )
        network_layout.addRow(self.move_study_button)
        network_layout.addRow(self.get_study_button)
        network_layout.addRow(self.find_series_button)

        network_layout.addRow(QLabel("Instance Query"))
        network_layout.addRow(
            "Series Instance UID:",
            self.find_series_uid_input,
        )
        network_layout.addRow(self.move_series_button)
        network_layout.addRow(self.get_series_button)
        network_layout.addRow(self.find_instances_button)

        network_layout.addRow(QLabel("Query Results"))
        network_layout.addRow(self.find_result)

        window_layout = QFormLayout()
        window_layout.addRow("Window Center:", self.window_center_spin)
        window_layout.addRow("Window Width:", self.window_width_spin)

        # 오른쪽 제어 영역
        # Viewer tab
        viewer_tab = QWidget()
        viewer_layout = QVBoxLayout()

        viewer_layout.addWidget(self.open_button)
        viewer_layout.addWidget(self.save_png_button)
        viewer_layout.addWidget(self.anonymize_button)
        viewer_layout.addWidget(self.reset_view_button)
        viewer_layout.addWidget(self.reset_window_button)
        viewer_layout.addWidget(self.clear_roi_button)

        viewer_layout.addSpacing(10)
        viewer_layout.addWidget(self.zoom_label)
        viewer_layout.addWidget(self.window_label)
        viewer_layout.addWidget(self.pixel_info_label)
        viewer_layout.addWidget(self.distance_label)
        viewer_layout.addWidget(self.roi_label)

        viewer_layout.addSpacing(20)
        viewer_layout.addLayout(window_layout)
        viewer_layout.addStretch()

        viewer_tab.setLayout(viewer_layout)


        # Metadata tab
        metadata_tab = QWidget()
        metadata_tab_layout = QVBoxLayout()

        metadata_tab_layout.addLayout(metadata_layout)
        metadata_tab_layout.addSpacing(20)
        metadata_tab_layout.addWidget(QLabel("Metadata Search"))

        search_layout = QHBoxLayout()
        search_layout.addWidget(self.metadata_search_input)
        search_layout.addWidget(self.metadata_search_button)

        metadata_tab_layout.addLayout(search_layout)
        metadata_tab_layout.addWidget(self.metadata_search_result)
        metadata_tab_layout.addStretch()

        metadata_tab.setLayout(metadata_tab_layout)


        # Network tab
        network_tab = QWidget()
        network_tab_layout = QVBoxLayout()

        network_tab_layout.addLayout(network_layout)
        network_tab_layout.addStretch()

        network_tab.setLayout(network_tab_layout)


        # Right-side tabs
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(viewer_tab, "Viewer")
        self.tab_widget.addTab(metadata_tab, "Metadata")
        self.tab_widget.addTab(network_tab, "Network")
        self.tab_widget.setMinimumWidth(320)

        # 전체 화면 구성
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.image_view, 1)
        main_layout.addWidget(self.tab_widget)

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

            self.clear_measurements()

            self.save_png_button.setEnabled(True)
            self.anonymize_button.setEnabled(True)
            self.store_button.setEnabled(True)

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

    def clear_measurements(self):
        """Clear distance and ROI measurement state."""
        self.measurement_points.clear()
        self.image_view.clear_measurement()
        self.distance_label.setText("Distance: -")
        self.clear_roi_measurement()

    def send_c_echo(self):
        """Send a C-ECHO request using the current network settings."""
        self.echo_button.setEnabled(False)
        self.network_status_label.setText("Network: Connecting...")

        QApplication.processEvents()

        success, message = verify_connection(
            self.local_ae_input.text(),
            self.remote_ae_input.text(),
            self.remote_ip_input.text(),
            self.remote_port_spin.value(),
        )

        if success:
            self.network_status_label.setStyleSheet(
                "color: green;"
            )
        else:
            self.network_status_label.setStyleSheet(
                "color: red;"
            )

        self.network_status_label.setText(
            f"Network: {message}"
        )
        self.echo_button.setEnabled(True)

    def send_c_store(self):
        """Send the currently loaded DICOM file using C-STORE."""
        if not self.current_file_path:
            QMessageBox.warning(
                self,
                "C-STORE",
                "Please open a DICOM file first.",
            )
            return

        self.network_status_label.setStyleSheet("")
        self.network_status_label.setText(
            "Network: Sending DICOM..."
        )
        QApplication.processEvents()

        success, message = send_dicom_file(
            self.current_file_path,
            self.local_ae_input.text(),
            self.remote_ae_input.text(),
            self.remote_ip_input.text(),
            self.remote_port_spin.value(),
        )

        if success:
            self.network_status_label.setStyleSheet(
                "color: green;"
            )
        else:
            self.network_status_label.setStyleSheet(
                "color: red;"
            )

        self.network_status_label.setText(
            f"Network: {message}"
        )

    def start_storage_server(self):
        """Start the local DICOM Storage SCP."""
        if self.storage_server is not None:
            return

        try:
            local_ae_title = self.local_ae_input.text()
            local_port = self.scp_port_spin.value()

            storage_dir = Path.cwd() / "received"

            self.storage_server = start_storage_scp(
                local_ae_title=local_ae_title,
                local_ip="0.0.0.0",
                local_port=local_port,
                storage_dir=storage_dir,
            )

            self.start_scp_button.setEnabled(False)
            self.stop_scp_button.setEnabled(True)
            self.scp_port_spin.setEnabled(False)

            self.network_status_label.setText(
                f"Storage SCP running on port {local_port}"
            )
            self.network_status_label.setStyleSheet(
                "color: green;"
            )

        except Exception as error:
            self.storage_server = None

            QMessageBox.critical(
                self,
                "Storage SCP Error",
                str(error),
            )

            self.network_status_label.setText(
                f"Storage SCP failed: {error}"
            )
            self.network_status_label.setStyleSheet(
                "color: red;"
            )


    def stop_storage_server(self):
        """Stop the local DICOM Storage SCP."""
        if self.storage_server is None:
            return

        try:
            self.storage_server.shutdown()
            self.storage_server.server_close()

        finally:
            self.storage_server = None

            self.start_scp_button.setEnabled(True)
            self.stop_scp_button.setEnabled(False)
            self.scp_port_spin.setEnabled(True)

            self.network_status_label.setText(
                "Storage SCP stopped"
            )
            self.network_status_label.setStyleSheet(
                "color: gray;"
            )

    def closeEvent(self, event):
        """Stop the Storage SCP before closing the application."""
        if self.storage_server is not None:
            self.storage_server.shutdown()
            self.storage_server.server_close()
            self.storage_server = None

        event.accept()

    def send_c_find(self):
        """Search studies from the remote PACS using C-FIND."""
        self.find_study_uid_input.clear()
        self.find_series_uid_input.clear()
        success, results, message = find_studies(
            local_ae_title=self.local_ae_input.text(),
            remote_ae_title=self.remote_ae_input.text(),
            remote_ip=self.remote_ip_input.text(),
            remote_port=self.remote_port_spin.value(),
            patient_id=self.find_patient_id_input.text(),
            patient_name=self.find_patient_name_input.text(),
            study_date=self.find_study_date_input.text(),
        )

        self.network_status_label.setText(message)

        if not success:
            self.find_result.setText(message)
            return

        if not results:
            self.find_result.setText(
                "No matching studies found."
            )
            return

        lines = []

        for index, dataset in enumerate(results, start=1):
            lines.append(
                f"Study {index}\n"
                f"Patient ID: "
                f"{getattr(dataset, 'PatientID', '')}\n"
                f"Patient Name: "
                f"{getattr(dataset, 'PatientName', '')}\n"
                f"Study Date: "
                f"{getattr(dataset, 'StudyDate', '')}\n"
                f"Study Description: "
                f"{getattr(dataset, 'StudyDescription', '')}\n"
                f"Accession Number: "
                f"{getattr(dataset, 'AccessionNumber', '')}\n"
                f"Modalities: "
                f"{getattr(dataset, 'ModalitiesInStudy', '')}\n"
                f"Study Instance UID: "
                f"{getattr(dataset, 'StudyInstanceUID', '')}"
            )

        if len(results) == 1:
            study_instance_uid = str(
                getattr(
                    results[0],
                    "StudyInstanceUID",
                    "",
                )
            ).strip()

            self.find_study_uid_input.setText(
                study_instance_uid
            )

        self.find_result.setText(
            "\n\n".join(lines)
        )

    def send_series_find(self):
        """Search series in the selected study using C-FIND."""
        self.find_series_uid_input.clear()

        success, results, message = find_series(
            local_ae_title=self.local_ae_input.text(),
            remote_ae_title=self.remote_ae_input.text(),
            remote_ip=self.remote_ip_input.text(),
            remote_port=self.remote_port_spin.value(),
            study_instance_uid=(
                self.find_study_uid_input.text()
            ),
        )

        self.network_status_label.setText(message)

        if not success:
            self.find_result.setText(message)
            return

        if not results:
            self.find_result.setText(
                "No matching series found."
            )
            return

        lines = []

        for index, dataset in enumerate(results, start=1):
            lines.append(
                f"Series {index}\n"
                f"Series Number: "
                f"{getattr(dataset, 'SeriesNumber', '')}\n"
                f"Description: "
                f"{getattr(dataset, 'SeriesDescription', '')}\n"
                f"Modality: "
                f"{getattr(dataset, 'Modality', '')}\n"
                f"Instances: "
                f"{getattr(dataset, 'NumberOfSeriesRelatedInstances', '')}\n"
                f"Series Instance UID: "
                f"{getattr(dataset, 'SeriesInstanceUID', '')}"
            )

        if len(results) == 1:
            series_instance_uid = str(
                getattr(
                    results[0],
                    "SeriesInstanceUID",
                    "",
                )
            ).strip()

            self.find_series_uid_input.setText(
                series_instance_uid
            )

        self.find_result.setText(
            "\n\n".join(lines)
        )


    def send_instance_find(self):
        """Search instances in the selected series using C-FIND."""
        success, results, message = find_instances(
            local_ae_title=self.local_ae_input.text(),
            remote_ae_title=self.remote_ae_input.text(),
            remote_ip=self.remote_ip_input.text(),
            remote_port=self.remote_port_spin.value(),
            study_instance_uid=(
                self.find_study_uid_input.text()
            ),
            series_instance_uid=(
                self.find_series_uid_input.text()
            ),
        )

        self.network_status_label.setText(message)

        if not success:
            self.find_result.setText(message)
            return

        if not results:
            self.find_result.setText(
                "No matching instances found."
            )
            return

        lines = []

        for index, dataset in enumerate(results, start=1):
            lines.append(
                f"Instance {index}\n"
                f"Instance Number: "
                f"{getattr(dataset, 'InstanceNumber', '')}\n"
                f"SOP Class UID: "
                f"{getattr(dataset, 'SOPClassUID', '')}\n"
                f"SOP Instance UID: "
                f"{getattr(dataset, 'SOPInstanceUID', '')}"
            )

        self.find_result.setText(
            "\n\n".join(lines)
        )


    def send_study_move(self):
        """Retrieve all instances in the selected study."""
        self.send_c_move("STUDY")


    def send_series_move(self):
        """Retrieve all instances in the selected series."""
        self.send_c_move("SERIES")


    def send_c_move(self, query_level):
        """Request DICOM retrieval using C-MOVE."""
        if self.storage_server is None:
            message = (
                "Start the local Storage SCP before C-MOVE."
            )
            self.network_status_label.setText(message)
            QMessageBox.warning(
                self,
                "C-MOVE Error",
                message,
            )
            return

        success, counts, message = move_instances(
            local_ae_title=self.local_ae_input.text(),
            remote_ae_title=self.remote_ae_input.text(),
            remote_ip=self.remote_ip_input.text(),
            remote_port=self.remote_port_spin.value(),
            move_destination_ae_title=(
                self.local_ae_input.text()
            ),
            query_level=query_level,
            study_instance_uid=(
                self.find_study_uid_input.text()
            ),
            series_instance_uid=(
                self.find_series_uid_input.text()
            ),
        )

        self.network_status_label.setText(message)

        result_text = (
            f"{message}\n\n"
            f"Query Retrieve Level: {query_level}\n"
            f"Completed: {counts.get('completed', 0)}\n"
            f"Failed: {counts.get('failed', 0)}\n"
            f"Warnings: {counts.get('warning', 0)}\n"
            f"Remaining: {counts.get('remaining', 0)}\n"
            f"Storage Directory: received/"
        )

        self.find_result.setText(result_text)

        if not success:
            QMessageBox.warning(
                self,
                "C-MOVE Error",
                message,
            )


    def send_study_get(self):
        """Retrieve all instances in the selected study using C-GET."""
        self.send_c_get("STUDY")


    def send_series_get(self):
        """Retrieve all instances in the selected series using C-GET."""
        self.send_c_get("SERIES")


    def send_c_get(self, query_level):
        """Request DICOM retrieval using C-GET."""
        storage_dir = Path.cwd() / "received"

        success, counts, message = get_instances(
            local_ae_title=self.local_ae_input.text(),
            remote_ae_title=self.remote_ae_input.text(),
            remote_ip=self.remote_ip_input.text(),
            remote_port=self.remote_port_spin.value(),
            query_level=query_level,
            study_instance_uid=(
                self.find_study_uid_input.text()
            ),
            series_instance_uid=(
                self.find_series_uid_input.text()
            ),
            storage_dir=storage_dir,
        )

        self.network_status_label.setText(message)

        result_text = (
            f"{message}\n\n"
            f"Query Retrieve Level: {query_level}\n"
            f"Completed: {counts.get('completed', 0)}\n"
            f"Failed: {counts.get('failed', 0)}\n"
            f"Warnings: {counts.get('warning', 0)}\n"
            f"Remaining: {counts.get('remaining', 0)}\n"
            f"Storage Directory: received/\n"
            f"Association: Same association as C-GET"
        )

        self.find_result.setText(result_text)

        if not success:
            QMessageBox.warning(
                self,
                "C-GET Error",
                message,
            )


def main():
    app = QApplication(sys.argv)

    viewer = DicomViewer()
    viewer.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
