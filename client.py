class Client:
    def __init__(self, address):
        self.address = address
        self.accounts = []
        self.indice_account = 0

    def perform_transaction(self, account, transaction):
        try :
            print(f"\nIniciando a operação {transaction.__class__.__name__}...")
            transaction.register(account)
        except Exception as exc:
            print(f"Falha critica na transação! Ocorreu um erro inesperado : {exc} @@@")

    def add_account(self, account):
        self.accounts.append(account)