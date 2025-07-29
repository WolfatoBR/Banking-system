from abc import ABC, abstractmethod,abstractclassmethod, abstractproperty

class Transaction(ABC):
    @property
    @abstractproperty
    def value(self):
        pass
    
    @abstractclassmethod
    def register(self, account):
        pass