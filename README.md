# Farmer
## Introduction
A farmer wants to plant a field that is 500 m^2. He can plant wheat, corn and beet but he must decide on how much
he wants to use his field for each of them. He cannot predict weather so after planting, the crops weight is unknown.
He knows the all scenarios that may happen in advance so he wants to solve a stochastic programming model to
maximize his profit or minimize his costs.

He has requirements for wheat and corn and if these requirements are unmeet he must buy them.
There is no requirement for beet and all of it will be sold. But there is an specific demand for beet
and extra of it will be sold in much lower price.

In a normal year we have the following rates for each seed:

| Seed  | Rate |
|:----- |:----:|
| Wheat | 2.5  |
| Corn  | 3    | 
| Beet  | 20   |

and we have the following scenarios:

| index | proportion |
|:-----:|:----------:|
| 0     | 1 + 0.2    |
| 1     | 1          |
| 2     | 1 - 0.2    |

We write the problem with Here-and-Now formulation so the more the number of scenarios, the huge the problem become.

This problem can have an integer format. In the integer format the farmer can only sell or buy crops in 1000kg packages.

## Up and Running
This project is based on awesome [gurobi](https://www.gurobi.com/) python interface so first of all you need to instal it.
Then use the following commands:

```sh
poetry shell
cd $GUROBI_HOME
python3 setup.py install
cd -
poetry install
```
