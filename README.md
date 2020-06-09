https://github.com/PyO3/maturin

# Building the wheel

```bash
$ maturin develop --release --strip
$ poetry build
```

OR

```bash
$ maturin build --release --strip
```

# Building the .so library for development

```bash
$ maturin develop
```

# Benchmark

```bash
$ poetry install --no-root
$ maturin develop --release --strip
$ pytest test.py
```

