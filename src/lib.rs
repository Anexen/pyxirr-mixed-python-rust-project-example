use chrono::NaiveDate;
use pyo3::prelude::*;
use pyo3::types::{PyDate, PyDateAccess, PyList};
use pyo3::{create_exception, exceptions, wrap_pyfunction};
use xirr::{self, Payment};

create_exception!(pyxirr, InvalidPaymentsError, exceptions::Exception);

#[pyfunction]
fn xirr_rust(py_payments: &PyList) -> PyResult<f64> {
    let mut payments = Vec::with_capacity(py_payments.len());

    for py_elem in py_payments.into_iter() {
        let date = py_elem.get_item(0).unwrap().extract::<&PyDate>()?;
        let amount = py_elem.get_item(1).unwrap().extract::<f64>()?;

        payments.push(Payment {
            date: NaiveDate::from_ymd(
                date.get_year(),
                date.get_month() as u32,
                date.get_day() as u32,
            ),
            amount: amount,
        });
    }

    let res = xirr::compute(&payments);

    match res {
        Err(e) => Err(InvalidPaymentsError::py_err(e.to_string())),
        Ok(v) => Ok(v),
    }
}

#[pymodule]
/// A Python module implemented in Rust.
fn pyxirr(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_wrapped(wrap_pyfunction!(xirr_rust))?;

    Ok(())
}
