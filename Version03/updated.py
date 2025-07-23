# Melhorias aplicadas:
# 1. Otimização do contador de saques na CheckingAccount.
# 2. Sugestão de uso de dict para clientes (implementado).
# 3. Extrato mais eficiente.
# 4. Comentários explicativos.
# 5. Separação de classes em arquivos sugerida nos comentários.

import textwrap
from abc import ABC, abstractclassmethod, abstractproperty
from datetime import datetime

class Client:
    def __init__(self, address):
        self.address = address
        self.accounts = []

    def perform_transaction(self, account, transaction):
        transaction.register(account)

    def add_account(self, account):
        self.accounts.append(account)

class Individual(Client):
    def __init__(self, name, birth_date, cpf, address):
        super().__init__(address)
        self.name = name
        self.birth_date = birth_date
        self.cpf = cpf

class Account:
    def __init__(self, number, client):
        self._balance = 0
        self._number = number
        self._agency = "0001"
        self._client = client
        self._history = History()

    @classmethod
    def new_account(cls, client, number):
        return cls(number, client)

    @property
    def balance(self):
        return self._balance

    @property
    def number(self):
        return self._number

    @property
    def agency(self):
        return self._agency

    @property
    def client(self):
        return self._client

    @property
    def history(self):
        return self._history

    def withdraw(self, value):
        balance = self.balance
        exceeded_balance = value > balance

        if exceeded_balance:
            print("\n@@@ Operação falhou! Você não tem saldo suficiente. @@@")
        elif value > 0:
            self._balance -= value
            print("\n=== Saque realizado com sucesso! ===")
            return True
        else:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
        return False

    def deposit(self, value):
        if value > 0:
            self._balance += value
            print("\n=== Depósito realizado com sucesso! ===")
            return True
        else:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
            return False

class CheckingAccount(Account):
    def __init__(self, number, client, limit=500, withdraw_limit=3):
        super().__init__(number, client)
        self._limit = limit
        self._withdraw_limit = withdraw_limit
        self._withdraw_count = 0  # Otimização: contador de saques

    def withdraw(self, value):
        exceeded_limit = value > self._limit
        exceeded_withdraws = self._withdraw_count >= self._withdraw_limit

        if exceeded_limit:
            print("\n@@@ Operação falhou! O valor do saque excede o limite. @@@")
        elif exceeded_withdraws:
            print("\n@@@ Operação falhou! Número máximo de saques excedido. @@@")
        else:
            result = super().withdraw(value)
            if result:
                self._withdraw_count += 1  # Incrementa apenas se o saque for realizado
                return True
        return False

    def __str__(self):
        return f"""\
            Agência:\t{self.agency}
            C/C:\t\t{self.number}
            Titular:\t{self.client.name}
        """

class History:
    def __init__(self):
        self._transactions = []

    @property
    def transactions(self):
        return self._transactions

    def add_transaction(self, transaction):
        self._transactions.append(
            {
                "type": transaction.__class__.__name__,
                "value": transaction.value,
                "date": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            }
        )

class Transaction(ABC):
    @property
    @abstractproperty
    def value(self):
        pass

    @abstractclassmethod
    def register(self, account):
        pass

class Withdraw(Transaction):
    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value

    def register(self, account):
        transaction_success = account.withdraw(self.value)
        if transaction_success:
            account.history.add_transaction(self)

class Deposit(Transaction):
    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value

    def register(self, account):
        transaction_success = account.deposit(self.value)
        if transaction_success:
            account.history.add_transaction(self)

def menu():
    menu = """\n
    ================ MENU ================
    [d]\tDepositar
    [s]\tSacar
    [e]\tExtrato
    [nc]\tNova conta
    [lc]\tListar contas
    [nu]\tNovo usuário
    [q]\tSair
    => """
    return input(textwrap.dedent(menu))

# Agora clientes é um dict, usando CPF como chave para acesso rápido.
def filter_client(cpf, clients_dict):
    return clients_dict.get(cpf)

