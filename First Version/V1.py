menu = """

  [d] Depositar
  [s] Sacar
  [e] Extrato
  [q] Sair

  """

balance = 0
limit = 500
statement = ""
number_of_withdrawals = 0
WITHDRAWAL_LIMIT = 3

while True:

    option = input(menu)

    if option == "d":
        value = float(input("Informe o valor do deposito: "))

        if value > 0:
            balance += value
            statement += f"Deposito: R$ {value:.2f}\n"
        else:
            print("Operacao falhou! O valor informado é invalido.")

    elif option == "s":
        value = float(input("Informe o valor do saque: "))

        exceeded_balance = value > balance

        exceeded_limit = value > limit
        
        exceeded_withdrawals = number_of_withdrawals >= WITHDRAWAL_LIMIT

        if exceeded_balance:
            print("Operação falhou! Você não tem saldo suficiente.")

        elif exceeded_limit:
            print("Operação falhou! O valor do saque ultrapassou o limite.")

        elif exceeded_withdrawals:
            print("Operação falhou! Número maximo de saques excedidos.")

        elif value > 0:
            balance -= value
            statement += f"Saque: R$ {value:.2f}\n"
            number_of_withdrawals += 1

        else:
            print("Operação falhou! O valor informado é invalido.")

    elif option == "e":
        print("\n================== Extrato =================")
        print("Não foram realizadas movimentações." if not statement else statement)
        print(f"\n Saldo: R$ {balance:.2f}")
        print("=============================================")

    elif option == "q":
        break
    
    else:
        print("Operação invalida, porfavor selecione novamente a operação desejada.")