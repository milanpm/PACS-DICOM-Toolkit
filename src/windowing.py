import numpy as np


def apply_window(
    pixel_array: np.ndarray,
    window_center: float,
    window_width: float,
) -> np.ndarray:
    """Window Level/Width를 적용하여 8-bit 영상으로 변환합니다."""
    if window_width <= 0:
        raise ValueError("Window width must be greater than 0.")

    window_min = window_center - window_width / 2
    window_max = window_center + window_width / 2

    windowed = np.clip(pixel_array, window_min, window_max)
    windowed = (windowed - window_min) / (window_max - window_min)
    windowed = (windowed * 255).astype(np.uint8)

    return windowed
