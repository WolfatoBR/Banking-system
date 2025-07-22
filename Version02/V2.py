import textwrap

def main():
    LIMIT_WITHDRAW = 3
    AGENC = "0001"

    balance = 0
    limit = 500
    statement = ""
    number_withdraw = 0
    users = []
    acconts= []

    while True:
        option = menu()

        if option == "d":
           value = float(input("Informe o valor do deposito: "))
           balance, statement = deposit(balance, value, statement)
        
        elif option == "s":
            value = float(input("Informe o valor do saque: "))
            balance, statement = withdraw(balance=balance,
                                          value=value,
                                          statement=statement,
                                          limit=limit,
                                          number_withdraw=number_withdraw,
                                          limit_withdraw=LIMIT_WITHDRAW)
        
        elif option == "e":
            statement_accont(balance, statement=statement)
        
        elif option == "nu":
            new_user(users)
        
        elif option == "nc":
            number_accont = len(acconts) + 1
            accont = create_accont(AGENC, number_accont, users)
            
            if accont:
                acconts.append(accont)
        
        elif option == "lc":
            list_acconts(acconts)
        
        elif option == "q":
            break
        
        else:
            print("Operação invalida, por favor selecione novamente a opção desejada.")

def menu():
    menu = """\n
    ==========MENU==========
    [d]\tDepositar
    [s]\tSacar
    [e]\tExtrato
    [nc]\tNova Conta
    [lc]\tListar Contas
    [nu]\tNovo Usuario
    [q]\tSair
    => """
            #textwrap => serve para remover os recuos
    return input(textwrap.dedent(menu))

# Funcao Deposito : Saldo, valor, extrato
def deposit(balance, value, statement, /):
    if value > 0:
        balance += value
        statement += f"Deposito: R$ {value:.2f}\n"
    else:
        print("A operação de Deposito falhou! O valor informado é invalido.")
    
    return balance, statement


# Funcao Sacar : Saldo, valor, extrato, limite, numero_saques, limite_saque
def withdraw(*, balance, value, statement, limit, number_withdraw, limit_withdraw):
    
    exceeded_balance = value > balance
    
    exceeded_limit = value > limit

    exceeded_withdraw = number_withdraw >= limit_withdraw

    if exceeded_balance:
        print("Operação falhou! Você não possui saldo suficiente.")
    elif exceeded_limit:
        print("Operação falhou! O valor do saque ultrapassa o limite disponivel.")
    elif exceeded_withdraw:
        print("Operação falhou! Número maximo de saques excedidos.")
    
    elif value>0:
        balance -= value
        statement += f"Saque: R$ {value:.2f}\n"
        number_withdraw+=1
    else:
        print("Operação falhou! O valor informado é invalido.")
    
    return balance, statement

def statement_accont(balance,/, *, statement):
    print("\n========== Extrato =========")
    print("Não foram realizadas movimentações." if not statement else statement)
    print(f"\n\t Saldo: R$ {balance:.2f}")
    print("=========================")

def new_user(users):
    cpf = input("Informe o numero de CPF (apenas numeros).")
    user = filter_user(cpf, users)

    if user:
        print(f"\n@@@ Já existe usuario em esse CPF! {cpf} @@@")
        return
    
    name = input("Infrome o nome Completo: ")
    date_of_birth = input("Informe a data de nascimento (dd-mm-aaaa): ")
    address = input("Informe o endereço (logradouro, numero - bairro - cidade/sigla estado): ")

    users.append({"nome": name, "data_nascimento": date_of_birth, "cpf": cpf, "endereco": address})

    print("=== Usuario com sucesso ===")

def filter_user(cpf, users):
    users_filters = [user for user in users if user["cpf"] == cpf]
    return users_filters[0] if users_filters else None

def create_accont(agenc, number_accont, users):
    cpf = input("Informe o CPF do usuário: ")
    user = filter_user(cpf, users)

    if user:
        print("\n=== Conta criada com sucesso! ===")
        return {"agencia": agenc, "numero_conta": number_accont, "usuario": user}

    print("\n@@@ Usuário não encontrado, fluxo de criação de conta encerrado! @@@")


def list_acconts(acconts):
    for accont in acconts:
        row = f"""\
            Agência:\t{accont['agencia']}
            C/C:\t\t{accont['numero_conta']}
            Titular:\t{accont['usuario']['nome']}
        """
        print("=" * 100)
        print(textwrap.dedent(row))

main()