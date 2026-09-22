"""
File Name: network_worker.py
Created Date: 2026-09-04
Modified Date: 2026-09-22
Author: Alex
Description:
    Runs blocking DICOM network operations in a background
    QThread and reports progress, results, cancellation, and
    errors using Qt signals.
"""

from threading import Event

from PyQt5.QtCore import QThread, pyqtSignal


class NetworkWorker(QThread):
    """Run one DICOM network operation in a worker thread."""

    progress = pyqtSignal(str)
    result = pyqtSignal(object)
    cancelled = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(
        self,
        operation_name,
        operation,
        *args,
        enable_progress=False,
        enable_cancellation=False,
        **kwargs,
    ):
        super().__init__()

        self.operation_name = operation_name
        self.operation = operation
        self.args = args
        self.kwargs = kwargs
        self.enable_progress = enable_progress
        self.enable_cancellation = enable_cancellation
        self._cancel_event = Event()

    def request_cancel(self):
        """Request cooperative cancellation of the operation."""
        if self._cancel_event.is_set():
            return

        self._cancel_event.set()
        self.progress.emit(
            f"{self.operation_name}: Cancellation requested..."
        )

    def is_cancel_requested(self):
        """Return whether cancellation has been requested."""
        return self._cancel_event.is_set()

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

            if self.enable_cancellation:
                operation_kwargs["cancel_callback"] = (
                    self.is_cancel_requested
                )

            operation_result = self.operation(
                *self.args,
                **operation_kwargs,
            )

            if self.is_cancel_requested():
                self.cancelled.emit(
                    f"{self.operation_name} cancelled"
                )
                return

            self.result.emit(operation_result)

        except Exception as error:
            if self.is_cancel_requested():
                self.cancelled.emit(
                    f"{self.operation_name} cancelled"
                )
                return

            self.error.emit(
                f"{self.operation_name} error: {error}"
            )
