import sys
from datetime import datetime

from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QInputDialog
from PyQt6.QtCore import QStringListModel
from mainwindow_qt import Ui_MainWindow

import database as db

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

        db.create_project_tables()

        self.log_messages= []
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
        """Adiciona uma mensagem ao log da UI e ao arquivo de log."""
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
    
    def _get_hydrated_objects(self, cpf):
        """
        Busca dados no BD e os "hidrata", criando instancias das classes
        Individual e CheckingAccount para que possamos usar a lógica de négocio.
        vai retornar (client_obj, account_obj) ou (None, None).
        """
        client_data = db.get_client_by_cpf(cpf)
        if not client_data:
            self.log_message(f"Cliente com CPF {cpf} não encontrado!")
            return None, None
        
        client_obj = Individual(
            name= client_data['name'],
            birth_date= client_data['birth_date'],
            cpf= client_data['cpf'],
            address= client_data['address']
        )

        # busca a primeira conta do client
        accounts_data = db.get_accounts_by_client(cpf)
        if not accounts_data:
            self.log_message(f"Este cliente não possui uma conta cadastrada!")
            return client_obj, None
        
        # usa a primeira conta encontradsa
        account_data = accounts_data[0]

        account_obj = CheckingAccount(
            number= account_data['number'],
            client= client_obj,
            limit= account_data['limit_value'],
            withdrawn_limit= account_data['withdraw_limit']
        )
        #FIXME deixar definido o saldo do objeto com o valor que esta no BD
        account_obj._balance = account_data['balance']

        client_obj.add_account(account_obj)
        return client_obj, account_obj
    
    def create_client(self):
        cpf = self.get_cpf()
        if not cpf:
            self.log_message("É obrigatorio um Cpf para criar um cliente.")
            return
        
        name, ok = QInputDialog.getText(self, "Novo Cliente", "Nome Completo:")
        if not ok or not name.strip() :
            return

        birth_date, ok2 = QInputDialog.getText(self, "Novo Client", "Data de Nascimento (dd-mm-aaaa):")
        if not ok2 or not birth_date.strip(): 
            return

        address, ok3 = QInputDialog.getText(self, "Novo Cliente", "Endereço:")
        if not ok3 or not address.strip(): 
            return
        
        success = db.add_client(cpf, name, birth_date, address)

        if success:
            self.log_message(f"Cliente {name} (CPF: {cpf}) criado com sucesso!")
            QMessageBox.information(self, "Sucesso", "Cliente criado com sucesso!")
        else:
            self.log_message(f"Erro: Cliente com CPF {cpf} já cadastrado no sistema.")
            QMessageBox.warning(self, "Erro", "Já existe um cliente com este CPF.")
    
    def create_account(self):
        cpf = self.get_cpf()
        if not cpf:
            self.log_message("CPF do titular é obrigatorio para ciração de conta.")
            return
        
        # a função do BD ja verifica se o cliente existe
        new_account_number = db.add_account(agency="0001", balance=0, client_cpf= cpf)

        if new_account_number:
            self.log_message(f"Conta número {new_account_number} criada para o cliente de CPF {cpf}.")
            QMessageBox.information(self, "Sucesso", f"Conta {new_account_number} criada com sucesso.")
        else:
            self.log_message(f"Não foi possivel criar a conta. Verifique se o cliente com CPF {cpf} existe.")
            QMessageBox.warning(self, "Erro", "Não foi possível criar a conta.\nVerifique se o cliente com este CPF já está cadastrado.")
    
    def deposit_func(self):
        cpf = self.get_cpf()
        value = self.get_value()

        if value is None or value <=0:
            self.log_message("Valor do deposito invalido.")
            QMessageBox.warning(self, "Valor Invalido", "Insira um valor de deposito valido.")
            return
        
        client, account = self._get_hydrated_objects(cpf)
        if not account:
            return
        
        transaction = Deposit(value)
        client.perform_transaction(account, transaction)

        db.update_account_balance(account.number, account.balance)

        self.log_message(f"Depósito de R$ {value:.2f} realizado na conta {account.number}.")
        QMessageBox.information(self, "Sucesso", "Deposito realizado com suceesso.")
    
    def withdraw_func(self):
        cpf = self.get_cpf()
        value = self.get_value()

        if value is None or value <= 0:
            self.log_message("Valor de saque inválido.")
            QMessageBox.warning(self, "Valor Inválido", "Por favor, insira um valor de saque positivo.")
            return

        client, account = self._get_hydrated_objects(cpf)
        if not account:
            return
            
        transaction = Withdraw(value)
        
        client.perform_transaction(account, transaction)
        
        db.update_account_balance(account.number, account.balance)

        # A mensagem de sucesso/falha já é (ou deveria ser) impressa pelos métodos de negócio
        self.log_message(f"Tentativa de saque de R$ {value:.2f} na conta {account.number}.")
        QMessageBox.information(self, "Sucesso", f"Saque no valor de R$ ({value:.2f}) realizado com sucesso.")
    
    def show_statement(self):
        cpf =self.get_cpf()
        client, account = self._get_hydrated_objects(cpf)
        if not account:
            return
        
        # FIXME melhoria futura -> salvar o historico de transações no BD
        self.log_message(f"==== Extrato da Conta: {account.number} ====")

        # Temporariamente, vamos adicionar uma transação "falsa" para popular o histórico
        # já que ele não está sendo salvo no banco.
        account.deposit(0) # Isso adiciona o saldo atual ao histórico

        statement_has_transactions = False
        for transaction in account.history.generate_report():
            statement_has_transactions = True
            self.log_message(f"{transaction['date']} - {transaction['type']}: R$ {transaction['value']:.2f}")

        if not statement_has_transactions:
            self.log_message("Nenhuma transação registrada nesta sessão.")
        
        self.log_message(f"Saldo final: R$ {account.balance:.2f}")
        self.log_message("=" * 30)

    def list_accounts(self):
        all_clients_data = db.get_all_clients()
        if not all_clients_data:
            self.log_message("Nenhum cliente encontrado no sistema.")
            return
        
        self.log_message("===== Lista de contas Cadastradas =====")
        accounts_found = False
        for client_data in all_clients_data:
            accounts_for_client = db.get_accounts_by_client(client_data['cpf'])
            for account_data in accounts_for_client:
                accounts_found = True
                self.log_message(
                    f"Ag: {account_data['agency']}"
                    f"Conta: {account_data['number']} | "
                    f"Titular: {client_data['name']} | "
                    f"Saldo: R$ {account_data['balance']:.2f}"
                )
        
        if not accounts_found:
            self.log_message("Nenhuma conta encontrada no sistema.")

        self.log_message("=" * 40)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BankingApp()
    window.show()
    sys.exit(app.exec())