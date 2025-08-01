class Client:
    def __init__(self, address):
        self.address = address
        self.accounts = []
        self.indice_account = 0

    def perform_transaction(self, account, transaction):
        # TODO: validar o número de transações e invalidar a operação se for necessário
        # print("\n@@@ Você excedeu o número de transações permitidas para hoje! @@@")
        transaction.register(account)

    def add_account(self, account):
        self.accounts.append(account)