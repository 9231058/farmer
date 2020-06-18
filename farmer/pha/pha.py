"""
Main loop of PHA algorithm.
"""

import dataclasses
import typing
import math

from config import Config
from solver import Solver

from .base_problem import BaseProblem


@dataclasses.dataclass
class Parameters:
    """
    PHA method parameters
    """

    epsilon: float
    rou_transform: typing.Callable[[float], float]


class PHA(Solver):
    def __init__(self, cfg: Config, param: Parameters):
        self.cfg = cfg

        self.eplison = param.epsilon
        self.rou_transform = param.rou_transform

        self.iterations: typing.Dict[str, typing.List[float]] = {
            "k": [],
            "x_hat_1": [],
            "x_hat_2": [],
            "x_hat_3": [],
            "rou": [],
            "z": [],
            "difference": [],
        }

    def solve(self):
        base_problems: typing.List[BaseProblem] = []
        _lambda: typing.List[typing.Tuple[float, float, float]] = []
        rou = 0
        x_hat_1 = 0
        x_hat_2 = 0
        x_hat_3 = 0
        k = 0

        probability = 1 / len(self.cfg.scenarios)
        for index, scenario in enumerate(self.cfg.scenarios):
            base_problems.append(
                BaseProblem(index, scenario, probability, self.cfg)
            )
            _lambda.append((0, 0, 0))

        while True:
            z_total = 0
            x_total_1 = 0
            x_total_2 = 0
            x_total_3 = 0

            difference = 0

            x_s_1 = []
            x_s_2 = []
            x_s_3 = []

            for base_problem in base_problems:
                z, x_1, x_2, x_3 = base_problem.solve(
                    _lambda[base_problem.index], rou, x_hat_1, x_hat_2, x_hat_3
                )

                x_s_1.append(x_1)
                x_s_2.append(x_2)
                x_s_3.append(x_3)

                z_total += z
                x_total_1 += base_problem.probability * x_1
                x_total_2 += base_problem.probability * x_2
                x_total_3 += base_problem.probability * x_3

                difference += base_problem.probability * (x_1 - x_hat_1) ** 2
                difference += base_problem.probability * (x_2 - x_hat_2) ** 2
                difference += base_problem.probability * (x_3 - x_hat_3) ** 2

            x_hat_1 = x_total_1
            x_hat_2 = x_total_2
            x_hat_3 = x_total_3

            for base_problem in base_problems:
                _lambda[base_problem.index] = (
                    _lambda[base_problem.index][0]
                    + rou * (x_s_1[base_problem.index] - x_hat_1),
                    _lambda[base_problem.index][1]
                    + rou * (x_s_2[base_problem.index] - x_hat_2),
                    _lambda[base_problem.index][2]
                    + rou * (x_s_3[base_problem.index] - x_hat_3),
                )

            if k == 0:
                rou = 0.1
            else:
                rou = self.rou_transform(rou)

            self.iterations["k"].append(k)
            self.iterations["x_hat_1"].append(x_hat_1)
            self.iterations["x_hat_2"].append(x_hat_2)
            self.iterations["x_hat_3"].append(x_hat_3)
            self.iterations["rou"].append(rou)
            self.iterations["z"].append(z_total)
            self.iterations["difference"].append(difference)

            if math.isclose(difference ** 0.5, 0, abs_tol=self.eplison):
                return z_total, x_hat_1, x_hat_2, x_hat_3

            k += 1
