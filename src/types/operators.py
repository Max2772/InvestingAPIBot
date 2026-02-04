import operator
from typing import Dict

operators: Dict[str, operator] = {
    ">": operator.gt,
    ">=": operator.ge,
    "<": operator.lt,
    "<=": operator.le
}
