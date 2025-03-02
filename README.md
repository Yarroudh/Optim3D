<img src="https://github.com/Yarroudh/templates_cj/assets/72500344/1b523bfa-b0d4-46d6-9400-69bc1c81fe90" alt="logo" width="200"/>

**Paper is now published. For more information, please refer to: [Recent Advances in 3D Geoinformation Science](https://link.springer.com/chapter/10.1007/978-3-031-43699-4_50)**

# Optim3D: Efficient and scalable generation of large-scale 3D building

[![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://github.com/Yarroudh/ZRect3D/blob/main/LICENSE)
[![GeoScITY LAB - Development](https://img.shields.io/badge/Geomatics_Unit_of_ULiege-Development-2ea44f)](http://geomatics.ulg.ac.be/)
[![Springer](https://img.shields.io/badge/Springer-10.1007/978--3--031--43699--4_50-green?style=flat&link=https://doi.org/10.1007/978-3-031-43699-4_50)](https://doi.org/10.1007/978-3-031-43699-4_50)

*Command-Line Interface (CLI) application for efficient and optimized reconstruction of large-scale 3D building models.*

Optim3D is a powerful tool for efficient and scalable generation of highly detailed and large-scale 3D building models. The modeling process is based on [GeoFlow](https://github.com/geoflow3d/geoflow-bundle). The tool focuses mainly on preparing data for efficient reconstruction through indexing, tiling and parallel computing, which significantly reduces the processing time and resources required to generate large-scale 3D building models.

<img src="https://user-images.githubusercontent.com/72500344/212364590-b7fd444d-ec26-4a8b-bda9-fd4e1669bc6e.png" alt="Workflow of 3D Reconstruction" width="500"/>

## Documentation

If you are using Optim3D, we highly recommend that you take the time to read the [documentation](https://optim3d.readthedocs.io/en/latest/). The documentation is an essential resource that will help you understand the features and functionality of our software, as well as provide guidance on how to use it effectively.

## Installation

You can install optim3d in your Conda environment by simply running:

```bash
conda create --name optimenv python==3.9
conda activate optimenv
conda install -c conda-forge pdal python-pdal
conda install -c conda-forge entwine
pip install optim3d
```

You can also build everything from source (see [INSTALL.md](https://github.com/Yarroudh/Optim3D/blob/main/INSTALL.md)). A [Docker image](https://hub.docker.com/r/yarroudh/optim3d) is also available.

**NOTE:** It is important to note that in order to use our program for 3D reconstruction of buildings, [GeoFlow-bundle](https://github.com/geoflow3d/geoflow-bundle/releases/tag/2022.06.17) must be installed. Please read the LICENSE file.

## Usage of the CLI

### Python package

After installation, you have a small program called <code>optim3d</code>. Use <code>optim3d --help</code> to see the detailed help:

```
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

The process consists of five steps or <code>commands</code> that must be executed in a specific order to achieve the desired outcome.

#### Step 1 : 2D building footprints indexing and tiling

Quadtree-based tiling scheme is used for spatial partitioning of building footprints. This assures that the reconstruction time per tile is more or less the same and that the tiles available for download are similar in file size. This is done using the first command <code>index2d</code>. Use <code>optim3d index2d --help</code> to see the detailed help:

```
Usage: optim3d index2d [OPTIONS] [FOOTPRINTS]

  QuadTree indexing and tiling of building 2D footprints.

Options:
  --output PATH                   Output directory.  [default: ./output]
  --osm <FLOAT FLOAT FLOAT FLOAT>...
                                  Download and work with building footprints
                                  from OpenStreetMap [west, north, est,
                                  south].
  --crs INTEGER                   Specify the Coordinate Reference System
                                  (EPSG).
  --max INTEGER                   Maximum number of buildings per tile.
                                  [default: 3500]
  --help                          Show this message and exit.
```

#### Step 2 : OcTree indexing of the 3D point cloud

Processing large point cloud datasets is hardware-intensive. Therefore, it is necessary to index the 3D point cloud before processing. The index structure makes it possible to stream only the parts of the data that are required, without having to download the entire dataset. In this case, the spatial indexing of the airborne point cloud is performed using an octree structure. This is done using the second command <code>index3d</code>. Use <code>optim3d index3d --help</code> to see the detailed help:

```
Usage: optim3d index3d [OPTIONS] POINTCLOUD

  OcTree indexing of 3D point cloud using Entwine.

Options:
  --output PATH  Output directory.  [default: ./output]
  --help         Show this message and exit.
```

#### Step 3 : Tiling of the 3D point cloud

The tiling of the indexed point cloud is based on the processing areas already calculated. This is achieved using the third command <code>tiler3d</code>. Use <code>optim3d tiler3d --help</code> to see the detailed help:

```
Usage: optim3d tiler3d [OPTIONS]

  Tiling of 3D point cloud using the calculated processing areas.

Options:
  --areas PATH    The calculated processing areas.  [default:
                  ./output/processing_areas.gpkg]
  --indexed PATH  Indexed 3D point cloud directory.  [default:
                  ./output/indexed_pointcloud]
  --output PATH   Output directory.  [default: ./output]
  --help          Show this message and exit.
```

#### Step 4 : 3D reconstruction of building models tile by tile

In this step, we perform the 3D reconstruction of building models. The process make use of GeoFlow to generate highly detailed 3D building models tile by tile. This is achieved using the fourth command <code>reconstruct</code>. Use <code>optim3d reconstruct --help</code> to see the detailed help:

```
Usage: optim3d reconstruct [OPTIONS]

  Optimized 3D reconstruction of buildings using GeoFlow.

Options:
  --pointcloud PATH  3D point cloud tiles directory.  [default:
                     ./output/pointcloud_tiles]
  --footprints PATH  2D building footprints tiles directory.  [default:
                     ./output/footprint_tiles]
  --output PATH      Output directory.  [default: ./output]
  --help             Show this message and exit.
```

#### Step 5 : Post-processing of CityJSON files

The generated CityJSON files should be post-processed to correct the City Objects IDs. This is done using the fifth command <code>post</code>. Use <code>optim3d post --help</code> to see the detailed help:

```
Usage: optim3d post [OPTIONS]

  Postprocess the generated CityJSON files.

Options:
  --cityjson PATH  CityJSON files directory.  [default:
                   ./output/model/cityjson]
  --help           Show this message and exit.
```

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

### Building from source

If you want to build the solution from source, you should follow the steps in [INSTALL.md]().

## Results

The results of each command are saved in the <code>output</code> folder with the following structure:

```bash
├── output
│   ├── flowcharts
│   │   ├── *.json
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
│   ├── processing_areas.gpkg
│   └── quadtree.gpkg
```

The 3D building models can be inspected using [Ninja](https://github.com/cityjson/ninja), the official web viewer for CityJSON files.

![image](https://user-images.githubusercontent.com/72500344/216613188-82d54c75-7e03-4ee7-8c1c-d081e0c1d4ac.png)

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

This software was developped by [Anass Yarroudh](https://www.linkedin.com/in/anass-yarroudh/), a Research Engineer at the [GeoScITY department of the University of Liege](http://geomatics.ulg.ac.be/fr/home.php).
For more detailed information please contact us via <ayarroudh@uliege.be>, we are pleased to send you the necessary information.
