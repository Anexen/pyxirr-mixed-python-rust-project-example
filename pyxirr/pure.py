from decimal import Decimal
from logging import getLogger


logger = getLogger(__file__)


class ConvergenceFailed(Exception):
    pass


def secant(f, a, b, N, eps_y=1e-6, eps_x=1e-6):
    """Approximate solution of f(x)=0 on interval [a,b] by the secant method.

    Parameters
    ----------
    f : function
        The function for which we are trying to approximate a solution f(x)=0.
    a,b : numbers
        The interval in which to search for a solution. The function returns
        None if f(a)*f(b) >= 0 since a solution is not guaranteed.
    N : (positive) integer
        The number of iterations to implement.

    Returns
    -------
    m_N : number
        The x intercept of the secant line on the the Nth interval
            m_n = a_n - f(a_n)*(b_n - a_n)/(f(b_n) - f(a_n))
        The initial interval [a_0,b_0] is given by [a,b]. If f(m_n) == 0
        for some intercept m_n then the function returns this solution.
        If all signs of values f(a_n), f(b_n) and f(m_n) are the same at any
        iterations, the secant method fails and return None.

    Examples
    --------
    >>> f = lambda x: x**2 - x - 1
    >>> secant(f,1,2,5)
    1.6180257510729614
    """
    if f(a) * f(b) >= 0:
        logger.debug("Secant method fails.")
        return None
    a_n = a
    b_n = b
    prev_m_n = None
    for n in range(1, N + 1):
        f_a_n = f(a_n)
        f_b_n = f(b_n)
        m_n = a_n - f_a_n * (b_n - a_n) / (f_b_n - f_a_n)
        f_m_n = f(m_n)
        if n % 100 == 0:
            logger.debug("Secant iteration %s, delta %s, %s", n, abs(b_n - a_n), m_n)
            if prev_m_n is None:
                prev_m_n = m_n
            elif prev_m_n == m_n:
                raise ConvergenceFailed("secant stalled")
        if abs(b_n - a_n) < eps_x:
            logger.debug("Found solution by eps_x=%f, %d iterations", eps_x, n)
            return m_n
        elif abs(f_m_n) < eps_y:
            logger.debug("Found solution by eps_y=%f, %d iterations", eps_y, n)
            return m_n
        elif f_a_n * f_m_n < 0:
            a_n = a_n
            b_n = m_n
        elif f_b_n * f_m_n < 0:
            a_n = m_n
            b_n = b_n
        else:
            logger.debug("Secant method fails.")
            return None
    # return a_n - f(a_n) * (b_n - a_n) / (f(b_n) - f(a_n))
    logger.debug("Secant method fails.")
    return None


def xnpv(rate, cash_flow, sorted_, already_day_diffs=False):
    """
    Calculate the net present value of a series of cashflows at irregular intervals.
    Arguments
    ---------
    * rate: the discount rate to be applied to the cash flows
    * cashflows: a list object in which each element is a tuple of the form (date, amount), where date is a python datetime.date object or integer diff between dt and dt0 in days and amount is an integer or floating point number. Cash outflows (investments) are represented with negative amounts, and cash inflows (returns) are positive amounts.

    Returns
    -------
    * returns a single value which is the NPV of the given cash flows.
    Notes
    ---------------
    * The Net Present Value is the sum of each of cash flows discounted back to the date of the first cash flow. The discounted value of a given cash flow is A/(1+r)**(t-t0), where A is the amount, r is the discout rate, and (t-t0) is the time in years from the date of the first cash flow in the series (t0) to the date of the cash flow being added to the sum (t).
    * This function is equivalent to the Microsoft Excel function of the same name.
    """

    if not sorted_:
        cash_flow = sorted(cash_flow, key=lambda x: x[0])
    t0 = cash_flow[0][0]  # t0 is the date of the first cash flow
    x = 0.0
    year_days = 365.0
    rate_plus_1 = rate + 1
    last_power = 0
    last_raised = 1
    for item in cash_flow:
        # same as x += item[1] / rate_plus_1 ** ((item[0] - t0).days / year_days)
        if already_day_diffs:
            new_power = (item[0] - t0) / year_days
        else:
            new_power = (item[0] - t0).days / year_days
        last_raised = rate_plus_1 ** (new_power - last_power) * last_raised
        last_power = new_power
        x += item[1] / last_raised
    return x


def xirr(cash_flow, guess=Decimal("0.1"), silent=False):
    """
    Calculate the Internal Rate of Return of a series of cashflows at irregular intervals.
    Arguments
    ---------
    * cashflows: a list object in which each element is a tuple of the form (date, amount),
    where date is a python datetime.date object and amount is an integer or floating point number.
    Cash outflows (investments) are represented with negative amounts, and cash inflows (returns) are positive amounts.
    * guess (optional, default = 0.1): a guess at the solution to be used as a starting point for the numerical solution.
    Returns
    --------
    * Returns the IRR as a single value

    Notes
    ----------------
    * The Internal Rate of Return (IRR) is the discount rate at which the Net Present Value (NPV) of a series of cash flows is equal to zero. The NPV of the series of cash flows is determined using the xnpv function in this module. The discount rate at which NPV equals zero is found using the secant method of numerical solution.
    * This function is equivalent to the Microsoft Excel function of the same name.
    * For users that do not have the scipy module installed, there is an alternate version (commented out) that uses the secant_method function defined in the module rather than the scipy.optimize module's numerical solver. Both use the same method of calculation so there should be no difference in performance, but the secant_method function does not fail gracefully in cases where there is no solution, so the scipy.optimize.newton version is preferred.
    """
    cash_flow = sorted(
        [(dt, float(amount)) for dt, amount in cash_flow], key=lambda t: t[0]
    )
    t0 = cash_flow[0][0]
    cash_flow = [((dt - t0).days, amount) for dt, amount in cash_flow]
    try:
        return secant(lambda r: xnpv(r, cash_flow, True, True), 0.0, 10.0, 2000,)
    except ConvergenceFailed:
        if silent:
            return None
        raise
