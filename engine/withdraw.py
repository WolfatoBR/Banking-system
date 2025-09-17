from engine.transaction import Transaction

class Withdraw(Transaction):
    def __init__(self, value):
        self._value = value
    
    @property
    def value(self):
        return self._value

    def register(self, account):
        return account.withdraw(self._value)