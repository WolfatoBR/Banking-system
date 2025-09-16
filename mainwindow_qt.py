from PyQt6 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(956, 600)
        
        # --- ESTILOS CENTRALIZADOS ---
        # Definimos todos os estilos da aplicação em um único lugar.
        # Isso é mais robusto e fácil de manter do que aplicar estilos individuais.
        stylesheet = """
            /* Estilo geral da janela e groupbox */
            QMainWindow, QGroupBox {
                background-color: #1e1e1e; /* Um cinza escuro em vez de preto puro */
                color: #ffffff; /* Cor do texto padrão (branco) */
            }

            /* Estilo dos Rótulos (Labels) */
            QLabel {
                color: #cccccc; /* Cinza claro para textos normais */
                background-color: transparent; /* Fundo transparente */
            }

            /* Estilo específico para o título principal "Super Banking" */
            QLabel#label {
                font-size: 24pt;
                font-weight: bold;
                color: #55aaff; /* Azul claro */
            }
            
            /* Estilo para os títulos dos groupboxes */
            QGroupBox {
                font-size: 12pt;
                font-weight: bold;
                border: 1px solid #444444;
                border-radius: 5px;
                margin-top: 10px;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 3px;
            }

            /* Estilo dos campos de entrada de texto (CPF, Valor) */
            QLineEdit {
                background-color: #ffffff;
                color: #000000;
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 8px;
                font-size: 10pt;
            }

            /* Estilo da lista de extrato/mensagens */
            QListView {
                background-color: #2a2a2a;
                color: #cccccc;
                border: 1px solid #444444;
                border-radius: 5px;
            }

            /* Estilo dos Botões */
            QPushButton {
                background-color: #55aaff; /* Azul claro */
                color: #000000; /* Texto preto */
                border-radius: 5px;
                padding: 10px;
                font-size: 10pt;
                font-weight: bold;
                border: none;
            }

            QPushButton:hover {
                background-color: #77bbff; /* Azul um pouco mais claro ao passar o mouse */
            }
            
            QPushButton:pressed {
                background-color: #3388dd; /* Azul mais escuro ao clicar */
            }
        """
        
        # Aplicamos a folha de estilo inteira à janela principal
        MainWindow.setStyleSheet(stylesheet)
        # --- FIM DOS ESTILOS ---
        
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        self.label = QtWidgets.QLabel(parent=self.centralwidget)
        self.label.setGeometry(QtCore.QRect(0, 20, 951, 61))
        font = QtGui.QFont()
        font.setPointSize(24)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label.setObjectName("label")
        
        self.client_groupbox = QtWidgets.QGroupBox(parent=self.centralwidget)
        self.client_groupbox.setGeometry(QtCore.QRect(20, 100, 451, 101))
        self.client_groupbox.setObjectName("client_groupbox")
        
        self.cpf_input = QtWidgets.QLineEdit(parent=self.client_groupbox)
        self.cpf_input.setGeometry(QtCore.QRect(20, 40, 411, 41))
        self.cpf_input.setObjectName("cpf_input")
        
        self.operations_groupbox = QtWidgets.QGroupBox(parent=self.centralwidget)
        self.operations_groupbox.setGeometry(QtCore.QRect(20, 220, 451, 351))
        self.operations_groupbox.setObjectName("operations_groupbox")
        
        self.value_input = QtWidgets.QLineEdit(parent=self.operations_groupbox)
        self.value_input.setGeometry(QtCore.QRect(20, 40, 411, 41))
        self.value_input.setObjectName("value_input")
        
        self.deposit_button = QtWidgets.QPushButton(parent=self.operations_groupbox)
        self.deposit_button.setGeometry(QtCore.QRect(20, 100, 131, 51))
        self.deposit_button.setObjectName("deposit_button")
        
        self.withdrawn_button = QtWidgets.QPushButton(parent=self.operations_groupbox)
        self.withdrawn_button.setGeometry(QtCore.QRect(160, 100, 131, 51))
        self.withdrawn_button.setObjectName("withdrawn_button")
        
        self.statement_button = QtWidgets.QPushButton(parent=self.operations_groupbox)
        self.statement_button.setGeometry(QtCore.QRect(300, 100, 131, 51))
        self.statement_button.setObjectName("statement_button")
        
        self.management_groupbox = QtWidgets.QGroupBox(parent=self.operations_groupbox)
        self.management_groupbox.setGeometry(QtCore.QRect(20, 170, 411, 161))
        self.management_groupbox.setObjectName("management_groupbox")
        
        self.create_client_button = QtWidgets.QPushButton(parent=self.management_groupbox)
        self.create_client_button.setGeometry(QtCore.QRect(20, 40, 181, 51))
        self.create_client_button.setObjectName("create_client_button")
        
        self.create_account_button = QtWidgets.QPushButton(parent=self.management_groupbox)
        self.create_account_button.setGeometry(QtCore.QRect(210, 40, 181, 51))
        self.create_account_button.setObjectName("create_account_button")
        
        self.list_accounts_button = QtWidgets.QPushButton(parent=self.management_groupbox)
        self.list_accounts_button.setGeometry(QtCore.QRect(20, 100, 371, 51))
        self.list_accounts_button.setObjectName("list_accounts_button")
        
        self.log_groupbox = QtWidgets.QGroupBox(parent=self.centralwidget)
        self.log_groupbox.setGeometry(QtCore.QRect(490, 100, 451, 471))
        self.log_groupbox.setObjectName("log_groupbox")
        
        self.listView = QtWidgets.QListView(parent=self.log_groupbox)
        self.listView.setGeometry(QtCore.QRect(10, 30, 431, 431))
        self.listView.setObjectName("listView")
        
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Super Banking System"))
        self.label.setText(_translate("MainWindow", "Super Banking"))
        self.client_groupbox.setTitle(_translate("MainWindow", "Área do Cliente"))
        self.cpf_input.setPlaceholderText(_translate("MainWindow", "Digite o CPF do cliente (somente números)"))
        self.operations_groupbox.setTitle(_translate("MainWindow", "Operações"))
        self.value_input.setPlaceholderText(_translate("MainWindow", "Valor (R$). Ex: 1500.50"))
        self.log_groupbox.setTitle(_translate("MainWindow", "Extrato / Mensagens"))
        self.deposit_button.setText(_translate("MainWindow", "Depositar"))
        self.withdrawn_button.setText(_translate("MainWindow", "Sacar"))
        self.statement_button.setText(_translate("MainWindow", "Extrato"))
        self.management_groupbox.setTitle(_translate("MainWindow", "Gerenciamento"))
        self.create_client_button.setText(_translate("MainWindow", "Novo Usuário"))
        self.create_account_button.setText(_translate("MainWindow", "Nova Conta"))
        self.list_accounts_button.setText(_translate("MainWindow", "Listar Contas"))