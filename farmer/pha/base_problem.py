"""
Base problem of PHA. It is a master problem for an specific scenario.
"""
import typing

from gurobipy import Model, QuadExpr

from config import Config


class BaseProblem:
    def __init__(
        self, index: int, scenario: float, probability: float, cfg: Config
    ):
        self.cfg = cfg

        self.probability = probability
        self.index = index
        self.scenario = scenario

        self.objective = QuadExpr()

        # model.ModelSense is minimization by default
        self.model = Model(f"base_problem_{self.index}")

        self.x_1 = self.model.addVar(ub=self.cfg.area, name="x_1")
        self.x_2 = self.model.addVar(ub=self.cfg.area, name="x_2")
        self.x_3 = self.model.addVar(ub=self.cfg.area, name="x_3")

        self.model.addConstr(self.x_1 + self.x_2 + self.x_3 <= self.cfg.area)

        self.objective.add(
            self.x_1 * self.cfg.wheat.plant_cost * self.probability
        )
        self.objective.add(
            self.x_2 * self.cfg.corn.plant_cost * self.probability
        )
        self.objective.add(
            self.x_3 * self.cfg.beet.plant_cost * self.probability
        )

        self._corn_variables_constraint()
        self._wheat_variables_constraint()
        self._beet_variables_constraint()

    def _wheat_variables_constraint(self):
        y_11 = self.model.addVar(name=f"y_11_{self.index}")
        y_12 = self.model.addVar(name=f"y_12_{self.index}")

        self.objective.add(y_11 * self.cfg.wheat.buy_price * self.probability)
        self.objective.add(
            y_12 * -self.cfg.wheat.sell_price * self.probability
        )

        self.model.addConstr(
            self.cfg.wheat.requirement
            <= self.x_1 * self.cfg.wheat.produce_rate * (1 + self.scenario)
            + y_11
            - y_12,
            name="wheat_produce_constraint",
        )

    def _corn_variables_constraint(self):
        y_21 = self.model.addVar(name=f"y_21_{self.index}")
        y_22 = self.model.addVar(name=f"y_22_{self.index}")

        self.objective.add(y_21 * self.cfg.corn.buy_price * self.probability)
        self.objective.add(y_22 * -self.cfg.corn.sell_price * self.probability)

        self.model.addConstr(
            self.cfg.corn.requirement
            <= self.x_2 * self.cfg.corn.produce_rate * (1 + self.scenario)
            + y_21
            - y_22,
            name="cron_produce_constraint",
        )

    def _beet_variables_constraint(self):
        y_32 = self.model.addVar(
            ub=self.cfg.beet.max_demand, name=f"y_32_{self.index}",
        )
        y_33 = self.model.addVar(name=f"y_33_{self.index}")

        self.objective.add(
            y_32 * -self.cfg.beet.sell_price_high * self.probability
        )
        self.objective.add(
            y_33 * -self.cfg.beet.sell_price_low * self.probability
        )

        self.model.addConstr(
            self.x_3 * self.cfg.beet.produce_rate * (1 + self.scenario)
            >= y_32 + y_33,
            name="beet_produce_constraint",
        )

    def solve(
        self,
        _lambda: typing.Tuple[float, float, float],
        rou: float,
        x_hat_1: float,
        x_hat_2: float,
        x_hat_3: float,
    ):
        obj = self.objective.copy(1)

        obj.add(_lambda[0] * self.x_1)
        obj.add(_lambda[1] * self.x_2)
        obj.add(_lambda[2] * self.x_3)
        obj.add(rou / 2 * (self.x_1 - x_hat_1) * (self.x_1 - x_hat_1))
        obj.add(rou / 2 * (self.x_2 - x_hat_2) * (self.x_2 - x_hat_2))
        obj.add(rou / 2 * (self.x_3 - x_hat_3) * (self.x_3 - x_hat_3))

        self.model.setObjective(obj)
        self.model.optimize()

        return (
            self.model.objVal,
            self.x_1.x,
            self.x_2.x,
            self.x_3.x,
        )
