Usage of CLI
==========================================================

Commands
----------------

After installation, you have a small program called **optim3d**. Use `optim3d –-help` to see the detailed help:

::

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

The process consists of five distinct steps or commands that must be
executed in a specific order to achieve the desired outcome.

Step 1 : 2D building footprints indexing and tiling
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Quadtree-based tiling scheme is used for spatial partitioning of
building footprints. This assures that the reconstruction time per tile
is more or less the same and that the tiles available for download are
similar in file size. This is done using the first command index2d. Use
`optim3d index2d -–help` to see the detailed help:

::

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

Step 2 : OcTree indexing of the 3D point cloud
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Processing large point cloud datasets is hardware-intensive. Therefore,
it is necessary to index the 3D point cloud before processing. The index
structure makes it possible to stream only the parts of the data that
are required, without having to download the entire dataset. In this
case, the spatial indexing of the airborne point cloud is performed
using an octree structure. This can be easily done using Entwine, an
open-source library for organizing and indexing large point cloud
datasets using an octree data structure that allows fast and efficient
spatial queries. This is done using the second command index3d. Use
`optim3d index3d –-help` to see the detailed help:

::

   Usage: optim3d index3d [OPTIONS] POINTCLOUD

     OcTree indexing of 3D point cloud using Entwine.

   Options:
     --output PATH  Output directory.  [default: ./output]
     --help         Show this message and exit.

Step 3 : Tiling of the 3D point cloud
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The tiling of the indexed point cloud is based on processing areas
calculated when the footprints were indexed. This is achieved using the
third command tiler3d. Use `optim3d tiler3d –-help` to see the detailed
help:

::

   Usage: optim3d tiler3d [OPTIONS]

     Tiling of 3D point cloud using the calculated processing areas.

   Options:
     --areas PATH    The calculated processing areas.  [default:
                     ./output/processing_areas.gpkg]
     --indexed PATH  Indexed 3D point cloud directory.  [default:
                     ./output/indexed_pointcloud]
     --output PATH   Output directory.  [default: ./output]
     --help          Show this message and exit.

Step 4 : 3D reconstruction of building models tile by tile
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The 3D reconstruction of building models is performed in this step. The
process make use of GeoFlow to generate hight detailed 3D building
models tile by tile. This is achieved using the fourth command
reconstruct. Use `optim3d reconstruct -–help` to see the detailed help:

::

   Usage: optim3d reconstruct [OPTIONS]

     Optimized 3D reconstruction of buildings using GeoFlow.

   Options:
     --pointcloud PATH  3D point cloud tiles directory.  [default:
                        ./output/pointcloud_tiles]
     --footprints PATH  2D building footprints tiles directory.  [default:
                        ./output/footprint_tiles]
     --output PATH      Output directory.  [default: ./output]
     --help             Show this message and exit.

Step 5 : Post-processing of CityJSON files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The generated CityJSON files should be processed to add information
about tiles to 3D objects. This is done using the fifth command post.
Use `optim3d post -–help` to see the detailed help:

::

   Usage: optim3d post [OPTIONS]

     Postprocess the generated CityJSON files.

   Options:
     --cityjson PATH  CityJSON files directory.  [default:
                      ./output/model/cityjson]
     --help           Show this message and exit.

Results
-------

The results of each command are saved in the **output** folder, which should
look like this after executing all the commands:

.. code:: bash

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

The 3D building models can be viewd using
`Ninja <https://github.com/cityjson/ninja>`__, the official web viewer
for CityJSON files.

.. figure:: https://user-images.githubusercontent.com/72500344/216613188-82d54c75-7e03-4ee7-8c1c-d081e0c1d4ac.png
   :alt: image

   CityJSON file visualized using Ninja

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