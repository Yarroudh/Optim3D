<img src="https://github.com/Yarroudh/templates_cj/assets/72500344/1b523bfa-b0d4-46d6-9400-69bc1c81fe90" alt="logo" width="200"/>

**Paper is now published. For more information, please refer to: [Recent Advances in 3D Geoinformation Science](https://link.springer.com/chapter/10.1007/978-3-031-43699-4_50)**

# Optim3D: Efficient and scalable generation of large-scale 3D building

[![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://github.com/Yarroudh/ZRect3D/blob/main/LICENSE)
[![GeoScITY - Dev](https://img.shields.io/badge/GeoScITY-Dev-2ea44f)](https://www.geoscity.uliege.be)
[![Springer](https://img.shields.io/badge/Springer-10.1007/978--3--031--43699--4_50-green?style=flat&link=https://doi.org/10.1007/978-3-031-43699-4_50)](https://doi.org/10.1007/978-3-031-43699-4_50)

*Command-Line Interface (CLI) application for efficient and optimized reconstruction of large-scale 3D building models.*

Optim3D is a powerful tool for efficient and scalable generation of highly detailed and large-scale 3D building models. The modeling process is based on [GeoFlow](https://github.com/geoflow3d/geoflow-bundle). The tool focuses mainly on preparing data for efficient reconstruction through indexing, tiling and parallel computing, which significantly reduces the processing time and resources required to generate large-scale 3D building models.

<img src="https://user-images.githubusercontent.com/72500344/212364590-b7fd444d-ec26-4a8b-bda9-fd4e1669bc6e.png" alt="Workflow of 3D Reconstruction" width="500"/>

## Documentation

If you are using Optim3D, we highly recommend that you take the time to read the [documentation](https://optim3d.readthedocs.io/en/latest/).

## Installation

**NOTE:** Before installing <code>Optim3D</code>. It is important to have [GeoFlow-bundle](https://github.com/geoflow3d/geoflow-bundle/releases/tag/2022.06.17) installed on your machine. Please read the LICENSE file of <code>Geoflow-bundle</code> before usage.

### Requirements

- Python >= 3.9
- PDAL >= 2.4.0
- Entwine >= 3.1.0
- Geoflow-bundle >= 2022.06.17
- click >= 8.0.1
- geopandas >= 1.0.1
- osmnx >= 2.0.1
- rich >= 13.9.0

### Download from PyPI

You can install optim3d in your Conda environment by running the following commands:

```bash
conda create --name optimenv python==3.9
conda activate optimenv
conda install -c conda-forge pdal python-pdal
conda install -c conda-forge entwine
pip install optim3d
```

If conda is not installed on your machine, you can install it by following the instructions on the [official website](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html).

If installing PDAL and Python-PDAL is slow, you can use [Mamba](https://mamba.readthedocs.io/en/latest/) as a package manager. Mamba is a faster and more efficient package manager than Conda, particularly when it comes to installation, updates and dependency resolution. This is because Mamba is written in C++ and uses multithreading to parallelize operations, whereas Conda is written in Python and does not take advantage of multiple cores as effectively.

Mamba can be used in a similar way to Conda for creating and managing Conda environments:

```bash
conda create --name optimenv python=3.9
conda activate optimenv
conda install mamba -c conda-forge
mamba install pdal python-pdal -c conda-forge
mamba install entwine -c conda-forge
pip install optim3d
```

### Building from source

You can also build everything from source (see [INSTALL.md](https://github.com/Yarroudh/Optim3D/blob/main/INSTALL.md)). A [Docker image](https://hub.docker.com/r/yarroudh/optim3d) is also available.

## Quick Start

### Usage

After installation, you have a small program called <code>optim3d</code>. Use <code>optim3d --help</code> to see the detailed help:

```
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
```

The process consists of six steps or <code>commands</code> that must be executed in a specific order to achieve the desired outcome.

#### Step 1 : Prepare the output folder structure

Before starting the 3D reconstruction process, it is necessary to prepare the output folder structure. This is done using the first command <code>prepare</code>. Use <code>optim3d prepare --help</code> to see the detailed help:

```
Usage: optim3d prepare [OPTIONS]

  Prepare the output folder structure.

Options:
  --output PATH              Output directory.  [default: output]
  --footprint_tiles PATH     Footprint tiles directory.  [default:
                             footprint_tiles]
  --indexed_pointcloud PATH  Indexed pointcloud directory.  [default:
                             indexed_pointcloud]
  --model PATH               Model directory.  [default: model]
  --pointcloud_tiles PATH    Pointcloud tiles directory.  [default:
                             pointcloud_tiles]
  --folder_structure PATH    Folder structure file.  [default:
                             folder_structure.xml]
  --help                     Show this message and exit.
```

For example, you can use the following command to prepare the output folder structure:

```bash
optim3d prepare
```

This command will create the following folder structure in the <code>output</code> folder:

```bash
├── output
│   ├── footprint_tiles
│   ├── indexed_pointcloud
│   ├── model
│   ├── pointcloud_tiles
│   └── folder_structure.xml
```

You can specify the output folder using the <code>--output</code> option. For example, to save the results in the <code>results</code> folder, use the following command:

```bash
optim3d prepare --output results
```

The file <code>folder_structure.xml</code> contains the structure of the output folder. You can modify it according to your needs, but it is recommended to keep the default structure.

#### Step 2 : 2D building footprints indexing and tiling

Quadtree-based tiling scheme is used for spatial partitioning of building footprints. This assures that the reconstruction time per tile is more or less the same and that the tiles available for download are similar in file size. This is done using the first command <code>index2d</code>. Use <code>optim3d index2d --help</code> to see the detailed help:

```
Usage: optim3d index2d [OPTIONS] [FOOTPRINTS]

  QuadTree indexing and tiling of 2D building footprints.

Options:
  --output PATH                   Output directory.  [default: output]
  --folder-structure PATH         Folder structure file.  [default:
                                  folder_structure.xml]
  --osm ('WEST', 'NORTH', 'EAST', 'SOUTH')
                                  Download footprints from OSM in [west north
                                  east south] format.  [default: -1, -1, -1,
                                  -1]
  --osm-save-path PATH            Path to save downloaded OSM footprints
                                  (optional).
  --quadtree-fname PATH           Filename for the QuadTree file (forced to
                                  GPKG format).  [default: quadtree.gpkg]
  --processing-areas-fname PATH   Filename for the processing areas file
                                  (forced to GPKG format).  [default:
                                  processing_areas.gpkg]
  --crs INTEGER                   Coordinate Reference System (EPSG).
  --max INTEGER                   Max number of buildings per tile.  [default:
                                  3500]
  --help                          Show this message and exit.
```

We recommend using a building footprints file instead of downloading from OSM. If your file path is <code>data/buildings.gpkg</code>, you can use the following command: 

```bash
optim3d index2d data/buildings.gpkg
```

If you changed the output folder structure, you can specify the output folder using the <code>--output</code> option. For example, to save the results in the <code>results</code> folder, use the following command:

```bash
optim3d index2d data/buildings.gpkg --output results
```

While it is possible to download building footprints from OSM, it is recommended to use a file instead. If you want to download building footprints from OSM, you can specify the bounding box using the <code>--osm</code> option. For example, to download building footprints in the bounding box [5.5, 50.6, 5.7, 50.8], use the following command:

```bash
optim3d index2d --osm 5.5 50.6 5.7 50.8
```

This will download the building footprints from OSM, index them using the quadtree scheme, and save the results in the <code>output</code> folder. You can specify the path to save the downloaded OSM footprints using the <code>--osm-save-path</code> option. For example, to save the downloaded OSM footprints in the <code>data</code> folder, use the following command:

```bash
optim3d index2d --osm 5.5 50.6 5.7 50.8 --osm-save-path osm_footprints.shp
```

#### Step 3 : OcTree indexing of the 3D point cloud

Processing large point cloud datasets is hardware-intensive. Therefore, it is necessary to index the 3D point cloud before processing. The index structure makes it possible to stream only the parts of the data that are required, without having to download the entire dataset. In this case, the spatial indexing of the airborne point cloud is performed using an octree structure. This is done using the second command <code>index3d</code>. Use <code>optim3d index3d --help</code> to see the detailed help:

```
Usage: optim3d index3d [OPTIONS] POINTCLOUD

  OcTree indexing of 3D point cloud using Entwine.

Options:
  --output PATH            Output directory.  [default: output]
  --folder-structure PATH  Folder structure file.  [default:
                           folder_structure.xml]
  --help                   Show this message and exit.
```

For example, if your point cloud file is <code>data/pointcloud.laz</code>, you can use the following command:

```bash
optim3d index3d data/pointcloud.laz
```

#### Step 4 : Tiling of the 3D point cloud

The tiling of the indexed point cloud is based on the processing areas already calculated. This is achieved using the third command <code>tile3d</code>. Use <code>optim3d tile3d --help</code> to see the detailed help:

```
Usage: optim3d tile3d [OPTIONS]

  Tiling of point cloud using the calculated processing areas.

Options:
  --output PATH            Output directory.  [default: output]
  --folder-structure PATH  Folder structure file.  [default:
                           folder_structure.xml]
  --areas PATH             Processing areas file.  [default:
                           processing_areas.gpkg]
  --max-workers INTEGER    Maximum number of workers for tiling.  [default: 8]
  --help                   Show this message and exit.
```

For example, you can use the following command to tile the indexed point cloud:

```bash
optim3d tile3d
```

If you changed the processing area default file name, you can specify the path to the processing areas file using the <code>--areas</code> option. For example, if the processing areas file is <code>data/areas.gpkg</code>, you can use the following command:

```bash
optim3d tile3d --areas data/areas.gpkg
```

#### Step 5 : 3D reconstruction of building models tile by tile

In this step, we perform the 3D reconstruction of building models. The process make use of GeoFlow to generate highly detailed 3D building models tile by tile. This is achieved using the fourth command <code>reconstruct</code>. Use <code>optim3d reconstruct --help</code> to see the detailed help:

```
Usage: optim3d reconstruct [OPTIONS]

  Optimized 3D reconstruction of buildings using GeoFlow.

Options:
  --output PATH            Output directory.  [default: output]
  --folder-structure PATH  Folder structure file.  [default:
                           folder_structure.xml]
  --max-workers INTEGER    Maximum number of workers for reconstruction.
                           [default: 8]
  --help                   Show this message and exit.
```

For example, you can use the following command to reconstruct the 3D building models:

```bash
optim3d reconstruct
```

The maximum number of workers for reconstruction can be specified using the <code>--max-workers</code> option. This parameter depends on your hardware configuration, and it is used to parallelize the reconstruction process. For example, to use 16 workers, you can use the following command:

```bash
optim3d reconstruct --max-workers 4
```

We recommend using a maximum number of workers less than the number of CPU cores available on your machine. This ensures that the reconstruction process does not consume all the resources and that the machine remains responsive. It also prevents the command from skipping tiles due to insufficient resources.


#### Step 6 : Post-processing of CityJSON files

The generated CityJSON files should be post-processed to correct the City Objects IDs. This is done using the fifth command <code>post</code>. Use <code>optim3d post --help</code> to see the detailed help:

```
Usage: optim3d post [OPTIONS]

  Postprocess the generated CityJSON files.

Options:
  --output PATH            Output directory.  [default: output]
  --folder-structure PATH  Folder structure file.  [default:
                           folder_structure.xml]
  --help                   Show this message and exit.
```

For example, you can use the following command to post-process the generated CityJSON files:

```bash
optim3d post
```

## Results

The results of each command are saved in the <code>output</code> folder with the following structure:

```bash
├── output
│   ├── footprint_tiles
│   │   ├── *.cpg
│   │   ├── *.dbf
│   │   ├── *.prj
│   │   ├── *.shp
│   │   ├── *.shx
│   ├── indexed_pointcloud
│   │   ├── ept-data
│   │   │   ├── *.laz
│   │   ├── ept-hierarchy
│   │   │   ├── 0-0-0-0.json
│   │   ├── ept-sources
│   │   │   ├── *.json
│   │   ├── ept.json
│   │   ├── ept-build.json
│   ├── model
│   │   ├── cityjson
│   │   ├── *.city.json
│   │   ├── obj
│   │   ├── *.obj
│   │   ├── *.obj.mtl
│   ├── pointcloud_tiles
│   │   ├── *.las
│   ├── folder_structure.xml
│   ├── processing_areas.gpkg
│   └── quadtree.gpkg
```

The 3D building models can be inspected using [Ninja](https://github.com/cityjson/ninja), the official web viewer for CityJSON files.

![image](https://user-images.githubusercontent.com/72500344/216613188-82d54c75-7e03-4ee7-8c1c-d081e0c1d4ac.png)

### Docker Image

Optim3D is also available as [Docker image](https://hub.docker.com/r/yarroudh/optim3d).

These are the steps to run Optim3D as a Docker container:

1. First pull the image using the <code>docker pull</code> command:

```bash
docker pull yarroudh/optim3d
```

2. To run the Docker container and mount your data inside it, use the <code>docker run</code> command with the <code>-v</code> option to specify the path to the host directory and the path to the container directory where you want to mount the data folder. For example:

```bash
docker run -d -v ABSOLUTE_PATH_TO_HOST_DATA:/home/user/data yarroudh/optim3d
```

This command will start a Docker container in detached mode, mount the **ABSOLUTE_PATH_TO_HOST_DATA** directory on the host machine to the **/home/user/data** directory inside the container, and run the <code>yarroudh/optim3d</code> image. Do not change the path of the directory inside the container.

3. Find the container ID and copy it. You can use the <code>docker ps</code> command to list all running containers and their IDs.
4. Launch a command inside the container using <code>docker exec</code>, use the container ID or name and the command you want to run. For example:

```bash
docker exec CONTAINER_ID optim3d index2d data/FILE_NAME
docker exec CONTAINER_ID optim3d index3d data/FILE_NAME
docker exec CONTAINER_ID optim3d tiler3d
docker exec CONTAINER_ID optim3d reconstruct
docker exec CONTAINER_ID optim3d post
```

5. To copy the output of the command from the container to a local path, use the <code>docker cp</code> command with the container ID or name, the path to the file inside the container, and the path to the destination on the host machine. For example:

- To copy the output of one command:
```bash
docker cp CONTAINER_ID:/home/user/output/footprint_tiles PATH_ON_HOST_MACHINE
```
This will copy the output of footprints tiling. Please check the results section for the output structure.

- To copy the output of all the commands:
```bash
docker cp CONTAINER_ID:/home/user/output PATH_ON_HOST_MACHINE
```

6. Finally, after executing all the commands and copying the results to your local machine, you can stop the Docker container using the <code>docker stop</code> command followed by the container ID or name:

```bash
docker stop CONTAINER_ID
```


## Related repositories

[Automatic correction of buildings ground floor elevation in 3D City Models](https://github.com/Yarroudh/ZRect3D)

GeoFlow requires that the point cloud includes some ground points around the building so that it can determine the ground floor elevation. However, for aerial point clouds, buildings surrounded by others may not meet this condition which may result in inaccurate height estimation above the ground. This can be resolved using [ZRect3D](https://github.com/Yarroudh/zrect3d), a tool for automatic correction of buildings ground-floor elevation in CityJSON files using ground points from LiDAR data.

## License

This software is under the BSD 3-Clause "New" or "Revised" license which is a permissive license that allows you almost unlimited freedom with the software so long as you include the BSD copyright and license notice in it. Please read the [LICENSE](https://github.com/Yarroudh/Optim3D/blob/main/LICENSE) and the [COPYING](https://github.com/Yarroudh/Optim3D/blob/main/COPYING) files for more details.

## Citation

The recommended citation format for this repository is provided in the accompanying [BibTeX citation](https://github.com/Yarroudh/Optim3D/blob/main/CITATION.bib). Additionally, please make sure to comply with any licensing terms and conditions associated with the use of this repository.

```bibtex
@InProceedings{10.1007/978-3-031-43699-4_50,
  author="Yarroudh, Anass
  and Kharroubi, Abderrazzaq
  and Billen, Roland",
  editor="Kolbe, Thomas H.
  and Donaubauer, Andreas
  and Beil, Christof",
  title="Optim3D: Efficient and Scalable Generation of Large-Scale 3D Building Models",
  booktitle="Recent Advances in 3D Geoinformation Science",
  year="2024",
  publisher="Springer Nature Switzerland",
  address="Cham",
  pages="835--849",
}
```

Yarroudh, A., Kharroubi, A., Billen, R. (2024). Optim3D: Efficient and Scalable Generation of Large-Scale 3D Building Models. In: Kolbe, T.H., Donaubauer, A., Beil, C. (eds) Recent Advances in 3D Geoinformation Science. 3DGeoInfo 2023. Lecture Notes in Geoinformation and Cartography. Springer, Cham. https://doi.org/10.1007/978-3-031-43699-4_50

## About Optim3D

This software was developped by [Anass Yarroudh](https://www.linkedin.com/in/anass-yarroudh/), a Research Engineer at the [GeoScITY department of the University of Liege](https://www.geoscity.uliege.be/).
For more detailed information please contact us via <ayarroudh@uliege.be>, we are pleased to send you the necessary information.
