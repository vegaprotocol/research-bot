from abc import ABC, abstractmethod

class Handler(ABC):
    @abstractmethod
    def serve(self):
        """
        Serve the http response
        """
        pass