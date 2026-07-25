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

    return dataset, pixel_array
