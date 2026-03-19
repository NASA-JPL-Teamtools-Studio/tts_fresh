# FRESH Developer Docs

## Developer Installation

To install in editable mode with developer dependencies, create/activate a virtual environment and use the `dev` optional dependency identifier:

```
python3 -m pip install -e .[dev]
```

If you get a "No match" error, try installing without the `dev` identifier:

```
python3 -m pip install -e .
```

...and manually install the dev dependencies listed in [`setup.cfg`](../setup.cfg).

## Testing

Tests are built and invoked with `pytest`.

## Packaging and Distribution

Use `build` to package `mm-fresh` for distribution:

```
python3 -m build
```
