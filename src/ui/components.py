from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import pyqtSignal, Qt


class ResponsiveErrorWidget(QWidget):
    """
    Componente personalizado y adaptable para representar
    estados de error o pantallas vacías (Empty/Error States).
    """
    retry_clicked = pyqtSignal()

    def __init__(self, message: str, parent=None):
        super().__init__(parent)
        self._init_ui(message)

    def _init_ui(self, message: str):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(10)

        # Icono visual llamativo (Accesibilidad / Feedback inmediato)
        self.icon_label = QLabel("📡❌")
        self.icon_label.setStyleSheet("font-size: 48px;")
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Mensaje descriptivo del fallo
        self.msg_label = QLabel(message)
        self.msg_label.setWordWrap(True)
        self.msg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.msg_label.setStyleSheet("color: #FF0055; font-weight: bold; font-size: 15px;")

        # Botón de acción rápida para reintento manual
        self.retry_btn = QPushButton("Forzar Reintento")
        self.retry_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.retry_btn.clicked.connect(self.retry_clicked.emit)

        layout.addWidget(self.icon_label)
        layout.addWidget(self.msg_label)
        layout.addWidget(self.retry_btn)