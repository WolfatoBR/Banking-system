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
        self.ui.list_accounts_button.clicked.connect(self.list_accounts)
        
        # validação em tempo real
        self.ui.cpf_input.editingFinished.connect(self.validate_cpf_field)
    
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
    
    def validate_cpf_field(self):
        """
        Valida o CPF em tempo real quando o usúario sai do campo.
        Muda a cor do campo indicando se é valido ou não.
        """
        cpf = self.ui.cpf_input.text().strip()

        if not cpf:
            # sem validação
            self.reset_cpf_field_style()
            return
        
        if self.validate_cpf(cpf):
            #se for valido, ira ficar verde
            self.set_cpf_field_valid()
            self.log_message(f"CPF {cpf} validado com sucesso.")
        
        else:
            #se for invalido , campo vermelho
            self.set_cpf_field_invalid()
            self.log_message(f"CPF {cpf} é invalido!")
            QMessageBox.warning(self, "CPF invalido",
                                f"O CPF '{cpf}' não é valido.\nPor favor, verifique e digite novamente."
                                )
        
    def set_cpf_field_valid(self):
        """Define o estilo do campo CPF como valido (verde)."""
        self.ui.cpf_input.setStyleSheet("""
                QLineEdit {
                            border: 2px solid #4CAF50;
                            background-color: #E8F5E9;
                                        }
                                        """)
    
    def set_cpf_field_invalid(self):
        """Define o estilo do campo CPF como invalido(vermelho)."""
        self.ui.cpf_input.setStyleSheet("""
                QLineEdit {
                            border: 2px solid #F44336;
                            background-color: #FFEBEE
                                        }
                                        """)
    
    def reset_cpf_field_style(self):
        """Reseta o estilo do campo CPF para o padrão"""
        self.ui.cpf_input.setStyleSheet("")

    def validate_cpf(self, cpf):
        """
        Valida um cpf Brasileiro.
        
        args:
            cpf (str): CPF a ser validado (pode conter pontos e traço)
            
        Returns:
            bool: True se o CPF é valido, False caso não.
        """

        # Remove caracteres não numéricos
        cpf_clean = ''.join(filter(str.isdigit, cpf))
        
        # Verifica se tem 11 dígitos
        if len(cpf_clean) != 11:
            return False
        
        # Verifica se os dígitos são todos iguais
        if cpf_clean == cpf_clean[0] * 11:
            return False
        
        # Calcula o primeiro dígito verificador
        sum_product = sum(int(a) * b for a, b in zip(cpf_clean[0:9], range(10, 1, -1)))
        expected_digit_1 = (sum_product * 10 % 11) % 10
        
        if int(cpf_clean[9]) != expected_digit_1:
            return False
        
        # Calcula o segundo dígito verificador
        sum_product_2 = sum(int(a) * b for a, b in zip(cpf_clean[0:10], range(11, 1, -1)))
        expected_digit_2 = (sum_product_2 * 10 % 11) % 10
        
        if int(cpf_clean[10]) != expected_digit_2:
            return False
        
        return True

    def get_cpf(self):
        cpf = self.ui.cpf_input.text().strip()
        if not cpf:
            return None
        if not self.validate_cpf(cpf):
            QMessageBox.warning(self, "CPF invalido", "Porfavor, insira um CPF valido.")
            return None
        return cpf
    
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

        date_dialog = DateDialog(self)

        # .exec() abre o dialogo
        if date_dialog.exec():
            birth_qdate = date_dialog.selected_date()
            # vamos converter o objeto QDate para o Python
            birth_date = birth_qdate.toPyDate()
        else:
            return
        
        today = datetime.now().date()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

        if age < 18:
            self.log_message(f"Tentativa de cadastro de menor de idade (CPF: {cpf} | Idade: {age})")
            QMessageBox.warning(self, "Idade Invalida", f"O cliente deve ter no minimo 18 anos. Idade calculada: {age} anos.")
            return
        
        address, _ = QInputDialog.getText(self, "Novo Clienete", "Endereço:")
        if not address.strip():
            return
        
        birth_date_str = birth_date.strftime("%d-%m-%Y")

        if db.add_client(cpf, name, birth_date_str, address):
            self.log_message(f"Cliente {name} (CPF: {cpf}) criado com sucesso.")
            QMessageBox.information(self, "Sucesso", "Cliente criado com sucesso.")
            self.ui.cpf_input.clear()
        else:
            self.log_message(f"Erro: Cliente com CPF {cpf} já existe.")
            QMessageBox.warning(self, "Erro", "Ja existe um cliente com esse CPF.")

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