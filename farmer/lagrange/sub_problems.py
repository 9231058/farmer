"""
lagrangian decomposition of the farmer problem
creates the following sub-problems.
"""
from gurobipy import Model

from config import Config


class WheatSubProblem:
    def __init__(self, cfg: Config):
        self.cfg = cfg

        # model.ModelSense is minimization by default
        self.model = Model("wheat_sub_problem")

        self.x_1 = self.model.addVar(ub=self.cfg.area, name="x_1")

        probability = 1 / len(self.cfg.scenarios)
        for index, scenario in enumerate(self.cfg.scenarios):
            self._variables_constraint(index, scenario, probability)

    def _variables_constraint(self, index, scenario, probability):
        y_11 = self.model.addVar(
            name=f"y_11_{index}", obj=self.cfg.wheat.buy_price * probability
        )
        y_12 = self.model.addVar(
            name=f"y_12_{index}", obj=-self.cfg.wheat.sell_price * probability
        )

        self.model.addConstr(
            self.cfg.wheat.requirement
            <= self.x_1 * self.cfg.wheat.produce_rate * (1 + scenario)
            + y_11
            - y_12,
            name="wheat_produce_constraint",
        )

    def solve(self, _lambda):
        self.x_1.obj = _lambda + self.cfg.wheat.plant_cost
        self.model.optimize()

        return (
            self.model.objVal,
            self.x_1.x,
        )


class CornSubProblem:
    def __init__(self, cfg: Config):
        self.cfg = cfg

        # model.ModelSense is minimization by default
        self.model = Model("corn_sub_problem")

        self.x_2 = self.model.addVar(ub=self.cfg.area, name="x_2")

        probability = 1 / len(self.cfg.scenarios)
        for index, scenario in enumerate(self.cfg.scenarios):
            self._variables_constraint(index, scenario, probability)

    def _variables_constraint(self, index, scenario, probability):
        y_21 = self.model.addVar(
            name=f"y_21_{index}", obj=self.cfg.corn.buy_price * probability
        )
        y_22 = self.model.addVar(
            name=f"y_22_{index}", obj=-self.cfg.corn.sell_price * probability
        )

        self.model.addConstr(
            self.cfg.corn.requirement
            <= self.x_2 * self.cfg.corn.produce_rate * (1 + scenario)
            + y_21
            - y_22,
            name="cron_produce_constraint",
        )

    def solve(self, _lambda):
        self.x_2.obj = _lambda + self.cfg.corn.plant_cost
        self.model.optimize()

        return (
            self.model.objVal,
            self.x_2.x,
        )


class BeetSubProblem:
    def __init__(self, cfg: Config):
        self.cfg = cfg

        # model.ModelSense is minimization by default
        self.model = Model("beet_sub_problem")

        self.x_3 = self.model.addVar(ub=self.cfg.area, name="x_3")

        probability = 1 / len(self.cfg.scenarios)
        for index, scenario in enumerate(self.cfg.scenarios):
            self._variables_constraint(index, scenario, probability)

    def _variables_constraint(self, index, scenario, probability):
        y_32 = self.model.addVar(
            ub=self.cfg.beet.max_demand,
            name=f"y_32_{index}",
            obj=-self.cfg.beet.sell_price_high * probability,
        )
        y_33 = self.model.addVar(
            name=f"y_33_{index}",
            obj=-self.cfg.beet.sell_price_low * probability,
        )

        self.model.addConstr(
            self.x_3 * self.cfg.beet.produce_rate * (1 + scenario)
            >= y_32 + y_33,
            name="beet_produce_constraint",
        )

    def solve(self, _lambda):
        self.x_3.obj = _lambda + self.cfg.beet.plant_cost
        self.model.optimize()

        return (
            self.model.objVal,
            self.x_3.x,
        )
