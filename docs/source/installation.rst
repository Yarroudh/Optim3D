Installation Guide
==================

This guide describes the steps to install Optim3D using `PyPI <https://pypi.org/project/optim3d/>`__ or from source.

Step 1: Install Miniconda
-------------------------

First, you need to install Miniconda, which is a minimal version of
Anaconda. You can download Miniconda from the following link:
https://docs.conda.io/en/latest/miniconda.html

Choose the version that matches your operating system, and follow the
instructions to install it on your system.

Step 2: Install Geoflow-bundle
------------------------------

You need to install **Geoflow-bundle v2022.06.17** to perform the 3D
reconstruction of buildings. You can follow the steps of installation in
the following link: https://github.com/geoflow3d/geoflow-bundle

Once Geoflow-bundle is installed, you can go through the next steps.

Step 3: Create the Conda Environment
------------------------------------

Before installing Optim3D, you need to create a Conda environment by
running the following commands:

.. code:: bash

   conda create --name optimenv python=3.9
   conda activate optimenv
   conda install -c conda-forge pdal python-pdal
   conda install -c conda-forge entwine

This command will create a new Conda environment named optimenv. The
environment uses **Python 3.9** and have the following packages
installed: - Entwine - PDAL - Python-PDAL (Python bindings for PDAL)

Step 4: Install Optim3D
-----------------------

You can install optim3d in your Conda environment by simply running:

.. code:: bash

   pip install optim3d

Or, you can build it from source:

Clone the Repository
~~~~~~~~~~~~~~~~~~~~

Clone the repository of the Optim3D and navigate to its root directory.

.. code:: bash

   git clone https://github.com/Yarroudh/Optim3D/
   cd Optim3D

Install Dependencies
~~~~~~~~~~~~~~~~~~~~

Before installing Optim3D, you should install all the dependencies using
the following command:

.. code:: bash

   pip install -r requirements.txt

Finally, install Optim3D using the setup.py file.

.. code:: bash

   pip install .

This command will install Optim3D and its dependencies in the Conda
environment that you created earlier. These dependencies are : -
click==8.1.8 - geopandas==1.0.1 - osmnx==2.0.1 - rich>=13.9.0

Verify the Installation
~~~~~~~~~~~~~~~~~~~~~~~

Verify that the application is installed correctly by running this
command:

.. code:: bash

   optim3d --help

If the command shows you the following message, the application is
correctly installed in the Conda environment:

.. code:: bash

   Usage: optim3d [OPTIONS] COMMAND [ARGS]...

      CLI tool to manage full optimized reconstruction of large-scale 3D building
      models.

   Options:
      --help  Show this message and exit.

   Commands:
      prepare      Prepare the output folder structure.
      index2d      QuadTree indexing and tiling of 2D building footprints.
      index3d      OcTree indexing of 3D point cloud using Entwine.
      tile3d       Tiling of point cloud using the calculated processing areas.
      reconstruct  Optimized 3D reconstruction of buildings using GeoFlow.
      post         Postprocess the generated CityJSON files.