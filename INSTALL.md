# Installation Guide
This guide describes the steps to install Optim3D using [PyPI](https://pypi.org/project/optim3d/) or from source.

## Step 1: Install Miniconda
First, you need to install Miniconda, which is a minimal version of Anaconda. You can download Miniconda from the following link: https://docs.conda.io/en/latest/miniconda.html

Choose the version that matches your operating system, and follow the instructions to install it on your system.

## Step 2: Install Geoflow-bundle
You need to install **Geoflow-bundle v2022.06.17** to perform the 3D reconstruction of buildings. You can follow the steps of installation in the following link:
https://github.com/geoflow3d/geoflow-bundle

Once Geoflow-bundle is installed, you can go through the next steps.

## Step 3: Create the Conda Environment
Before installing Optim3D, you need to create a Conda environment by running the following commands:

```bash
conda create --name optimenv python=3.6.13
conda activate optimenv
conda install -c conda-forge pdal python-pdal
conda install -c conda-forge entwine
```

This command will create a new Conda environment named <code>optimenv</code>. The environment uses **Python 3.6.13** and have the following packages installed:
- Entwine
- PDAL
- Python-PDAL (Python bindings for PDAL)

In case the installation of dependencies using <code>conda</code> is taking too much time, an alternative option is to use <code>Mamba</code> as a package manager. Mamba is a faster and more efficient package manager than Conda, particularly when it comes to installation, updates, and dependency resolution. This is because Mamba is written in C++ and uses multithreading to parallelize operations, whereas Conda is written in Python and does not take advantage of multiple cores as effectively.

Mamba can be used in a similar way to Conda for creating and managing Conda environments:

```bash
conda create --name optimenv python=3.6.13
conda activate optimenv
conda install mamba -c conda-forge
mamba install pdal python-pdal -c conda-forge
mamba install entwine -c conda-forge
```

## Step 4: Install Optim3D

You can install <code>optim3d</code> in your Conda environment by simply running:

```bash
pip install optim3d
```

Or, you can build it from source:

### Clone the Repository
Clone the repository of the Optim3D and navigate to its root directory.

```bash
git clone https://github.com/Yarroudh/Optim3D/
cd Optim3D
```

### Install Dependencies
Before installing Optim3D, you should install all the dependencies using the following command:

```bash
pip install -r requirements.txt
```

Finally, install Optim3D using the <code>setup.py</code> file.

```bash
pip install -e .
```

This command will install Optim3D and its dependencies in the Conda environment that you created earlier. These dependencies are :
- click==8.0.4
- geopandas==0.9.0
- osmnx==0.11.3
- shapely==1.6.0

### Verify the Installation

Verify that the application is installed correctly by running this command:

```bash
optim3d --help
```

If the command shows you the following message, the application is correctly installed in the Conda environment:

```bash
Usage: optim3d [OPTIONS] COMMAND [ARGS]...

  CLI tool to manage full optimized reconstruction of large-scale 3D
  building models.

Options:
  --help  Show this message and exit.

Commands:
  index2d      QuadTree indexing and tiling of 2D building footprints.
  index3d      OcTree indexing of 3D point cloud using Entwine.
  tiler3d      Tiling of point cloud using the calculated processing areas.
  reconstruct  Optimized 3D reconstruction of buildings using GeoFlow.
  post         Post-processing generated CityJSON files.
```
