from dataclasses import dataclass
from brospec import CallableSpec
from typing import Callable

@dataclass
class DataSpec:
    a: int
    b: str

class MyClass:
    def __init__(self, diy_fn: Callable):
        self.diy_fn = diy_fn

    def diy_method(self, spec: DataSpec) -> list[DataSpec] | list:
        # this diy_fn allows only one argument as spec with DataSpec type
        # and it will return only list of DataSpec or empty list
        return self.diy_fn(spec=spec)

if __name__=="__main__":
    my_fn_spec = CallableSpec(params={"spec": DataSpec}, returns=list[DataSpec] | list, name="my_fn")

    # decoration type
    @my_fn_spec
    def decorator_good_fn(spec: DataSpec) -> list[DataSpec] | list:
        return [spec]

    def normal_good_fn(spec: DataSpec) -> list[DataSpec] | list:
        return [spec]

    # normal .check type
    my_fn_spec.check(normal_good_fn)
    # it's supposed to pass.