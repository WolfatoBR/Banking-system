from individual import Individual
from checkingAccount import CheckingAccount
from deposit import Deposit
from withdraw import Withdraw
from accountsIteractor import AccountsIteractor
import textwrap ; from datetime import datetime

LOG_FILE = "log_bancario.txt"

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

#decorador
def log_transaction(func):
    def wrapper(*args, **kwargs):
        timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        log_message_start = f"[{timestamp}] - INFO - Iniciando operação: '{func.__name__}'\n"

        # abrir o arquivo em modo de append e escreve o log de inicio
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(log_message_start)
        except IOError as exc:
            print(f"@@@ Erro ao escrever no arquivo de log: {exc} @@@")
        
        print(log_message_start.strip()) # .strip() vai remover a quebra de linha

        # executando func original
        result = func(*args, **kwargs)

        timestamp_end = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        log_message_end = f"[{timestamp_end}] - INFO - Operação finalizada: '{func.__name__}'\n"

        # escreve o log de finalização
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(log_message_end)
        except IOError as exc:
            print(f"@@@ Erro ao escrever no arquivo de log: {exc} @@@")

        return result
    return wrapper

def filter_client(cpf, clients_dict):
    return clients_dict.get(cpf)

def get_client_account(client):
    if not client.accounts:
        print("\n !!! Cliente não possui conta cadastrada. !!!")
        return None
    
    if len(client.accounts) > 1:
        print("\nContas disponíveis:")
        for i, account in enumerate(client.accounts):
            # mostra as opções começando em 1
            print(f"    [{i + 1}] Agência: {account.agency} | Conta: {account.number}")
        
        try:
            choice = int(input("Escolha o número da conta: "))
            
            if i<= choice <= len(client.accounts):
                # subtrai 1 para pegar o indice correto
                return client.accounts[choice - 1]
            else:
                print("\n!!! Opção inválida. Por favor, escolha um dos número listados. !!!")
                return None
            
        except (ValueError, IndexError):
            print("\n !!! Opção inválida. Por favor, digite apenas o numero da conta. !!!")
            return None
        
    return client.accounts[0]

@log_transaction
def deposit_func(clients_dicts):
    cpf = input("Informe o CPF do cliente: ")
    client = filter_client(cpf, clients_dicts)

    if not client:
        print("\n !!! Cliente não encontrado !!!")
        return
    
    value = float(input("Informe o valor do depósito: "))
    transaction = Deposit(value)
    account = get_client_account(client)

    if not account:
        return
    client.perform_transaction(account, transaction)

@log_transaction
def withdraw_func(clients_dicts):
    cpf = input("Informe o CPF do cliente: ")
    client = filter_client(cpf, clients_dicts)

    if not client:
        print("\n !!! Cliente não encontrado !!!")
        return
    
    value = float(input("Informe o valor do saque: "))
    transaction = Withdraw(value)
    account = get_client_account(client)

    if not account:
        return
    client.perform_transaction(account, transaction)

@log_transaction
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
    statemant = ""
    have_transactions = False
    for transaction in account.history.generate_report(type_transaction=None):
        have_transactions = True
        statemant += f"\n{transaction['type']}:\n\tR$ {transaction['value']:.2f}\n"
    
    if not have_transactions:
        statemant = "Não foram realizadas transações nesta conta."
    
    print(statemant)
    print(f"\nSaldo:\n\tR$ {account.balance:.2f}")
    print("==========================================")

@log_transaction
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

@log_transaction
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

@log_transaction
def list_accounts(accounts):
    for account in AccountsIteractor(accounts):
        print("=" * 70)
        print(textwrap.dedent(str(account)))
    if not accounts:
        print("Não existe contas deste usuario!!!")

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