from PySide6.QtWidgets import QMessageBox


def pop_error_message_box(
    error_type: str, error_message: str, error_icon=QMessageBox.Warning
) -> None:
    """pop an error message box."""
    error_message_box = QMessageBox()
    error_message_box.setWindowTitle(error_type)
    error_message_box.setIcon(error_icon)
    error_message_box.setText(error_message)
    error_message_box.exec()


def pop_success_message_box(success_hint: str, success_message: str) -> None:
    """pop a success message box"""
    success_message_box = QMessageBox()
    success_message_box.setWindowTitle(success_hint)
    success_message_box.setText(success_message)
    success_message_box.exec()
