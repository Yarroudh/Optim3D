# Installation Guide
This guide describes the steps to install Optim3D from source.

## Step 1: Install Miniconda
First, you need to install Miniconda, which is a minimal version of Anaconda. You can download Miniconda from the following link: https://docs.conda.io/en/latest/miniconda.html

Choose the version that matches your operating system, and follow the instructions to install it on your system.

## Step 2: Install Geoflow-bundle
You need to install Geoflow-bundle to perform the 3D reconstruction of buildings. You can follow the steps of installation in the following link:
https://github.com/geoflow3d/geoflow-bundle

## Step 3: Clone the Repository
Clone the repository of the Optim3D and navigate to its root directory.

```bash
git clone https://github.com/Yarroudh/Optim3D/
cd Optim3D
```

## Step 4: Create the Conda Environment
Before installing Optim3D, you need to create a Conda environment using the <code>environment.yaml</code> file provided in the repository.

```bash
conda env create -f environment.yaml
```

This command will create a new Conda environment with the name specified in the <code>environment.yaml</code> file. The environment uses **Python 3.6.13** and have the following packages installed:
- Entwine
- PDAL
- Python-PDAL (Python bindings for PDAL)

## Step 5: Activate the Conda Environment
Activate the Conda environment that you created in the previous step.

```bash
conda activate optimenv
```

## Step 6: Install the Python Application
Finally, install the Python application using the <code>setup.py</code> file.

```bash
python setup.py install
```

This command will install Optim3D and its dependencies in the Conda environment that you created earlier. These dependencies are :
- click==8.0.4
- geopandas==0.9.0
- osmnx==0.11.3
- shapely==1.6.0

## Step 7: Verify the Installation

Verify that the application is installed correctly by running this command:

```bash
optim3d --help
```

If the command shows you the following message, the application is installed correctly in the Conda environment:

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
