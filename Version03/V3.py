import textwrap
from abc import ABC, abstractclassmethod, abstractproperty
from datetime import datetime


# É interessante você separar cada classe em um arquivo diferente.
# Isso facilita o reuso em outros sistemas, além de não sobrecarregar o processo com classes
# que podem ser desnecessárias no contexto.
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
        else:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
            return False

        return True


class CheckingAccount(Account):
    def __init__(self, number, client, limit=500, withdraw_limit=3):
        super().__init__(number, client)
        self._limit = limit
        self._withdraw_limit = withdraw_limit

    def withdraw(self, value):
        # Você precisa contar as transações todas as vezes que o cliente solicitar uma nova?
        # Pense o quanto de overload você pode causar em um banco com 10 milhões de clientes e uma média
        # de 50 transações por intervalo de tempo... Cada saque teria que ler 500 milhões de transações antes
        # de fazer uma nova... Pense numa estratégia que melhore esse gargalo.
        withdraw_count = len(
            [transaction for transaction in self.history.transactions if transaction["type"] == Withdraw.__name__]
        )

        exceeded_limit = value > self._limit
        exceeded_withdraws = withdraw_count >= self._withdraw_limit

        if exceeded_limit:
            print("\n@@@ Operação falhou! O valor do saque excede o limite. @@@")

        elif exceeded_withdraws:
            print("\n@@@ Operação falhou! Número máximo de saques excedido. @@@")

        else:
            return super().withdraw(value)

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
                "date": datetime.now().strftime("%d-%m-%Y %H:%M:%s"),
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

def filter_client(cpf, clients):
    # CPF é um valor numérico. Se você pensar no conceito de hash ou dict,
    # essa operação não precisa ser feita, já que o próprio CPF pode ser o indice da
    # lista de clientes
    filtered_clients = [client for client in clients if client.cpf == cpf]
    return filtered_clients[0] if filtered_clients else None


def get_client_account(client):
    if not client.accounts:
        print("\n@@@ Cliente não possui conta! @@@")
        return

    # FIXME: não permite cliente escolher a conta
    return client.accounts[0]


# Se você instanciar o seu sistema solicitando o cliente que será utilizando
# não tem porque ter esse cpf sendo informado o tempo inteiro.
# Pense nos bancos normais, uma vez que você "acessou", você opera na conta selecionada.
# Ajuste para ficar nesse fluxo.
def deposit_func(clients):
    cpf = input("Informe o CPF do cliente: ")
    client = filter_client(cpf, clients)

    if not client:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    value = float(input("Informe o valor do depósito: "))
    transaction = Deposit(value)

    account = get_client_account(client)
    if not account:
        return

    client.perform_transaction(account, transaction)


def withdraw_func(clients):
    cpf = input("Informe o CPF do cliente: ")
    client = filter_client(cpf, clients)

    if not client:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    value = float(input("Informe o valor do saque: "))
    transaction = Withdraw(value)

    account = get_client_account(client)
    if not account:
        return

    client.perform_transaction(account, transaction)


def show_statement(clients):
    cpf = input("Informe o CPF do cliente: ")
    client = filter_client(cpf, clients)

    if not client:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    account = get_client_account(client)
    if not account:
        return

    print("\n================ EXTRATO ================")
    transactions = account.history.transactions

    # Vou deixar a melhoria pontual desse bloco (271-276)
    # para sua criatividade. Mas dá pra ser mais eficiente aqui
    statement = ""
    if not transactions:
        statement = "Não foram realizadas movimentações."
    else:
        for transaction in transactions:
            statement += f"\n{transaction['type']}:\n\tR$ {transaction['value']:.2f}"

    print(statement)
    print(f"\nSaldo:\n\tR$ {account.balance:.2f}")
    print("==========================================")


def create_client(clients):
    cpf = input("Informe o CPF (somente número): ")
    client = filter_client(cpf, clients)

    if client:
        print("\n@@@ Já existe cliente com esse CPF! @@@")
        return

    name = input("Informe o nome completo: ")
    birth_date = input("Informe a data de nascimento (dd-mm-aaaa): ")
    address = input("Informe o endereço (logradouro, nro - bairro - cidade/sigla estado): ")

    client = Individual(name=name, birth_date=birth_date, cpf=cpf, address=address)

    clients.append(client)

    print("\n=== Cliente criado com sucesso! ===")


def create_account(account_number, clients, accounts):
    cpf = input("Informe o CPF do cliente: ")
    client = filter_client(cpf, clients)

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
    clients = []
    accounts = []

    while True:
        option = menu()

        if option == "d":
            deposit_func(clients)

        elif option == "s":
            withdraw_func(clients)

        elif option == "e":
            show_statement(clients)

        elif option == "nu":
            create_client(clients)

        elif option == "nc":
            account_number = len(accounts) + 1
            create_account(account_number, clients, accounts)

        elif option == "lc":
            list_accounts(accounts)

        elif option == "q":
            break

        else:
            print("\n@@@ Operação inválida, por favor selecione novamente a operação desejada. @@@")


main()