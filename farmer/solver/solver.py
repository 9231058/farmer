import abc

from .result import Result


class Solver(abc.ABC):
    @abc.abstractmethod
    def solve(self) -> Result:
        pass
