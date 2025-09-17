class Client:
    def __init__(self, address):
        self.address = address
        self.accounts = []
        self.indice_account = 0

    def perform_transaction(self, account, transaction):
        transaction_sucess = False
        try :
            print(f"\nIniciando a operação {transaction.__class__.__name__}...")
            transaction_sucess = transaction.register(account)
        except Exception as exc:
            print(f"Falha critica na transação! Ocorreu um erro inesperado : {exc} @@@")

        return transaction_sucess
    
    def add_account(self, account):
        self.accounts.append(account)