from setuptools import setup, find_packages

setup(
    name="optim3d",
    version='0.2.0',
    description="CLI application for efficient and optimized reconstruction of large-scale 3D building models",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "optim3d=src.optim3d:cli"
        ]
    }
)
