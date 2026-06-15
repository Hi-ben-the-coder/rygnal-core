use pyo3::prelude::*;

/// A simple tracer bullet function to prove Python -> Rust execution.
#[pyfunction]
fn verify_bridge(payload: String) -> PyResult<String> {
    Ok(format!(
        "[Rust Kernel]: Connection secure. Received payload -> {}",
        payload
    ))
}

/// Python module exposed by the compiled Rust extension.
#[pymodule]
fn rygnal_kernel(_py: Python, module: &PyModule) -> PyResult<()> {
    module.add_function(wrap_pyfunction!(verify_bridge, module)?)?;
    Ok(())
}
