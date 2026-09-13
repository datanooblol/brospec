# brospec

The only spec validation library you'll ever need, quick and simple.

bro's goal:

- one place for all your spec validations, no scattering them around
- reusable, so you write the contract once and reuse it everywhere
- lightweight and python native, no bloat, no extra deps
- built to plug into the rest of the bro libraries: brollm, broflow, broskill and whatever else shows up down the road

Real talk on why this exists: I kept running into the same annoying chore — hand-rolling a callable spec every time I needed to validate a function/method before wiring it into one of my bro libs. A pattern I use a lot is a base class with a method that lets users bring their own function and hand it in at instantiation. Gotta make sure whatever they pass actually takes the right inputs and gives back the right output, otherwise the whole lib breaks downstream. Since I keep reaching for this same pattern, it made sense to rip the validation logic out into its own little lib instead of copy-pasting it forever.

Sure, you could roll your own. But why bother when this is right here? Grab it, skip the boilerplate, go spend your energy on the actually hard stuff.

## What's available now

- **CallableSpec** — validates a function/method's input and return type hints against a reusable contract. Use it as a decorator, or run it on demand with `.check()`.

More specs are coming as we figure out what's actually worth building. Check [VERSIONS.md](VERSIONS.md) for the timeline.

## CallableSpec

- validates your function/method's inputs and return type.
- keeps your base function as just a skeleton, so users can bring their own function and plug it in, no worries about it breaking your contract.

Check [examples/example1.py](examples/example1.py)

```python
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
```
