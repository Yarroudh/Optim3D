Usage of CLI
==========================================================

Commands
----------------

After installation, you have a small program called **optim3d**. Use `optim3d --help` to see the detailed help:

::

  Usage: optim3d [OPTIONS] COMMAND [ARGS]...

    CLI tool to manage full optimized reconstruction of large-scale 3D
    building models.

  Options:
    --help  Show this message and exit.

  Commands:
    prepare      Prepare the output folder structure.
    index2d      QuadTree indexing and tiling of 2D building footprints.
    index3d      OcTree indexing of 3D point cloud using Entwine.
    tile3d       Tiling of point cloud using the calculated processing areas.
    reconstruct  Optimized 3D reconstruction of buildings using GeoFlow.
    post         Postprocess the generated CityJSON files.

The process consists of six steps or commands that must be executed in a specific order to achieve the desired outcome.

Step 1 : Prepare the output folder structure
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Before starting the 3D reconstruction process, it is necessary to prepare the output folder structure. This is done using the first command prepare. Use `optim3d prepare --help` to see the detailed help:

::

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

Step 2 : 2D building footprints indexing and tiling
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Quadtree-based tiling scheme is used for spatial partitioning of building footprints. This assures that the reconstruction time per tile is more or less the same and that the tiles available for download are similar in file size. This is done using the first command index2d. Use `optim3d index2d --help` to see the detailed help:

::

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

Step 3 : OcTree indexing of the 3D point cloud
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Processing large point cloud datasets is hardware-intensive. Therefore, it is necessary to index the 3D point cloud before processing. The index structure makes it possible to stream only the parts of the data that are required, without having to download the entire dataset. In this case, the spatial indexing of the airborne point cloud is performed using an octree structure. This is done using the second command index3d. Use `optim3d index3d --help` to see the detailed help:

::

  Usage: optim3d index3d [OPTIONS] POINTCLOUD

    OcTree indexing of 3D point cloud using Entwine.

  Options:
    --output PATH            Output directory.  [default: output]
    --folder-structure PATH  Folder structure file.  [default:
                    folder_structure.xml]
    --help                   Show this message and exit.

Step 4 : Tiling of the 3D point cloud
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The tiling of the indexed point cloud is based on the processing areas already calculated. This is achieved using the third command tile3d. Use `optim3d tile3d --help` to see the detailed help:

::

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

Step 5 : 3D reconstruction of building models tile by tile
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In this step, we perform the 3D reconstruction of building models. The process make use of GeoFlow to generate highly detailed 3D building models tile by tile. This is achieved using the fourth command reconstruct. Use `optim3d reconstruct --help` to see the detailed help:

::

  Usage: optim3d reconstruct [OPTIONS]

    Optimized 3D reconstruction of buildings using GeoFlow.

  Options:
    --output PATH            Output directory.  [default: output]
    --folder-structure PATH  Folder structure file.  [default:
                    folder_structure.xml]
    --max-workers INTEGER    Maximum number of workers for reconstruction.
                    [default: 8]
    --help                   Show this message and exit.

Step 6 : Post-processing of CityJSON files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The generated CityJSON files should be post-processed to correct the City Objects IDs. This is done using the fifth command post. Use `optim3d post --help` to see the detailed help:

::

  Usage: optim3d post [OPTIONS]

    Postprocess the generated CityJSON files.

  Options:
    --output PATH            Output directory.  [default: output]
    --folder-structure PATH  Folder structure file.  [default:
                    folder_structure.xml]
    --help                   Show this message and exit.

  Results
  ^^^^^^^

  The results of each command are saved in the output folder with the following structure:

  ::

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

  The 3D building models can be inspected using `Ninja <https://github.com/cityjson/ninja>`__, the official web viewer for CityJSON files.

  .. image:: https://user-images.githubusercontent.com/72500344/216613188-82d54c75-7e03-4ee7-8c1c-d081e0c1d4ac.png
     :alt: Ninja web viewer for CityJSON files

Post-processing
--------------------

`Automatic correction of buildings ground floor elevation in 3D City
Models <https://github.com/Yarroudh/ZRect3D>`__

GeoFlow requires that the point cloud includes some ground points around
the building so that it can determine the ground floor elevation.
However, for aerial point clouds, buildings surrounded by others may not
meet this condition which may result in inaccurate height estimation
above the ground. This can be resolved using
`ZRect3D <https://github.com/Yarroudh/zrect3d>`__, a tool for automatic
correction of buildings ground-floor elevation in CityJSON files using
ground points from LiDAR data.