"""
Lagrangian main loop with its parameters.
Here we use subgradient method to calculate lambdas.
"""

import dataclasses
import typing

from config import Config
from solver import Solver

from .sub_problems import WheatSubProblem, CornSubProblem, BeetSubProblem


@dataclasses.dataclass
class Parameters:
    lower_bound: float
    upper_bound: float
    k_1_bound: int
    k_bound: int


class Lagrange(Solver):
    def __init__(self, cfg: Config, param: Parameters):
        self.cfg = cfg
        self.k = 1
        self.k_1 = 0
        self.tau = 2.0
        self._lambda = 0.0
        self.lower_bound = param.lower_bound
        self.upper_bound = param.upper_bound
        self.k_1_bound = param.k_1_bound
        self.k_bound = param.k_bound

        self.iterations: typing.Dict[str, typing.List[float]] = {
            "k": [],
            "x_1": [],
            "x_2": [],
            "x_3": [],
            "z_lb": [],
            "omega": [],
            "teta": [],
            "lambda": [],
        }

    def solve(self):
        wheat_sub_problem = WheatSubProblem(self.cfg)
        corn_sub_problem = CornSubProblem(self.cfg)
        beet_sub_problem = BeetSubProblem(self.cfg)

        while True:
            z_1, x_1 = wheat_sub_problem.solve(self._lambda)
            z_2, x_2 = corn_sub_problem.solve(self._lambda)
            z_3, x_3 = beet_sub_problem.solve(self._lambda)
            z_lb = z_1 + z_2 + z_3 - self.cfg.area * self._lambda

            self.iterations["k"].append(self.k)
            self.iterations["x_1"].append(x_1)
            self.iterations["x_2"].append(x_2)
            self.iterations["x_3"].append(x_3)
            self.iterations["z_lb"].append(z_lb)
            self.iterations["lambda"].append(self._lambda)

            if z_lb > self.lower_bound:
                self.lower_bound = z_lb
                self.k_1 = 0
            else:
                self.k_1 += 1

            if self.k_1 == self.k_1_bound:
                self.tau = self.tau / 2
                self.k_1 = 0

            self.k += 1

            omega = x_1 + x_2 + x_3 - self.cfg.area

            teta = self.tau * (self.upper_bound - z_lb) / (omega ** 2)

            self.iterations["teta"].append(teta)
            self.iterations["omega"].append(omega)

            if (omega <= 0 and self._lambda * omega == 0) or (
                self.k == self.k_bound
            ):
                return (z_lb, x_1, x_2, x_3)

            self._lambda = max(0, self._lambda + teta * omega)
