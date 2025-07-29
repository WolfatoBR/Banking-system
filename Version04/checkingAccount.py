from account import Account
import textwrap

class CheckingAccount(Account):
    def __init__(self, number, client, limit=500, withdrawn_limit=3):
        super().__init__(number, client)
        self._limit = limit
        self._withdrawn_limit = withdrawn_limit
        self._withdrawn_count = 0

    def withdraw(self, value):
        exceeded_limit = value > self._limit
        exceeded_withdrawn_limit = self._withdrawn_count >= self._withdrawn_limit

        if exceeded_limit:
            print(f"!!! Operação não permitida: valor {value} maior que o limite de {self._limit}.")
            return False
        if exceeded_withdrawn_limit:
            print(f"!!! Operação não permitida: limite de saques atingido ({self._withdrawn_limit}).")
            return False
        else:
            result = super().withdraw(value)
            if result:
                self._withdrawn_count += 1
                print(f"Operação realizada com sucesso. Saque de {value} realizado.")
            return result
        return False
    
    def __str__(self):
        return f"""\
            Agência:\t{self.agency}
            C/C:\t\t{self.number}
            Titular:\t{self.client.name}
        """