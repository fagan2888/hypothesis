from hypothesis.internal.utils.reflection import (
    convert_keyword_arguments,
    get_pretty_function_description,
)
import pytest


def result(f, args, kwargs):
    try:
        return (0, f(*args, **kwargs))
    except Exception as e:
        return (1, e.__class__, e.args)


def do_conversion_test(f, args, kwargs):
    cargs, ckwargs = convert_keyword_arguments(f, args, kwargs)
    assert result(f, args, kwargs) == result(f, cargs, ckwargs)


def test_simple_conversion():
    def foo(a, b, c):
        return (a, b, c)

    assert convert_keyword_arguments(
        foo, (1, 2, 3), {}) == ((1, 2, 3), {})
    assert convert_keyword_arguments(
        foo, (), {'a': 3, 'b': 2, 'c': 1}) == ((3, 2, 1), {})

    do_conversion_test(foo, (1, 0), {'c': 2})
    do_conversion_test(foo, (1,), {'c': 2, 'b': "foo"})


def test_populates_defaults():
    def bar(x=[], y=1):
        pass

    assert convert_keyword_arguments(bar, (), {}) == (([], 1), {})
    assert convert_keyword_arguments(bar, (), {'y': 42}) == (([], 42), {})
    do_conversion_test(bar, (), {})
    do_conversion_test(bar, (1,), {})


def test_leaves_unknown_kwargs_in_dict():
    def bar(x, **kwargs):
        pass

    assert convert_keyword_arguments(bar, (1,), {'foo': 'hi'}) == (
        (1,), {'foo': 'hi'}
    )
    assert convert_keyword_arguments(bar, (), {'x': 1, 'foo': 'hi'}) == (
        (1,), {'foo': 'hi'}
    )
    do_conversion_test(bar, (1,), {})
    do_conversion_test(bar, (), {'x': 1, 'y': 1})


def test_errors_on_bad_kwargs():
    def bar():
        pass    # pragma: no cover

    with pytest.raises(TypeError):
        convert_keyword_arguments(bar, (), {"foo": 1})


def test_passes_varargs_correctly():
    def foo(*args):
        pass

    assert convert_keyword_arguments(foo, (1, 2, 3), {}) == ((1, 2, 3), {})

    do_conversion_test(foo, (1, 2, 3), {})


def test_errors_if_keyword_precedes_positional():
    def foo(x, y):
        pass  # pragma: no cover
    with pytest.raises(TypeError):
        convert_keyword_arguments(foo, (1,), {'x': 2})


def test_errors_if_not_enough_args():
    def foo(a, b, c, d=1):
        pass  # pragma: no cover

    with pytest.raises(TypeError):
        convert_keyword_arguments(foo, (1, 2), {'d': 4})


def test_errors_on_extra_kwargs():
    def foo(a):
        pass  # pragma: no cover

    with pytest.raises(TypeError) as e:
        convert_keyword_arguments(foo, (1,), {'b': 1})
    assert 'keyword' in e.value.args[0]

    with pytest.raises(TypeError) as e2:
        convert_keyword_arguments(foo, (1,), {'b': 1, 'c': 2})
    assert 'keyword' in e2.value.args[0]


def destructure_my_arguments((a, b), c):
    return a, b, c


def test_can_handle_destructuring_functions():
    do_conversion_test(
        destructure_my_arguments,
        ((1, 2,),), {'c': 3})
    do_conversion_test(
        destructure_my_arguments,
        ((1, 2,), 3), {})


def test_names_of_functions_are_pretty():
    assert get_pretty_function_description(
        test_names_of_functions_are_pretty
    ) == 'test_names_of_functions_are_pretty'


class Foo(object):
    @classmethod
    def bar(cls):
        pass  # pragma: no cover

    def baz(cls):
        pass  # pragma: no cover

    def __repr__(self):
        return "SoNotFoo()"


def test_class_names_are_included_in_class_method_prettiness():
    assert get_pretty_function_description(Foo.bar) == 'Foo.bar'


def test_repr_is_included_in_bound_method_prettiness():
    assert get_pretty_function_description(Foo().baz) == 'SoNotFoo().baz'


def test_source_of_lambda_is_pretty():
    assert get_pretty_function_description(lambda x: True) == 'lambda x: True'


def test_variable_names_are_not_pretty():
    t = lambda x: True
    assert get_pretty_function_description(t) == 'lambda x: True'


def test_does_not_error_on_dynamically_defined_functions():
    x = eval('lambda t: 1')
    get_pretty_function_description(x)
