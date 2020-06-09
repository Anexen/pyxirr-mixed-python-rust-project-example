from xirr.math import xirr
from .pyxirr import xirr_rust
from .pure import xirr as xirr_pure


__all__ = ["xirr_rust", "xirr_scipy", "xirr_pure"]


def xirr_scipy(payments):
    return xirr(dict(payments))
