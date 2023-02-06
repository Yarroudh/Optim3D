<img src="https://user-images.githubusercontent.com/72500344/210864557-4078754f-86c1-4e7c-b291-73223bdf4e4d.png" alt="logo" width="200"/>

# Optimized reconstruction of large-scale 3D building models 

[![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://github.com/Yarroudh/ZRect3D/blob/main/LICENSE)
[![Geomatics Unit of ULiege - Development](https://img.shields.io/badge/Geomatics_Unit_of_ULiege-Development-2ea44f)](http://geomatics.ulg.ac.be/)

*Command-Line Interface (CLI) application for efficient and optimized reconstruction of large-scale 3D building models.*

[GeoFlow](https://github.com/geoflow3d/geoflow-bundle) is a software tool that can be used to automatically reconstruct 3D building models from point clouds, with a high level of detail. It is a powerful tool for creating detailed and accurate 3D models of buildings and can be used in a variety of applications. The software is fully automated, making it easy to use and efficient for large-scale projects.

Our program is based on GeoFlow and makes use of it to perform 3D reconstruction of buildings. The process is inspired by the 3D BAG project, which is an up-to-date dataset containing detailed 3D building models of the Netherlands, based on the official BAG data and national AHN point cloud. The optimization of the reconstruction process is achieved by indexing and tiling of the input data which reduces the processing time and resources needed to generate large-scale 3D building models. The indexing and tiling of both, 3D point cloud and 2D footprints, allows for more efficient processing and handling of the 3D reconstruction workflow.

<img src="https://user-images.githubusercontent.com/72500344/212364590-b7fd444d-ec26-4a8b-bda9-fd4e1669bc6e.png" alt="Workflow of 3D Reconstruction" width="500"/>

## Installation

The easiest way to install <code>Optim3D</code> on Windows is to use the binary package on the [Release page](). In case you can not use the Windows installer, or if you are using a different operating system, you can build everything from source.

**NOTE:** It is important to note that in order to use our program for 3D reconstruction of buildings, [GeoFlow-bundle](https://github.com/geoflow3d/geoflow-bundle/releases/tag/2022.06.17) must be installed. It is a necessary requirement for the program to function properly and perform the 3D reconstruction.

## Usage of the CLI
After installation, you have a small program called <code>optim3d</code>. Use <code>optim3d --help</code> to see the detailed help:

```
  Usage: optim3d [OPTIONS] COMMAND [ARGS]...

    CLI tool to manage full optimized reconstruction of large-scale 3D building
    models using GeoFlow.

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

### Step 1 : 2D building footprints indexing and tiling

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

### Step 2 : OcTree indexing of the 3D point cloud

Processing large point cloud datasets is hardware-intensive. Therefore, it is necessary to index the 3D point cloud before processing. The index structure makes it possible to stream only the parts of the data that are required, without having to download the entire dataset. In this case, the spatial indexing of the airborne point cloud is performed using an octree structure. This can be easily done using Entwine, an open-source library for organizing and indexing large point cloud datasets using an octree data structure that allows fast and efficient spatial queries. This is done using the second command <code>index3d</code>. Use <code>optim3d index3d --help</code> to see the detailed help:

```
  Usage: optim3d index3d [OPTIONS] POINTCLOUD

    OcTree indexing of 3D point cloud using Entwine.     

  Options:
    --output PATH  Output directory.  [default: ./output]
    --help         Show this message and exit.
```

### Step 3 : Tiling of the 3D point cloud

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

### Step 4 : 3D reconstruction of building models tile by tile

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

### Step 5 : Post-processing of CityJSON files

The generated CityJSON files should be processed to add information about tiles to 3D objects. This is done using the fifth command <code>post</code>. Use <code>optim3d post --help</code> to see the detailed help:

```
  Usage: optim3d post [OPTIONS]

    Postprocess the generated CityJSON files.

  Options:
    --cityjson PATH  CityJSON files directory.  [default:
                     ./output/model/cityjson]
    --help           Show this message and exit.
```

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

This software is under the BSD 3-Clause "New" or "Revised" license which is a permissive license that allows you almost unlimited freedom with the software so long as you include the BSD copyright and license notice in it. Please read the [LICENSE]() and the [COPYING]() files for more details.

## About Optim3D

This software was developped by [Anass Yarroudh](https://www.linkedin.com/in/anass-yarroudh/), a Research Engineer in the [Geomatics Unit of the University of Liege](http://geomatics.ulg.ac.be/fr/home.php). 
For more detailed information please contact us via <ayarroudh@uliege.be>, we are pleased to send you the necessary information.

