from pathlib import Path

import numpy as np
import pydicom
from pydicom.dataset import Dataset


def load_dicom(file_path: str) -> tuple[Dataset, np.ndarray]:
    """DICOM 파일을 읽고 데이터셋과 픽셀 배열을 반환합니다."""
    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(f"DICOM file not found: {path}")

    dataset = pydicom.dcmread(str(path))

    if "PixelData" not in dataset:
        raise ValueError("The selected DICOM file has no pixel data.")

    pixel_array = dataset.pixel_array.astype(np.float32)

    slope = float(getattr(dataset, "RescaleSlope", 1.0))
    intercept = float(getattr(dataset, "RescaleIntercept", 0.0))
    pixel_array = pixel_array * slope + intercept

    return dataset, pixel_array


def extract_metadata(dataset: Dataset) -> dict[str, str]:
    """DICOM 데이터셋에서 주요 메타데이터를 추출합니다."""
    return {
        "Patient Name": str(dataset.get("PatientName", "N/A")),
        "Patient ID": str(dataset.get("PatientID", "N/A")),
        "Study Date": str(dataset.get("StudyDate", "N/A")),
        "Modality": str(dataset.get("Modality", "N/A")),
        "Rows": str(dataset.get("Rows", "N/A")),
        "Columns": str(dataset.get("Columns", "N/A")),
        "Window Center": str(dataset.get("WindowCenter", "N/A")),
        "Window Width": str(dataset.get("WindowWidth", "N/A")),
        "Pixel Spacing": str(dataset.get("PixelSpacing", "N/A")),
    }
