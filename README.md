# Farmer
## Introduction
A farmer wants to plat a field that has specific area (500 m^2). He can plant wheat, corn and beet but he must decide on how much
he wants to use from his field for each of them. He cannot predict weather so after the planting the crops weight is unknown.
He knows the all scenarios that may happens in advance so he want to solve an stochastic programming model to
maximize his profit or minimize his costs.

He has requirements for wheat and corn and if these requirements are unmeet he must buy the them.
There is no requirement for beet and all of it will sell. But there is an specific demand for beet
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

We write the problem with Here-and-Now formulation so it gets huge with number of scenarios increase.

This problem can have an integer format. In the integer format farmer can only sell or buy crops in 1000kg packages.
