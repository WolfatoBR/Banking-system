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
        
        name, _ = QInputDialog.getText(self, "Novo Cliente", "Nome Completo:")
        if not name.strip() :
            return

        birth_date, _ = QInputDialog.getText(self, "Novo Client", "Data de Nascimento (dd-mm-aaaa):")
        if not birth_date.strip(): 
            return
        
        # converção pra data
        try:
            birth_date_obj = datetime.strptime(birth_date, "%d-%m-%Y").date()

        except ValueError as e:
            self.log_message(f"Formato de data invalido: {birth_date}. Erro: {e}")
            QMessageBox.warning(self, "Formato invalido", "A data de nascimento deve estar no formato dd-mm-aaaa .")
            return
        except Exception as e:
            self.log_message(f"Erro inesperado ao processar data: {e}.")
            QMessageBox.warning(self, "Erro Inesperado", f"Erro ao processar data.\nDetalhes: {e}")
            return
        
        # obter data atual
        try:
            today = datetime.now().date()
        except Exception as e:
            self.log_message(f"Erro ao obter data atual: {e}")
            QMessageBox.warning(self, "Erro de sistema", f"Não foi possivel obter a data atual.\nDetalhes: {e}")
            return
        
        # calculo de idade
        try:
            age = today.year - birth_date_obj.year
            birth_pending = (today.day, today.month) < (birth_date_obj.day, birth_date_obj.month)

            if birth_pending:
                age = age - 1

            if age < 18:
                self.log_message(f"Tentativa de cadastro de menor de idade (CPF: {cpf}, Idade: {age}).")
                QMessageBox.warning(self, "Idade Invalida", f"O cliente deve ter no mínimo 18 anos. Idade calculada: {age} anos.")
                return
            
        except Exception as e:
            self.log_message(f"Erro ao calcular idade: {e}")
            QMessageBox.warning(self, "Erro de calculo", f"Não foi possivel calcular a idade.\nDetalhes: {e}")
            return

        address, _ = QInputDialog.getText(self, "Novo Cliente", "Endereço:")
        if not address.strip(): 
            return
        try:
            success = db.add_client(cpf, name, birth_date, address)

            if success:
                self.log_message(f"Cliente {name} (CPF: {cpf}) criado com sucesso!")
                QMessageBox.information(self, "Sucesso", "Cliente criado com sucesso!")
            else:
                self.log_message(f"Erro: Cliente com CPF {cpf} já cadastrado no sistema.")
                QMessageBox.warning(self, "Erro", "Já existe um cliente com este CPF.")
        except SqliteError as e:
            self.log_message(f"Erro de banco de dados ao criar cliente (CPF: {cpf}): {e}")
            QMessageBox.warning(self, "Erro de banco de dados", f"Não foi possivel salvar o cliente.\nDetalhes: {e}")
        except Exception as e:
            self.log_message(f"Erro inesperado ao criar cliente (CPF: {cpf}): {e}")
            QMessageBox.warning(self, "Erro inesperado", f"Ocorreu um erro na aplicação.\nDetalhes: {e}")
            
    
    def create_account(self):
        cpf = self.get_cpf()
        if not cpf:
            self.log_message("CPF do titular é obrigatorio para ciração de conta.")
            return
        
        try:
            # a função do BD ja verifica se o cliente existe
            new_account_number = db.add_account(agency="0001", balance=0, client_cpf= cpf)

            if new_account_number:
                self.log_message(f"Conta número {new_account_number} criada para o cliente de CPF {cpf}.")
                QMessageBox.information(self, "Sucesso", f"Conta {new_account_number} criada com sucesso.")
            else:
                self.log_message(f"Não foi possivel criar a conta. Verifique se o cliente com CPF {cpf} existe.")
                QMessageBox.warning(self, "Erro", "Não foi possível criar a conta.\nVerifique se o cliente com este CPF já está cadastrado.")
       
        except SqliteError as e:
                self.log_message(f"Erro de banco de dados ao criar conta para o CPF {cpf}: {e}")
                QMessageBox.critical(self, "Erro não esperado do banco de dados.",
                                     f"Detalhes : {e}")
        except Exception as e:
            self.log_message(f"Erro inesperado ao criar conta para o cpf {cpf}: {e}")
            QMessageBox.critical(self, "Erro inesperado",
                                 f"Ocorreu um erro na aplicação.... \n Detalhes: {e}")
    
    def deposit_func(self):
        cpf = self.get_cpf()
        value = self.get_value()
        if value is None or value <= 0:
            QMessageBox.warning(self, "Valor Inválido", "Por favor, insira um valor de depósito positivo.")
            return

        client, account = self._get_hydrated_objects(cpf)
        if not account:
            QMessageBox.warning(self, "Operação Falhou", "Cliente não encontrado ou não possui conta.")
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
        cpf = self.get_cpf()
        value = self.get_value()
        if value is None or value <= 0:
            QMessageBox.warning(self, "Valor Inválido", "Por favor, insira um valor de saque positivo.")
            return

        client, account = self._get_hydrated_objects(cpf)
        if not account:
            QMessageBox.warning(self, "Operação Falhou", "Cliente não encontrado ou não possui conta.")
            return
            
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
        cpf = self.get_cpf()
        _, account = self._get_hydrated_objects(cpf)
        if not account:
            QMessageBox.warning(self, "Operação Falhou", "Cliente não encontrado ou não possui conta.")
            return
            
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