try:
    from setuptools import setup

except ImportError:
    from distutils.core import setup
    
setup(
    name="optim3d",
    version='0.2.0',
    description="CLI application for efficient and optimized reconstruction of large-scale 3D building models",
    packages=["src"]
    install_requires=reqs
    entry_points='''
        [console_scripts]
        optim3d=src.optim3d:cli
    ''',
)
