from transaction import Transaction

class Withdraw(Transaction):
    def __init__(self, value):
        self._value = value
    
    @property
    def value(self):
        return self._value

    def register(self, account):
        Transaction_sucsess = account.withdraw(self._value)
        if Transaction_sucsess:
            account.history.add_transaction(self)