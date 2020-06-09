from datetime import date

from pyxirr import xirr_pure, xirr_rust, xirr_scipy

payments = [
    (date(2015, 6, 11), -1000.0),
    (date(2015, 7, 21), -9000.0),
    (date(2018, 6, 10), 20000.0),
    (date(2015, 10, 17), -3000.0),
]


def test_xirr_pure(benchmark):
    benchmark(xirr_pure, payments)


def test_xirr_rust(benchmark):
    benchmark(xirr_rust, payments)


def test_xirr_scipy(benchmark):
    benchmark(xirr_scipy, payments)
