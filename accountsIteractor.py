class AccountsIteractor:
    def __init__(self, accounts):
        self.accounts = accounts
        self._index = 0
    
    def __iter__(self):
        return self
    
    def __next__(self):
        try:
            account = self.accounts[self._index]
            return f"""\
                Agência:\t{account.agency}
                Número:\t\t{account.number}
                Titular:\t{account.client.name}
                Saldo:\t\tR$ {account.balance:.2f}
        """
        except IndexError:
            raise StopIteration
        finally:
            self._index +=1