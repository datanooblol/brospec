import functools
import inspect
from collections.abc import Callable
from typing import Any, get_type_hints


class CallableSpecError(TypeError):
    """Raised when a callable's signature does not match a CallableSpec contract."""


class CallableSpec:
    """A reusable, portable input/output contract for functions.

    A ``CallableSpec`` describes the expected parameter and return type
    annotations of a function. It can validate a function's signature
    either by wrapping it as a decorator, or by checking an existing
    function directly via :meth:`check` — both paths run the same
    validation logic.

    Attributes:
        params: Mapping of parameter name to its expected type annotation.
        returns: The expected return type annotation.
        name: Optional human-readable name for the contract, used for
            error messages and identification. Defaults to ``"contract"``.

    Example:
        >>> from dataclasses import dataclass
        >>> from brospec import CallableSpec
        >>>
        >>> @dataclass
        ... class DataSpec:
        ...     a: int
        ...     b: str
        >>>
        >>> test_spec = CallableSpec(
        ...     params={"spec": DataSpec},
        ...     returns=list[DataSpec] | list,
        ...     name="my_fn",
        ... )
        >>>
        >>> @test_spec
        ... def good_fn(spec: DataSpec) -> list[DataSpec] | list:
        ...     return [spec]
        >>>
        >>> good_fn(DataSpec(a=1, b="x"))
        [DataSpec(a=1, b='x')]
    """

    def __init__(self, params: dict[str, Any], returns: Any, name: str | None = None):
        """Initialize a CallableSpec contract.

        Args:
            params: Mapping of parameter name to its expected type annotation.
            returns: The expected return type annotation.
            name: Optional human-readable name for the contract. Defaults to
                ``"contract"`` when not provided.
        """
        self.params = params
        self.returns = returns
        self.name = name or "contract"

    def check(self, fn: Callable) -> Callable:
        """Validate a function's signature against this contract.

        Call this on any function, whether or not it is decorated with
        this contract. Useful for validating a function on demand, or
        for asserting that a function fails validation in tests.

        Args:
            fn: The function whose signature will be validated.

        Returns:
            The same function, unchanged, if validation succeeds.

        Raises:
            CallableSpecError: If a required parameter is missing, a
                parameter's type hint does not match the expected type,
                the return type hint does not match, or a type hint
                cannot be resolved.

        Example:
            >>> from dataclasses import dataclass
            >>> from brospec import CallableSpec
            >>>
            >>> @dataclass
            ... class DataSpec:
            ...     a: int
            ...     b: str
            >>>
            >>> test_spec = CallableSpec(
            ...     params={"spec": DataSpec},
            ...     returns=list[DataSpec] | list,
            ...     name="my_fn",
            ... )
            >>>
            >>> def good_fn(spec: DataSpec) -> list[DataSpec] | list:
            ...     return [spec]
            >>> test_spec.check(good_fn) is good_fn
            True
            >>>
            >>> def bad_fn(spec: str) -> list[DataSpec] | list:
            ...     return [spec]
            >>> test_spec.check(bad_fn)
            Traceback (most recent call last):
                ...
            brospec.callable_spec.CallableSpecError: bad_fn: param 'spec' expected <class '...DataSpec'>, got <class 'str'>
        """
        sig = inspect.signature(fn)
        try:
            hints = get_type_hints(fn)
        except NameError as e:
            raise CallableSpecError(f"{fn.__name__}: unresolved type hint ({e})") from e

        for pname, expected in self.params.items():
            if pname not in sig.parameters:
                raise CallableSpecError(f"{fn.__name__}: missing param '{pname}'")
            actual = hints.get(pname)
            if actual != expected:
                raise CallableSpecError(
                    f"{fn.__name__}: param '{pname}' expected {expected}, got {actual}"
                )

        actual_return = hints.get("return")
        if actual_return != self.returns:
            raise CallableSpecError(
                f"{fn.__name__}: expected return {self.returns}, got {actual_return}"
            )
        return fn

    def __call__(self, fn: Callable) -> Callable:
        """Use this contract as a decorator.

        Validates ``fn`` against the contract immediately (at decoration
        time) and returns a wrapper that calls ``fn`` unchanged. The
        contract is attached to both the original function and the
        wrapper via the ``__contract__`` attribute.

        Args:
            fn: The function to decorate and validate.

        Returns:
            A wrapper function that behaves like ``fn`` and carries a
            ``__contract__`` attribute referencing this spec.

        Raises:
            CallableSpecError: If ``fn``'s signature does not match the
                contract (see :meth:`check`).

        Example:
            >>> from dataclasses import dataclass
            >>> from brospec import CallableSpec
            >>>
            >>> @dataclass
            ... class DataSpec:
            ...     a: int
            ...     b: str
            >>>
            >>> test_spec = CallableSpec(
            ...     params={"spec": DataSpec},
            ...     returns=list[DataSpec] | list,
            ...     name="my_fn",
            ... )
            >>>
            >>> @test_spec
            ... def good_fn(spec: DataSpec) -> list[DataSpec] | list:
            ...     return [spec]
            >>> good_fn.__contract__ is test_spec
            True
        """
        self.check(fn)
        fn.__contract__ = self
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)
        wrapper.__contract__ = self
        return wrapper