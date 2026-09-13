from dataclasses import dataclass

import pytest

from brospec import CallableSpec
from brospec.callable_spec import CallableSpecError


@dataclass
class DataSpec:
    a: int
    b: str


my_fn_spec = CallableSpec(
    params={"spec": DataSpec}, returns=list[DataSpec] | list, name="my_fn"
)


def good_fn(spec: DataSpec) -> list[DataSpec] | list:
    return [spec]


def bad_input_fn(spec: str) -> list[DataSpec] | list:
    return [spec]


def bad_output_fn(spec: DataSpec) -> str:
    return "wrong"


class TestDecorator:
    def test_good_function_passes(self):
        decorated = my_fn_spec(good_fn)
        assert decorated(DataSpec(a=1, b="x")) == [DataSpec(a=1, b="x")]

    def test_bad_input_raises(self):
        with pytest.raises(CallableSpecError):
            my_fn_spec(bad_input_fn)

    def test_bad_output_raises(self):
        with pytest.raises(CallableSpecError):
            my_fn_spec(bad_output_fn)


class TestCheck:
    def test_good_function_passes(self):
        assert my_fn_spec.check(good_fn) is good_fn

    def test_bad_input_raises(self):
        with pytest.raises(CallableSpecError):
            my_fn_spec.check(bad_input_fn)

    def test_bad_output_raises(self):
        with pytest.raises(CallableSpecError):
            my_fn_spec.check(bad_output_fn)
