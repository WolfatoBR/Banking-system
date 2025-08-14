import sys
from datetime import datetime

from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QInputDialog
from PyQt6.QtCore import QStringListModel
from mainwindow_qt import Ui_MainWindow

from individual import Individual
from checkingAccount import CheckingAccount
from deposit import Deposit
from withdraw import Withdraw
from accountsIteractor import AccountsIteractor

LOG_FILE = "log_bancario.txt"

class BankingApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.log_messages= []
        self.clients_dict = {}
        self.accounts = []
        # self._setup_initial_data()
        self.connect_signals()

        self.log_model = QStringListModel(self.log_messages)
        self.ui.listView.setModel(self.log_model)

    def connect_signals(self):    
        self.ui.deposit_button.clicked.connect(self.deposit_func)
        self.ui.withdrawn_button.clicked.connect(self.withdraw_func)
        self.ui.statement_button.clicked.connect(self.show_statement)
        self.ui.create_client_button.clicked.connect(self.create_client)
        self.ui.create_account_button.clicked.connect(self.create_account)
        self.ui.list_accounts_button.clicked.connect(self.list_accounts)

    def log_message(self, txt):
        timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        msg = f"[{timestamp}] - INFO - {txt}"
        self.log_messages.append(msg)
        self.log_model.setStringList(self.log_messages) #atualiza a view
        self.ui.listView.scrollToBottom() #aqui vai rolar para baixo
        
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
    
    def filter_client(self, cpf):
        # filtra e retorna um client pelo CPF
        return self.clients_dict.get(cpf)
    
    def get_client_account(self, client):
        if not client.accounts:
            self.log_message("Cliente não possui conta cadastrada")
            return None
        ## aqui precisaria de outra tela...
        return client.accounts[0]
    
    def deposit_func(self):
        cpf = self.get_cpf()
        client = self.filter_client(cpf)

        if not client:
            self.log_message("Cliente não encontrado !!!")
            return
        
        value = self.get_value()
        if value is None or value <= 0:
            self.log_message("Valor de depósito invalido.")
            return
        
        account = self.get_client_account(client)
        if not account:
            return
        
        transaction = Deposit(value)
        client.perform_transaction(account, transaction)
        self.log_message(f"Deposito de R$ {value:.2f} realizado para o CPF {cpf}")
    
    def withdraw_func(self):
        cpf = self.get_cpf()
        client = self.filter_client(cpf)
        account = self.get_client_account(client)

        if not client:
            self.log_message("Cliente não encontrado!!!")
            return
        
        value = self.get_value()
        if value is None or value <= 0 or value >= account.balance:
            self.log_message("Valor de saque invalido!!!")
            return
        
        if not account:
            return
        
        transaction = Withdraw(value)
        client.perform_transaction(account, transaction)
        self.log_message(f"Saque de R$ {value:.2f} realizado com sucesso.")
    
    def show_statement(self):
        cpf = self.get_cpf()
        client = self.filter_client(cpf)

        if not client:
            self.log_message("Cliente não encontrado!!!")
            return
        
        account = self.get_client_account(client)
        if not account:
            return
        
        have_transactions = False
        self.log_message("===== Extrato =====")
        for transaction in account.history.generate_report(type_transaction=None):
            have_transactions = True
            self.log_message(f"{transaction['type']}: R$ {transaction['value']:.2f}")
        
        if not have_transactions:
            self.log_message(f"Nenhuma transação encontrada.")
        
        self.log_message(f"Saldo atual: R$ {account.balance:.2f}")
        self.log_message(f"====================")
    
    def create_client(self):
        cpf = self.get_cpf()
        if self.filter_client(cpf):
            self.log_message("Já existe cliente com esse CPF!!")
            return
        
        name, ob1 = QInputDialog.getText(self, "Novo Cliente", "Nome Completo: ")
        if not ob1 or not name.strip():
            return
        
        birth_date, ob2 = QInputDialog.getText(self, "Novo Cliente", "Data de Nascimento (dd-mm-aaaa):")
        if not ob2 or not birth_date.strip():
            return
        
        address, ob3 = QInputDialog.getText(self, "Novo Cliente", "Endereço:")
        if not ob3 or not address.strip():
            return
        
        client = Individual(name=name, birth_date=birth_date, cpf=cpf, address=address)
        self.clients_dict[cpf] = client
        self.log_message(f"Cliente {name} criado com sucesso!")

    def create_account(self):
        cpf = self.get_cpf()
        client = self.filter_client(cpf)

        if not client:
            self.log_message("Cliente não encontrado para criação de conta")
            return

        account_number = len(self.accounts) +1
        account = CheckingAccount.new_account(client=client, number=account_number)
        self.accounts.append(account)
        client.accounts.append(account)
        self.log_message(f"Conta {account_number} criada para CPF {cpf}")

    def list_accounts(self):
        if not self.accounts:
            self.log_message("Nenhuma conta encontrada.")
            return
        
        self.log_message("===== Lista de contas =====")
        for account in AccountsIteractor(self.accounts):
            self.log_message(str(account))
        self.log_message("===========================")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BankingApp()
    window.show()
    sys.exit(app.exec())