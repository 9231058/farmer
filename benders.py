import math

from gurobipy import GRB, Model, LinExpr

BIG_M = 100 * 100 * 100

scenarios = [0.2, 0, -0.2]

EPSILON = 0.01

AREA = 500

WHEAT_COST = 150
WHEAT_PRODUCE = 2.5
WHEAT_REQUIREMENT = 200
WHEAT_BUY_PRICE = 238
WHEAT_SELL_PRICE = 170

CORN_COST = 230
CORN_PRODUCE = 3
CORN_REQUIREMENT = 240
CORN_BUY_PRICE = 210
CORN_SELL_PRICE = 150

BEET_COST = 260
BEET_PRODUCE = 20
BEET_MAX_DEMAND = 6000
BEET_SELL_PRICE_LOW = 10
BEET_SELL_PRICE_HIGH = 36


class MasterProblem:
    def __init__(self):
        self.model = Model("benders_master_porblem")

        self.x_1 = self.model.addVar(vtype=GRB.CONTINUOUS, lb=0, name="x_1")
        self.x_2 = self.model.addVar(vtype=GRB.CONTINUOUS, lb=0, name="x_2")
        self.x_3 = self.model.addVar(vtype=GRB.CONTINUOUS, lb=0, name="x_3")

        self.phi = self.model.addVar(
            vtype=GRB.CONTINUOUS, lb=-100 * 100 * 100, name="phi"
        )

        self.model.addConstr(
            self.x_1 + self.x_2 + self.x_3 <= AREA, name="area_constraint"
        )

        self.model.setObjective(
            self.x_1 * WHEAT_COST
            + self.x_2 * CORN_COST
            + self.x_3 * BEET_COST
            + self.phi,
            GRB.MINIMIZE,
        )

    def add_cut(self, lhs, pi_1, pi_2, pi_3):
        """
        add_cut adds new cuts to master problem based
        on given dual values and constant.
        these parameters come from the sub problem
        optimal solution in each benders iteration.
        """
        self.model.addConstr(
            lhs
            <= self.phi - self.x_1 * pi_1 - self.x_2 * pi_2 - self.x_3 * pi_3,
            name="cut",
        )

    def solve(self):
        """
        solve solves master problem and returns the optimal solution
        """
        self.model.optimize()

        return (
            self.model.objVal,
            self.x_1.x,
            self.x_2.x,
            self.x_3.x,
        )


class SubProblem:
    def __init__(self):
        self.model = Model("benders_sub_porblem")

        self.x_1 = self.model.addVar(vtype=GRB.CONTINUOUS, lb=0, name="x_1")
        self.x_2 = self.model.addVar(vtype=GRB.CONTINUOUS, lb=0, name="x_2")
        self.x_3 = self.model.addVar(vtype=GRB.CONTINUOUS, lb=0, name="x_3")

        self.objective = LinExpr()

        probability = 1 / len(scenarios)
        for index, scenario in enumerate(scenarios):
            self._wheat_variables_constraint(index, scenario, probability)
            self._corn_variables_constraint(index, scenario, probability)
            self._beet_variables_constraints(index, scenario, probability)

        self.model.setObjective(self.objective, GRB.MINIMIZE)

    def solve(self, x_1, x_2, x_3):
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
            WHEAT_REQUIREMENT
            <= self.x_1 * WHEAT_PRODUCE * (1 + scenario) + y_11 - y_12 + v_1,
            name="wheat_produce_constraint",
        )

        self.objective.add(y_11 * WHEAT_BUY_PRICE * probability)
        self.objective.add(y_12 * -WHEAT_SELL_PRICE * probability)
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
            CORN_REQUIREMENT
            <= self.x_2 * CORN_PRODUCE * (1 + scenario) + y_21 - y_22 + v_2,
            name="corn_produce_constraint",
        )

        self.objective.add(y_21 * CORN_BUY_PRICE * probability)
        self.objective.add(y_22 * -CORN_SELL_PRICE * probability)
        self.objective.add(v_2 * BIG_M)

    def _beet_variables_constraints(self, index, scenario, probability):
        y_32 = self.model.addVar(
            vtype=GRB.CONTINUOUS,
            lb=0,
            ub=BEET_MAX_DEMAND,
            name=f"y_32_{index}",
        )
        y_33 = self.model.addVar(
            vtype=GRB.CONTINUOUS, lb=0, name=f"y_33_{index}"
        )
        v_3 = self.model.addVar(
            vtype=GRB.CONTINUOUS, lb=0, name=f"v_3_{index}"
        )

        self.model.addConstr(
            self.x_3 * BEET_PRODUCE * (1 + scenario) - y_32 - y_33 + v_3 >= 0,
            name="beet_produce_constraint",
        )

        self.objective.add(y_32 * -BEET_SELL_PRICE_HIGH * probability)
        self.objective.add(y_33 * -BEET_SELL_PRICE_LOW * probability)
        self.objective.add(v_3 * BIG_M)


def main():
    iterations = {
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

    master_problem = MasterProblem()
    k = 0

    while True:
        k += 1
        iterations["k"].append(k)

        z_lb, x_1, x_2, x_3 = master_problem.solve()

        iterations["x_1"].append(x_1)
        iterations["x_2"].append(x_2)
        iterations["x_3"].append(x_3)
        iterations["z_lb"].append(z_lb)

        z_star, pi_1, pi_2, pi_3 = SubProblem().solve(x_1, x_2, x_3)
        z_ub = z_star + WHEAT_COST * x_1 + CORN_COST * x_2 + BEET_COST * x_3

        iterations["pi_1"].append(pi_1)
        iterations["pi_2"].append(pi_2)
        iterations["pi_3"].append(pi_3)
        iterations["z_ub"].append(z_ub)

        if math.isclose(z_lb, z_ub, abs_tol=EPSILON):
            return iterations

        master_problem.add_cut(
            z_star - pi_1 * x_1 - pi_2 * x_2 - pi_3 * x_3, pi_1, pi_2, pi_3
        )


if __name__ == "__main__":
    main()
