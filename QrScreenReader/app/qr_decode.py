from __future__ import annotations

from typing import Optional

import cv2
import numpy as np
from PySide6.QtGui import QImage


def qimage_to_cv(image: QImage) -> np.ndarray:
    rgb = image.convertToFormat(QImage.Format.Format_RGB888)
    width = rgb.width()
    height = rgb.height()
    ptr = rgb.bits()
    arr = np.frombuffer(ptr, dtype=np.uint8)
    arr = arr.reshape((height, width, 3))
    return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)


def decode_qr_from_qimage(image: QImage) -> Optional[str]:
    frame = qimage_to_cv(image)
    max_dim = max(frame.shape[0], frame.shape[1])
    if max_dim > 1800:
        scale = 1800.0 / float(max_dim)
        frame = cv2.resize(frame, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)

    detector = cv2.QRCodeDetector()

    data, points, _ = detector.detectAndDecode(frame)
    if data:
        return data

    ok, decoded_info, _, _ = detector.detectAndDecodeMulti(frame)
    if ok and decoded_info:
        for item in decoded_info:
            if item:
                return item

    return None
