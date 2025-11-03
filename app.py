import sys
from datetime import datetime

from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QInputDialog
from PyQt6.QtCore import QStringListModel
from engine.mainwindow_qt import Ui_MainWindow

from sqlite3 import Error as SqliteError

from engine import database as db
from engine.individual import Individual
from engine.checkingAccount import CheckingAccount
from engine.deposit import Deposit
from engine.withdraw import Withdraw
from engine.date_dialog import DateDialog

LOG_FILE = "log_bancario.txt"

class BankingApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        db.create_project_tables()

        self.log_messages= []
        self.connect_signals()

        self.log_model = QStringListModel(self.log_messages)
        self.ui.listView.setModel(self.log_model)

        # variaveis para guardar a sessão atual
        self.current_client = None
        self.current_account = None

    def connect_signals(self):    
        self.ui.deposit_button.clicked.connect(self.deposit_func)
        self.ui.withdrawn_button.clicked.connect(self.withdraw_func)
        self.ui.statement_button.clicked.connect(self.show_statement)
        self.ui.create_client_button.clicked.connect(self.create_client)
        self.ui.create_account_button.clicked.connect(self.create_account)
        self.ui.list_accounts_button.clicked.connect(self.select_active_client_and_account)

    def log_message(self, txt):
        timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        msg = f"[{timestamp}] - INFO - {txt}"
        self.log_messages.append(msg)
        self.log_model.setStringList(self.log_messages)
        self.ui.listView.scrollToBottom()
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(msg + "\n")
        except IOError as exc:
            print(f"Erro ao escrever no log: {exc}")
    
    def get_cpf(self):
        return self.ui.cpf_input.text().strip()
    
    def get_value(self):
        try:
            return float(self.ui.value_input.text().strip())
        except ValueError:
            return None

    def create_client(self):
        cpf = self.get_cpf()
        if not cpf:
            QMessageBox.warning(self, "Entrada Inválida", "O campo CPF é obrigatório.")
            return

        name, ok = QInputDialog.getText(self, "Novo Cliente", "Nome Completo:")
        if not ok or not name.strip(): return
        
        date_dialog = DateDialog(self)
        
        if date_dialog.exec():
            birth_qdate = date_dialog.selected_date()
            birth_date_obj = birth_qdate.toPyDate()
        else:
            return

        today = datetime.now().date()
        age = today.year - birth_date_obj.year - ((today.month, today.day) < (birth_date_obj.month, birth_date_obj.day))
        
        if age < 18:
            self.log_message(f"Tentativa de cadastro de menor de idade (CPF: {cpf}, Idade: {age}).")
            QMessageBox.warning(self, "Idade Inválida", f"O cliente deve ter no mínimo 18 anos. Idade calculada: {age} anos.")
            return

        address, ok = QInputDialog.getText(self, "Novo Cliente", "Endereço:")
        if not ok or not address.strip(): return
        
        birth_date_str = birth_date_obj.strftime("%d-%m-%Y")
        
        if db.add_client(cpf, name, birth_date_str, address):
            self.log_message(f"Cliente {name} (CPF: {cpf}) criado com sucesso!")
            QMessageBox.information(self, "Sucesso", "Cliente criado com sucesso!")
            self.ui.cpf_input.clear()
        else:
            self.log_message(f"Erro: Cliente com CPF {cpf} já existe.")
            QMessageBox.warning(self, "Erro", "Já existe um cliente com este CPF.")
    
    def create_account(self):
        cpf = self.get_cpf()
        if not cpf:
            QMessageBox.warning(self, "Entrada Inválida", "O campo CPF é obrigatório para criar uma conta.")
            return

        try:
            new_account_number = db.add_account(agency="0001", balance=0, client_cpf=cpf)
            if new_account_number:
                self.log_message(f"Conta {new_account_number} criada para o cliente de CPF {cpf}.")
                QMessageBox.information(self, "Sucesso", f"Conta {new_account_number} criada com sucesso!")
                self.ui.cpf_input.clear()
            else:
                self.log_message(f"Falha ao criar conta para CPF {cpf}. Cliente não encontrado.")
                QMessageBox.critical(self, "Erro", "Cliente não encontrado.\nVerifique se o CPF está correto e o cliente já foi cadastrado.")
        except SqliteError as e:
            self.log_message(f"ERRO DE BANCO DE DADOS ao criar conta para CPF {cpf}: {e}")
            QMessageBox.critical(self, "Erro de Banco de Dados", f"Ocorreu um erro inesperado ao acessar o banco de dados.\nDetalhes: {e}")
    
    def deposit_func(self):
        if not self.current_account or self.current_client.cpf != self.get_cpf():
            QMessageBox.warning(self, "Nenhuma Conta Ativa", "Por favor, digiteum CPF e use o botão 'Listar Contas' para selecionar um cliente e uma conta primeiro.")
            return
        
        account = self.current_account
        client = self.current_client

        value = self.get_value()
        if value is None or value <= 0:
            QMessageBox.warning(self, "Valor Inválido", "Por favor, insira um valor de depósito positivo.")
            return
            
        transaction = Deposit(value)
        # O perform_transaction ainda é útil para a lógica, mas não para o histórico
        if client.perform_transaction(account, transaction):
            db.update_account_balance(account.number, account.balance)
            db.add_transaction(account.number, "Depósito", value)
            
            self.log_message(f"Depósito de R$ {value:.2f} realizado na conta {account.number}.")
            QMessageBox.information(self, "Sucesso", "Depósito realizado com sucesso!")
            self.ui.value_input.clear()
    
    def withdraw_func(self):
        if not self.current_account or self.current_client.cpf != self.get_cpf():
            QMessageBox.warning(self, "Nenhuma Conta Ativa", "Por favor, digiteum CPF e use o botão 'Listar Contas' para selecionar um cliente e uma conta primeiro.")
            return
        
        value = self.get_value()
        if value is None or value <= 0:
            QMessageBox.warning(self, "Valor Inválido", "Por favor, insira um valor de saque positivo.")
            return
        
        account = self.current_account
        client = self.current_client
            
        transaction = Withdraw(value)
        # A lógica de negócio (verificar saldo, etc.) ainda é executada aqui
        if client.perform_transaction(account, transaction):
             db.update_account_balance(account.number, account.balance)
             db.add_transaction(account.number, "Saque", value)

             self.log_message(f"Saque de R$ {value:.2f} realizado na conta {account.number}.")
             QMessageBox.information(self, "Sucesso", "Saque realizado com sucesso!")
             self.ui.value_input.clear()
        else:
            self.log_message(f"Tentativa de saque de R$ {value:.2f} na conta {account.number} falhou.")
            QMessageBox.warning(self, "Operação Falhou", "Saque não realizado. Verifique o saldo e os limites.")
    
    def show_statement(self):
        if not self.current_account or self.current_client.cpf != self.get_cpf():
            QMessageBox.warning(self, "Nenhuma Conta Ativa", "Por favor, digiteum CPF e use o botão 'Listar Contas' para selecionar um cliente e uma conta primeiro.")
            return
        
        account = self.current_account
        client = self.current_client
            
        self.log_message(f"===== Extrato da Conta: {account.number} =====")
        
        #Busca as transações do banco de dados
        transactions = db.get_transactions_by_account(account.number)

        if not transactions:
            self.log_message("Nenhuma transação encontrada para esta conta.")
        else:
            for trans in transactions:
                self.log_message(
                    f"{trans['date']} - {trans['transaction_type']}: R$ {trans['value']:.2f}"
                )
        
        # O saldo final vem do objeto já hidratado
        self.log_message(f"Saldo atual: R$ {account.balance:.2f}")
        self.log_message("=" * 40)

    def select_active_client_and_account(self):
        cpf = self.get_cpf()
        if not cpf:
            QMessageBox.warning(self, "Entrada Inválida", "Digite um CPF para carregar o cliente.")
            return
        
        client_data = db.get_client_by_cpf(cpf)
        if not client_data:
            self.log_message(f"Cliente com CPF {cpf} não encontrado!")
            self.current_client = None
            self.current_account = None
            QMessageBox.warning(self, "Erro", "Cliente não encontrado.")
            return
        
        client_obj = Individual(name=client_data['name'], birth_date=client_data['birth_date'], cpf=client_data['cpf'], address=client_data['address'])
        self.current_client = client_obj
        
        accounts_data = db.get_accounts_by_client(cpf)
        
        if not accounts_data:
            self.log_message(f"Cliente {client_obj.name} encontrado, mas não possui contas.")
            self.current_account = None
            QMessageBox.warning(self, "Cliente sem Contas", "Este cliente foi encontrado, mas ainda não possui nenhuma conta bancária.")
            return

        hydrated_accounts = []
        for acc_data in accounts_data:
            account_obj = CheckingAccount(number=acc_data['number'], client=client_obj, limit=acc_data['limit_value'], withdrawn_limit=acc_data['withdraw_limit'])
            account_obj._balance = acc_data['balance'] 
            client_obj.add_account(account_obj)
            hydrated_accounts.append(account_obj)

        # logica
        selected_account = None
        if len(hydrated_accounts) == 1:
            selected_account = hydrated_accounts[0]
            self.log_message(f"Cliente {client_obj.name} carregado. Conta única {selected_account.number} selecionada.")
        else:
            # criando uma lista de String pra seleção
            account_options = [f"Conta: {acc.number} (Saldo: R$ {acc.balance:.2f})" for acc in hydrated_accounts]

            item, ok = QInputDialog.getItem(self, "Selecionar Conta",
                                           f"Cliente {client_obj.name} possui multiplas contas.\nSelecione a conta para operar.",account_options, 0, False)
            
            if ok and item:
                selected_index = account_options.index(item)
                selected_account = hydrated_accounts[selected_index]
            else:

                # atualização feita pra manter a sessão
                self.log_message("Seleção cancelada pelo usuario.")
                return
                
        # aqui atualizamos o estado do cliente
        self.current_client = client_obj
        self.current_account = selected_account
        
        self.log_message(f"CONTA ATIVA TROCADA: Conta {self.current_account.number} (Tituar: {self.current_client.name})")
        
        QMessageBox.information(self, "Sucesso", f"Cliente {self.current_client.name} e conta {self.current_account.number} estão ativos.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BankingApp()
    window.show()
    sys.exit(app.exec())