from PyQt6.QtWidgets import QDialog, QVBoxLayout, QDateEdit, QDialogButtonBox
from PyQt6.QtCore import QDate, Qt

class DateDialog(QDialog):
    """Um dialogo personalizado que usa um QDateEdit com um pop-up de calendario"""
    def __init__(self, parent=None):
        super().__init__(parent)

        # configuração da janela
        self.setWindowTitle("Selecione a Data de Nascimento")

        # criação do Widgets
        self.layout = QVBoxLayout(self)

        