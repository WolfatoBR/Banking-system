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

        # Usando o QDateEdite como um pop-up
        self.date_edit = QDateEdit(self, calendarPopup = True)
        self.date_edit.setDisplayFormat("dd-MM-yyyy") # formato de exibição

        # data maxima
        self.date_edit.setMaximumDate(QDate.currentDate())
        # data inicial padrao
        self.date_edit.setDate(QDate.currentDate().addYears(-18))

        # melhora a aparencia da font
        font = self.date_edit.font()
        font.setPointSize(12)
        self.date_edit.setFont(font)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)

        # conexao dos sinais
        self.buttonBox.accepted.connect(self.accepted)
        self.buttonBox.rejected.connect(self.rejected)

        # adicionando os widgets ao layout
        self.layout.addWidget(self.date_edit)
        self.layout.addWidget(self.buttonBox)
    
    def selected_date(self):
        """Retorna a data que o usuario retornou"""
        # O método para pegar a data de um QDateEdit é .date()
        return self.date_edit.date()
