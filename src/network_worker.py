"""
File Name: network_worker.py
Created Date: 2026-09-04
Author: Alex
Description:
    Runs blocking DICOM network operations in a background
    QThread and reports progress, results, and errors using
    Qt signals.
"""

from PyQt5.QtCore import QThread, pyqtSignal


class NetworkWorker(QThread):
    """Run one DICOM network operation in a worker thread."""

    progress = pyqtSignal(str)
    result = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(
        self,
        operation_name,
        operation,
        *args,
        enable_progress=False,
        **kwargs,
    ):
        super().__init__()

        self.operation_name = operation_name
        self.operation = operation
        self.args = args
        self.kwargs = kwargs
        self.enable_progress = enable_progress

    def run(self):
        """Execute the network operation outside the GUI thread."""
        try:
            self.progress.emit(
                f"{self.operation_name}: Working..."
            )

            operation_kwargs = dict(self.kwargs)

            if self.enable_progress:
                operation_kwargs["progress_callback"] = (
                    self.progress.emit
                )

            operation_result = self.operation(
                *self.args,
                **operation_kwargs,
            )

            self.result.emit(operation_result)

        except Exception as error:
            self.error.emit(
                f"{self.operation_name} error: {error}"
            )
