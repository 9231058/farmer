from config import Config
from gurobipy import GRB, Model, LinExpr

BIG_M = 100 * 100 * 100


class SubProblem:
    def __init__(self, cfg: Config):
        self.model = Model("benders_sub_porblem")
        self.cfg = cfg

        self.x_1 = self.model.addVar(vtype=GRB.CONTINUOUS, lb=0, name="x_1")
        self.x_2 = self.model.addVar(vtype=GRB.CONTINUOUS, lb=0, name="x_2")
        self.x_3 = self.model.addVar(vtype=GRB.CONTINUOUS, lb=0, name="x_3")

        self.objective = LinExpr()

        probability = 1 / len(self.cfg.scenarios)
        for index, scenario in enumerate(self.cfg.scenarios):
            self._wheat_variables_constraint(index, scenario, probability)
            self._corn_variables_constraint(index, scenario, probability)
            self._beet_variables_constraints(index, scenario, probability)

        self.model.setObjective(self.objective, GRB.MINIMIZE)

    def solve(self, x_1, x_2, x_3):
        """
        Solve the sub problem with given values for xs.
        """
        x_hat_1 = self.model.addConstr(self.x_1 == x_1, name="x_hat_1")
        x_hat_2 = self.model.addConstr(self.x_2 == x_2, name="x_hat_2")
        x_hat_3 = self.model.addConstr(self.x_3 == x_3, name="x_hat_3")

        self.model.optimize()

        return (
            self.model.objVal,
            x_hat_1.pi,
            x_hat_2.pi,
            x_hat_3.pi,
        )

    def _wheat_variables_constraint(self, index, scenario, probability):
        y_11 = self.model.addVar(
            vtype=GRB.CONTINUOUS, lb=0, name=f"y_11_{index}"
        )
        y_12 = self.model.addVar(
            vtype=GRB.CONTINUOUS, lb=0, name=f"y_12_{index}"
        )
        v_1 = self.model.addVar(
            vtype=GRB.CONTINUOUS, lb=0, name=f"v_1_{index}"
        )

        self.model.addConstr(
            self.cfg.wheat.requirement
            <= self.x_1 * self.cfg.wheat.produce_rate * (1 + scenario)
            + y_11
            - y_12
            + v_1,
            name="wheat_produce_constraint",
        )

        self.objective.add(y_11 * self.cfg.wheat.buy_price * probability)
        self.objective.add(y_12 * -self.cfg.wheat.sell_price * probability)
        self.objective.add(v_1 * BIG_M)

    def _corn_variables_constraint(self, index, scenario, probability):
        y_21 = self.model.addVar(
            vtype=GRB.CONTINUOUS, lb=0, name=f"y_21_{index}"
        )
        y_22 = self.model.addVar(
            vtype=GRB.CONTINUOUS, lb=0, name=f"y_22_{index}"
        )
        v_2 = self.model.addVar(
            vtype=GRB.CONTINUOUS, lb=0, name=f"v_2_{index}"
        )

        self.model.addConstr(
            self.cfg.corn.requirement
            <= self.x_2 * self.cfg.corn.produce_rate * (1 + scenario)
            + y_21
            - y_22
            + v_2,
            name="corn_produce_constraint",
        )

        self.objective.add(y_21 * self.cfg.corn.buy_price * probability)
        self.objective.add(y_22 * -self.cfg.corn.sell_price * probability)
        self.objective.add(v_2 * BIG_M)

    def _beet_variables_constraints(self, index, scenario, probability):
        y_32 = self.model.addVar(
            vtype=GRB.CONTINUOUS,
            lb=0,
            ub=self.cfg.beet.max_demand,
            name=f"y_32_{index}",
        )
        y_33 = self.model.addVar(
            vtype=GRB.CONTINUOUS, lb=0, name=f"y_33_{index}"
        )
        v_3 = self.model.addVar(
            vtype=GRB.CONTINUOUS, lb=0, name=f"v_3_{index}"
        )

        self.model.addConstr(
            self.x_3 * self.cfg.beet.produce_rate * (1 + scenario)
            - y_32
            - y_33
            + v_3
            >= 0,
            name="beet_produce_constraint",
        )

        self.objective.add(y_32 * -self.cfg.beet.sell_price_high * probability)
        self.objective.add(y_33 * -self.cfg.beet.sell_price_low * probability)
        self.objective.add(v_3 * BIG_M)
