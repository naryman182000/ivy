"""Collection of Jax gradient functions, wrapped to fit Ivy syntax and signature."""

# global
import jax
import jax.lax as jlax
import jaxlib as jaxlib
from jaxlib.xla_extension import Buffer


# local
import ivy
from ivy.container import Container


# ToDo: modify these functions to track whether variable() has been called
def variable(x):
    return x


def is_variable(x, exclusive=False):
    if exclusive:
        return False
    return isinstance(
        x, (jax.interpreters.xla._DeviceArray, jaxlib.xla_extension.DeviceArray, Buffer)
    )


def variable_data(x):
    return x


def execute_with_gradients(func, xs, retain_grads=False):
    xs = xs.to_native()
    func_ret = func(xs)
    if isinstance(func_ret, tuple):
        y = func_ret[0]
        rest = func_ret[1:]
        grad_fn = lambda x_in: ivy.to_native(ivy.reshape(func(x_in)[0], []))
    else:
        y = func_ret
        rest = tuple()
        grad_fn = lambda x_in: ivy.to_native(ivy.reshape(func(x_in), []))
    grad_func = jax.grad(grad_fn)
    grads = grad_func(xs)
    grads = Container(grads)
    grads = grads.to_ivy()
    if not retain_grads:
        y = ivy.stop_gradient(y)
    return (y, grads, *rest)


def stop_gradient(x, preserve_type=True):
    return jlax.stop_gradient(x)