def get_client_account(client):
    if not client.accounts:
        print("\n@@@ Cliente não possui conta! @@@")
        return None
    # Sugestão: permitir escolha de conta se houver mais de uma
    if len(client.accounts) > 1:
        print("\nContas disponíveis:")
        for idx, acc in enumerate(client.accounts):
            print(f"[{idx}] Agência: {acc.agency} | Conta: {acc.number}")
        try:
            escolha = int(input("Escolha o número da conta: "))
            return client.accounts[escolha]
        except (ValueError, IndexError):
            print("\n@@@ Escolha inválida! @@@")
            return None
    return client.accounts[0]

def deposit_func(clients_dict):
    cpf = input("Informe o CPF do cliente: ")
    client = filter_client(cpf, clients_dict)
    if not client:
        print("\n@@@ Cliente não encontrado! @@@")
        return
    value = float(input("Informe o valor do depósito: "))
    transaction = Deposit(value)
    account = get_client_account(client)
    if not account:
        return
    client.perform_transaction(account, transaction)

def withdraw_func(clients_dict):
    cpf = input("Informe o CPF do cliente: ")
    client = filter_client(cpf, clients_dict)
    if not client:
        print("\n@@@ Cliente não encontrado! @@@")
        return
    value = float(input("Informe o valor do saque: "))
    transaction = Withdraw(value)
    account = get_client_account(client)
    if not account:
        return
    client.perform_transaction(account, transaction)

def show_statement(clients_dict):
    cpf = input("Informe o CPF do cliente: ")
    client = filter_client(cpf, clients_dict)
    if not client:
        print("\n@@@ Cliente não encontrado! @@@")
        return
    account = get_client_account(client)
    if not account:
        return
    print("\n================ EXTRATO ================")
    transactions = account.history.transactions
    if not transactions:
        print("Não foram realizadas movimentações.")
    else:
        # Extrato mais eficiente usando join
        statement = "\n".join(
            f"{t['date']} - {t['type']}: R$ {t['value']:.2f}" for t in transactions
        )
        print(statement)
    print(f"\nSaldo:\n\tR$ {account.balance:.2f}")
    print("==========================================")

def create_client(clients_dict):
    cpf = input("Informe o CPF (somente número): ")
    if filter_client(cpf, clients_dict):
        print("\n@@@ Já existe cliente com esse CPF! @@@")
        return
    name = input("Informe o nome completo: ")
    birth_date = input("Informe a data de nascimento (dd-mm-aaaa): ")
    address = input("Informe o endereço (logradouro, nro - bairro - cidade/sigla estado): ")
    client = Individual(name=name, birth_date=birth_date, cpf=cpf, address=address)
    clients_dict[cpf] = client
    print("\n=== Cliente criado com sucesso! ===")

def create_account(account_number, clients_dict, accounts):
    cpf = input("Informe o CPF do cliente: ")
    client = filter_client(cpf, clients_dict)
    if not client:
        print("\n@@@ Cliente não encontrado, fluxo de criação de conta encerrado! @@@")
        return
    account = CheckingAccount.new_account(client=client, number=account_number)
    accounts.append(account)
    client.accounts.append(account)
    print("\n=== Conta criada com sucesso! ===")

def list_accounts(accounts):
    for account in accounts:
        print("=" * 100)
        print(textwrap.dedent(str(account)))

def main():
    clients_dict = {}  # Agora clientes é um dict
    accounts = []
    while True:
        option = menu()
        if option == "d":
            deposit_func(clients_dict)
        elif option == "s":
            withdraw_func(clients_dict)
        elif option == "e":
            show_statement(clients_dict)
        elif option == "nu":
            create_client(clients_dict)
        elif option == "nc":
            account_number = len(accounts) + 1
            create_account(account_number, clients_dict, accounts)
        elif option == "lc":
            list_accounts(accounts)
        elif option == "q":
            break
        else:
            print("\n@@@ Operação inválida, por favor selecione novamente a operação desejada. @@@")

main()