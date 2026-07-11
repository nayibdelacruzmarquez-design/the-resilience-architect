# Hojas de estilo para simular un dashboard moderno de alta fidelidad
DARK_STYLE = """
QMainWindow {
    background-color: #121212;
}
QWidget {
    color: #E0E0E0;
    font-family: 'Segoe UI', sans-serif;
    font-size: 14px;
}
QPushButton {
    background-color: #1F1F1F;
    border: 1px solid #333333;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #2D2D2D;
    border-color: #00ADB5;
}
QPushButton:pressed {
    background-color: #00ADB5;
    color: #121212;
}
QLabel#status_label {
    font-weight: bold;
    padding: 4px;
    border-radius: 4px;
}
QFrame#card {
    background-color: #1E1E1E;
    border-radius: 8px;
    border: 1px solid #2D2D2D;
}
"""

LIGHT_STYLE = """
QMainWindow { background-color: #F5F5F7; }
QWidget { color: #1C1C1E; font-family: 'Segoe UI', sans-serif; font-size: 14px; }
QPushButton { background-color: #FFFFFF; border: 1px solid #D1D1D6; border-radius: 6px; padding: 8px 16px; }
QPushButton:hover { background-color: #E5E5EA; }
QFrame#card { background-color: #FFFFFF; border-radius: 8px; border: 1px solid #E5E5EA; }
"""