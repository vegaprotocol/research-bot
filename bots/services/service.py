from abc import ABC, abstractmethod


class Service(ABC):
    @abstractmethod
    def check(self):
        """
        Run pre-start checks
        """
        pass

    @abstractmethod
    def wait(self):
        """
        Wait for some conditions
        """
        pass

    @abstractmethod
    def start(self):
        """
        Start the service
        """
        pass
