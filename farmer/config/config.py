import dataclasses
import typing


@dataclasses.dataclass
class RequiredSeed:
    """
    RequiredSeed is a seed that farmer requires it
    """

    plant_cost: int
    produce_rate: float
    requirement: int
    buy_price: int
    sell_price: int


@dataclasses.dataclass
class NonrequiredSeed:
    """
    Nonrequired is a seed that farmer plant just for selling it
    """

    plant_cost: int
    produce_rate: float
    max_demand: int
    sell_price_low: int
    sell_price_high: int


@dataclasses.dataclass
class Config:
    """
    Config contains the configuration of farmer problem
    """

    scenarios: typing.List[float] = [0.2, 0, -0.2]

    area: int = 500

    wheat: RequiredSeed = RequiredSeed(150, 2.5, 200, 238, 170)
    corn: RequiredSeed = RequiredSeed(230, 3, 240, 210, 150)

    beet: NonrequiredSeed = NonrequiredSeed(260, 20, 6000, 10, 36)
