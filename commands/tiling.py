# Copyright (c) 2022-2023 - University of Liège
# Author : Anass Yarroudh (ayarroudh@uliege.be), Geomatics Unit of ULiege
# This file is distributed under the BSD-3 licence. See LICENSE file for complete text of the license.

import click
import os
import json
import geopandas as gpd
import multiprocessing
import pdal
import time

def tile(index, features, path, output):
    minx = features.bounds.iloc[index].minx
    maxx = features.bounds.iloc[index].maxx
    miny = features.bounds.iloc[index].miny
    maxy = features.bounds.iloc[index].maxy
        
    data ={
        "pipeline": [
                {
                    "type": "readers.ept",
                    "filename":"{}/ept.json".format(path),
                    "bounds":"([{},{}],[{},{}])".format(minx, maxx, miny, maxy)
                },
                {
                    "type":"writers.las",
                    "filename":"{}/tile_{}.las".format('{}/pointcloud_tiles'.format(output), index)
                }
            ]
        }
        
    pipeline = pdal.Pipeline(json.dumps(data))
    pipeline.execute()

    print(".done: tile_{}.las".format(index), flush=True)

@click.command()
@click.option('--areas', help='The calculated processing areas.', type=click.Path(exists=True), default="./output/processing_areas.gpkg", show_default=True)
@click.option('--indexed', help='Indexed 3D point cloud directory.', type=click.Path(exists=True), default="./output/indexed_pointcloud", show_default=True)
@click.option('--output', help='Output directory.', type=click.Path(exists=False), default="./output", show_default=True)

def tiler3d(areas, indexed, output):
    '''
    Tiling of 3D point cloud using calculated processing areas.
    '''
    start = time.time()

    if (os.path.exists(output)==False):
        os.mkdir(output)
    if (os.path.exists('{}\\pointcloud_tiles'.format(output))==False):
        os.mkdir('{}\\pointcloud_tiles'.format(output))  

    tiles = gpd.read_file(areas)

    processes = [multiprocessing.Process(target=tile, args=(i, tiles, indexed, output)) for i, row in tiles.iterrows()]

    for process in processes:
        process.start()

    for process in processes:
        process.join()

    end = time.time()
    processTime = end - start

    print('All tiles generated successfully')
    click.echo("Time: {}".format(time.strftime("%H:%M:%S", time.gmtime(processTime))))
