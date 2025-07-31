from account import Account
from withdraw import Withdraw
import textwrap

class CheckingAccount(Account):
    def __init__(self, number, client, limit=500, withdrawn_limit=3):
        super().__init__(number, client)
        self._limit = limit
        self._withdrawn_limit = withdrawn_limit

    def withdraw(self, value):
        day_withdraws = [
            transaction for transaction in self.history.day_transactions()
            if transaction['type'] == Withdraw.__name__
        ]

        exceeded_limit = value > self._limit
        exceeded_withdrawn_limit = len(day_withdraws) >= self._withdrawn_limit

        if exceeded_limit:
            print(f"!!! Operação não permitida: valor do saque (R$ {value:.2f}) é maior que o seu limite de (R$ {self._limit:.2f}).")
            return False
        
        if exceeded_withdrawn_limit:
            print(f"!!! Operação não permitida: limite de saques diários ({self._withdrawn_limit}) atingido.")
            return False
        
        return super().withdraw(value)
    
    def __str__(self):
        return f"""\
            Agência:\t{self.agency}
            C/C:\t\t{self.number}
            Titular:\t{self.client.name}
            Saldo:\t\t{self.balance}
        """