from config import Config
from gurobipy import GRB, Model, LinExpr


class MasterProblem:
    """
    Benders's master problem.
    In each iteration a new cut will be added into this.
    """

    def __init__(self, cfg: Config):
        self.model = Model("benders_master_porblem")
        self.cfg = cfg

        self.x_1 = self.model.addVar(vtype=GRB.CONTINUOUS, lb=0, name="x_1")
        self.x_2 = self.model.addVar(vtype=GRB.CONTINUOUS, lb=0, name="x_2")
        self.x_3 = self.model.addVar(vtype=GRB.CONTINUOUS, lb=0, name="x_3")

        self.phi = self.model.addVar(
            vtype=GRB.CONTINUOUS, lb=-100 * 100 * 100, name="phi"
        )

        self.model.addConstr(
            self.x_1 + self.x_2 + self.x_3 <= cfg.area, name="area_constraint"
        )

        self.model.setObjective(
            self.x_1 * cfg.wheat.plant_cost
            + self.x_2 * cfg.corn.plant_cost
            + self.x_3 * cfg.beet.plant_cost
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
