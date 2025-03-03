from setuptools import setup

setup(
    name="stockalpha",
    version="0.1",
    packages=["stockalpha"],
    package_dir={"stockalpha": "src/stockalpha"},
    # Register the mypy plugin
    entry_points={
        "mypy.plugins": [
            "stockalpha_mypy_plugin = stockalpha.mypy_plugin:plugin",
        ],
    },
)
