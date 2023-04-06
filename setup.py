from setuptools import setup, find_packages

with open("requirements.txt", "r") as file:
    requirements = file.read().splitlines()

setup(
    name="optim3d",
    version='0.1.7',
    description="CLI application for efficient and optimized reconstruction of large-scale 3D building models",
    author = 'Anass Yarroudh',
    author_email = 'ayarroudh@uliege.be',
    url = 'https://github.com/Yarroudh/Optim3D',
    packages=find_packages(),
    py_modules=["optim3d"],
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "optim3d=optim3d.main:cli"
        ]
    },
     package_data={
        "optim3d": ["config/*.json"],
    }
)
