class Client:
    def __init__(self, address):
        self.address = address
        self.accounts = []
        self.indice_account = 0

    def perform_transaction(self, account, transaction):
        transaction.register(account)

    def add_account(self, account):
        self.accounts.append(account)