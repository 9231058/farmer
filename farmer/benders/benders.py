import math
import typing

from config import Config
from solver import Solver, Result
from .sub_problem import SubProblem
from .master_problem import MasterProblem


class Benders(Solver):
    def __init__(self, cfg: Config, epsilon: float = 0.01):
        self.cfg = cfg
        self.epsilon = epsilon
        self.iterations: typing.Dict[str, typing.List[float]] = {
            "k": [],
            "x_1": [],
            "x_2": [],
            "x_3": [],
            "z_lb": [],
            "z_ub": [],
            "pi_1": [],
            "pi_2": [],
            "pi_3": [],
        }

    def solve(self) -> Result:
        master_problem = MasterProblem(self.cfg)
        k = 0

        while True:
            k += 1
            self.iterations["k"].append(k)

            z_lb, x_1, x_2, x_3 = master_problem.solve()

            self.iterations["x_1"].append(x_1)
            self.iterations["x_2"].append(x_2)
            self.iterations["x_3"].append(x_3)
            self.iterations["z_lb"].append(z_lb)

            z_star, pi_1, pi_2, pi_3 = SubProblem(self.cfg).solve(
                x_1, x_2, x_3
            )
            z_ub = (
                z_star
                + self.cfg.wheat.plant_cost * x_1
                + self.cfg.corn.plant_cost * x_2
                + self.cfg.beet.plant_cost * x_3
            )

            self.iterations["pi_1"].append(pi_1)
            self.iterations["pi_2"].append(pi_2)
            self.iterations["pi_3"].append(pi_3)
            self.iterations["z_ub"].append(z_ub)

            if math.isclose(z_lb, z_ub, abs_tol=self.epsilon):
                return Result(z_ub, x_1, x_2, x_3)

            master_problem.add_cut(
                z_star - pi_1 * x_1 - pi_2 * x_2 - pi_3 * x_3, pi_1, pi_2, pi_3
            )
