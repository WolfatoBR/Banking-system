from Individual import Individual
from CheckingAccount import CheckingAccount
from Deposit import Deposit
from Withdraw import Withdraw
# Version 0.4 - Sistema bancário simples
# Importando as classes necessárias para o funcionamento do sistema
# Individual representa o cliente, CheckingAccount representa a conta corrente,
# Deposit e Withdraw representam as transações de depósito e saque, respectivamente.

import textwrap

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

def filter_client(cpf, clients_dict):
    return clients_dict.get(cpf)

def get_client_account(client):
    if not client.account:
        print("\n !!! Conta não encontrada !!!")
        return None
    
    if len(client.account) > 1:
        print("\n Contas disponiveis:")
        for i, account in enumerate(client.accounts):
            print(f"[{i}] Agência: {account.agency} | Conta: {account.number}")
        
        try:
            choice = int(input("Escolha o número da conta: "))
            return client.accounts[choice]
        except (ValueError, IndexError):
            print("\n !!! Opção inválida !!!")
            return None
        
    return client.account[0]

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