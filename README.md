<img src="https://user-images.githubusercontent.com/72500344/210864557-4078754f-86c1-4e7c-b291-73223bdf4e4d.png" alt="logo" width="200"/>

# Optimized reconstruction of large-scale 3D building models 

[![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://github.com/Yarroudh/ZRect3D/blob/main/LICENSE)
[![Geomatics Unit of ULiege - Development](https://img.shields.io/badge/Geomatics_Unit_of_ULiege-Development-2ea44f)](http://geomatics.ulg.ac.be/)

*Command-Line Interface (CLI) application for efficient and optimized reconstruction of large-scale 3D building models.*

![image](https://user-images.githubusercontent.com/72500344/217598559-8b58a28f-7c3a-4f61-a63d-9718383a6cef.png)

[GeoFlow](https://github.com/geoflow3d/geoflow-bundle) is a software tool that can be used to automatically reconstruct 3D building models from point clouds, with a high level of detail. It is a powerful tool for creating detailed and accurate 3D models of buildings and can be used in a variety of applications. The software is fully automated, making it easy to use and efficient for large-scale projects.

Our program is based on GeoFlow and makes use of it to perform 3D reconstruction of buildings. The process is inspired by the 3D BAG project, which is an up-to-date dataset containing detailed 3D building models of the Netherlands, based on the official BAG data and national AHN point cloud. The optimization of the reconstruction process is achieved by indexing and tiling of the input data which reduces the processing time and resources needed to generate large-scale 3D building models. The indexing and tiling of both, 3D point cloud and 2D footprints, allows for more efficient processing and handling of the 3D reconstruction workflow.

<img src="https://user-images.githubusercontent.com/72500344/212364590-b7fd444d-ec26-4a8b-bda9-fd4e1669bc6e.png" alt="Workflow of 3D Reconstruction" width="500"/>

## Installation

The easiest way to install <code>Optim3D</code> on Windows is to use the binary package on the [Release page](https://github.com/Yarroudh/Optim3D/releases/tag/release). In case you can not use the Windows installer, or if you are using a different operating system, you can build everything from source (see [INSTALL.md]()). You can also download the [Docker image](https://hub.docker.com/r/yarroudh/optim3d).

**NOTE:** It is important to note that in order to use our program for 3D reconstruction of buildings, [GeoFlow-bundle](https://github.com/geoflow3d/geoflow-bundle/releases/tag/2022.06.17) must be installed. Please read the License before using it.

## Usage of the CLI

### Binary package

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

The process consists of five distinct steps or <code>commands</code> that must be executed in a specific order to achieve the desired outcome.

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

Processing large point cloud datasets is hardware-intensive. Therefore, it is necessary to index the 3D point cloud before processing. The index structure makes it possible to stream only the parts of the data that are required, without having to download the entire dataset. In this case, the spatial indexing of the airborne point cloud is performed using an octree structure. This can be easily done using Entwine, an open-source library for organizing and indexing large point cloud datasets using an octree data structure that allows fast and efficient spatial queries. This is done using the second command <code>index3d</code>. Use <code>optim3d index3d --help</code> to see the detailed help:

```
Usage: optim3d index3d [OPTIONS] POINTCLOUD

  OcTree indexing of 3D point cloud using Entwine.     

Options:
  --output PATH  Output directory.  [default: ./output]
  --help         Show this message and exit.
```

#### Step 3 : Tiling of the 3D point cloud

The tiling of the indexed point cloud is based on processing areas calculated when the footprints were indexed. This is achieved using the third command <code>tiler3d</code>. Use <code>optim3d tiler3d --help</code> to see the detailed help:

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

The 3D reconstruction of building models is performed in this step. The process make use of GeoFlow to generate hight detailed 3D building models tile by tile. This is achieved using the fourth command <code>reconstruct</code>. Use <code>optim3d reconstruct --help</code> to see the detailed help:

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

The generated CityJSON files should be processed to add information about tiles to 3D objects. This is done using the fifth command <code>post</code>. Use <code>optim3d post --help</code> to see the detailed help:

```
Usage: optim3d post [OPTIONS]

  Postprocess the generated CityJSON files.

Options:
  --cityjson PATH  CityJSON files directory.  [default:
                   ./output/model/cityjson]
  --help           Show this message and exit.
```

### Running the application using Docker

Download the image from [Docker Hub](https://hub.docker.com/r/yarroudh/optim3d) using this command:

```bash
docker pull yarroudh/optim3d
```

To see which images are present locally, use the <code>docker images</code> command.

To access the data on your host inside Docker container, you can start the container with the volume from host mounted in the container by using <code>-v</code> flag:

```bash
docker run -v "/path/to/host/directory:/path/inside/container" optim3d
```

#### 2D building footprints indexing and tiling

```bash
docker run -v /data:/data optim3d main.py index2d data/footprints.shp
```

#### Copy the output folder

To copy the output folder from the Docker container to the host system, you can use the <code>docker cp</code> command as follows:

```bash
docker cp <container_id>:output output
```

To find the ID of the running Docker container, you can use the <code>docker ps</code> command, which lists all running containers along with their metadata, including the container ID.


### Building from source

If you want to build the solution from source, you should follow the steps in [INSTALL.md](). The commands can be used as decribed for the Binary package.

## Results

The results of each command are saved in the <code>output</code> folder, which will look like this after executing all the commands:

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

The 3D building models can be viewd using [Ninja](https://github.com/cityjson/ninja), the official web viewer for CityJSON files.

![image](https://user-images.githubusercontent.com/72500344/216613188-82d54c75-7e03-4ee7-8c1c-d081e0c1d4ac.png)

## Related repositories

[Automatic correction of buildings ground floor elevation in 3D City Models](https://github.com/Yarroudh/ZRect3D)

GeoFlow requires that the point cloud includes some ground points around the building so that it can determine the ground floor elevation. However, for aerial point clouds, buildings surrounded by others may not meet this condition which may result in inaccurate height estimation above the ground. This can be resolved using [ZRect3D](https://github.com/Yarroudh/zrect3d), a tool for automatic correction of buildings ground-floor elevation in CityJSON files using ground points from LiDAR data.

## License

This software is under the BSD 3-Clause "New" or "Revised" license which is a permissive license that allows you almost unlimited freedom with the software so long as you include the BSD copyright and license notice in it. Please read the [LICENSE](https://github.com/Yarroudh/Optim3D/blob/main/LICENSE) and the [COPYING](https://github.com/Yarroudh/Optim3D/blob/main/COPYING) files for more details.

## Citation

The use of open-source software repositories has become increasingly prevalent in scientific research. If you use this repository for your research, please make sure to cite it appropriately in your work. The recommended citation format for this repository is provided in the accompanying [BibTeX citation](https://github.com/Yarroudh/Optim3D/blob/main/CITATION.bib). Additionally, please make sure to comply with any licensing terms and conditions associated with the use of this repository.

```bibtex
@misc{yarroudh:2023:optim3d,
  author = {Yarroudh, Anass},
  title = {Optim3D: Optimized reconstruction of large-scale 3D building models},
  year = {2023},
  howpublished = {GitHub Repository},
  url = {https://github.com/Yarroudh/Optim3D}
}
```

Yarroudh, A. (2023). Optim3D: Optimized reconstruction of large-scale 3D building models [GitHub repository]. Retrieved from https://github.com/Yarroudh/Optim3D

## About Optim3D

This software was developped by [Anass Yarroudh](https://www.linkedin.com/in/anass-yarroudh/), a Research Engineer in the [Geomatics Unit of the University of Liege](http://geomatics.ulg.ac.be/fr/home.php). 
For more detailed information please contact us via <ayarroudh@uliege.be>, we are pleased to send you the necessary information.
