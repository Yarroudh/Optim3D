# Copyright (c) 2022-2023 - University of Liège
# Author : Anass Yarroudh (ayarroudh@uliege.be), GeoScITY Lab of ULiege
# This file is distributed under the BSD-3 licence. See LICENSE file for complete text of the license.

import click
import json
import copy
import time
import os
import tempfile
import geopandas as gpd
import osmnx as ox
import pdal
import multiprocessing
import subprocess
import psutil
from typing import List, Any, Union
import math
import collections
import shapely.geometry as geometry
from optim3d.utils import OrderedGroup, Point, Bounds, QuadTree, euclid_compare, euclid_distance, tile, geoflow


@click.group(cls=OrderedGroup, help="CLI tool to manage full optimized reconstruction of large-scale 3D building models.")
def cli():
    pass

@click.command()
@click.argument('footprints', type=click.Path(exists=True), required=False)
@click.option('--output', help='Output directory.', type=click.Path(exists=False), default="output", show_default=True)
@click.option('--osm', help='Download and work with building footprints from OpenStreetMap [west, north, est, south].', nargs=4, type=click.Tuple([float, float, float, float]), default=(-1, -1, -1, -1))
@click.option('--crs', help='Specify the Coordinate Reference System (EPSG).', type=click.INT)
@click.option('--max', help='Maximum number of buildings per tile.', type=click.INT, default=3500, show_default=True)

def index2d(footprints, output, osm, crs, max):
    '''
    QuadTree indexing and tiling of 2D building footprints.
    '''

    start = time.time()

    if (os.path.exists(output)==False):
        os.mkdir(output)
    if (os.path.exists('{}/footprint_tiles'.format(output))==False):
        os.mkdir('{}/footprint_tiles'.format(output))

    if (osm != (-1, -1, -1, -1)):
        buildings = ox.geometries.geometries_from_bbox(north=osm[0], south=osm[1], east=osm[2], west=osm[3], tags = {'building': True} )
    else:
        buildings = gpd.read_file(footprints, encoding="utf-8")

    if (crs):
        df = buildings.to_crs(epsg=crs)
    else:
        crs = str(buildings.crs)[-4:]
        df = buildings

    df['centroid'] = df['geometry'].centroid

    centroids = []
    for index, row in df.iterrows():
        centroids.append([row['centroid'].x, row['centroid'].y])

    bounds = df.dissolve().bounds
    width = bounds.maxx - bounds.minx
    height = bounds.maxy - bounds.miny

    quadTree = QuadTree(Bounds(float(bounds.minx), float(bounds.miny), float(width), float(height)), max_objects=max)

    for point in centroids:
        quadTree.insert(Point(point[0], point[1]))

    series = quadTree.create()
    series.to_file('{}/quadtree.gpkg'.format(output), driver="GPKG")

    boundings = gpd.read_file('{}/quadtree.gpkg'.format(output))
    df.reset_index()

    boundings.crs = df.crs
    node = []
    for i, building in df.iterrows():
        for j, bounding in boundings.iterrows():
            if (bounding.geometry.intersects(building.centroid)):
                node.append(j)

    df['node'] = node
    gp = df.drop('centroid', axis=1).groupby('node')

    bbox = []
    for g in gp.groups:
        area = gp.get_group(g)
        dissolved = area.dissolve()
        boundary = dissolved.boundary
        envelope = boundary.iloc[0].envelope
        buffer = envelope.buffer(10)
        bbox.append(buffer)

    process = gpd.GeoDataFrame({'geometry':bbox}, crs="EPSG:{}".format(crs))
    process.set_geometry(col='geometry')
    process.to_file("{}/processing_areas.gpkg".format(output), driver="GPKG")

    for g in gp.groups:
        group = gp.get_group(g)
        group.reset_index(inplace=True)
        group = group.rename(columns = {'index':'OIDN'})
        group.set_index(['OIDN'])
        group.to_file('{}/footprint_tiles/tile_{}.shp'.format(output, g), encoding="utf-8")
        print(".done: tile_{}.shp".format(g))

    end = time.time()
    processTime = end - start

    print("All tiles generated successfully")
    click.echo("Time: {}".format(time.strftime("%H:%M:%S", time.gmtime(processTime))))

@click.command()
@click.argument('pointcloud', type=click.Path(exists=True), required=True)
@click.option('--output', help='Output directory.', type=click.Path(exists=False), default="output", show_default=True)

def index3d(pointcloud, output):
    '''
    OcTree indexing of 3D point cloud using Entwine.
    '''

    if (os.path.exists(output)==False):
        os.mkdir(output)

    tmp = tempfile.mkdtemp()

    config = {
        "input":os.path.abspath(pointcloud),
        "output":os.path.abspath("{}/indexed_pointcloud".format(output))
    }

    config_file = os.path.join(tmp, "config.json")
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)

    os.system('entwine build -c {}'.format(config_file))

@click.command()
@click.option('--areas', help='The calculated processing areas.', type=click.Path(exists=True), default="output/processing_areas.gpkg", show_default=True)
@click.option('--indexed', help='Indexed 3D point cloud directory.', type=click.Path(exists=True), default="output/indexed_pointcloud", show_default=True)
@click.option('--output', help='Output directory.', type=click.Path(exists=False), default="output", show_default=True)

def tiler3d(areas, indexed, output):
    '''
    Tiling of point cloud using the calculated processing areas.
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

@click.command()
@click.option('--pointcloud', help='3D point cloud tiles directory.', type=click.Path(exists=True), default="output/pointcloud_tiles", show_default=True)
@click.option('--footprints', help='2D building footprints tiles directory.', type=click.Path(exists=True), default="output/footprint_tiles", show_default=True)
@click.option('--output', help='Output directory.', type=click.Path(exists=False), default="output", show_default=True)

def reconstruct(footprints, pointcloud, output):
    '''
    Optimized 3D reconstruction of buildings using GeoFlow.
    '''

    start = time.time()

    config_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config')
    config_file = os.path.join(config_dir, 'reconstruct.json')
    config_file_ = os.path.join(config_dir, 'reconstruct_.json')

    with open(config_file) as file:
        reconstruct = json.load(file)

    with open(config_file_) as file:
        reconstruct_ = json.load(file)

    if (os.path.exists('{}/flowcharts'.format(output))==False):
        os.mkdir('{}/flowcharts'.format(output))
    if (os.path.exists('{}/model'.format(output))==False):
        os.mkdir('{}/model'.format(output))
    if (os.path.exists('{}/model/cityjson'.format(output))==False):
        os.mkdir('{}/model/cityjson'.format(output))
    if (os.path.exists('{}/model/obj'.format(output))==False):
        os.mkdir('{}/model/obj'.format(output))

    for i in range(len(os.listdir('{}/pointcloud_tiles'.format(output)))):
        with open('{}/flowcharts/reconstruct{}.json'.format(output, i), 'w') as file:
            data = reconstruct
            data['globals']['input_footprint'][2] = '{}/tile_{}.shp'.format(footprints, i)
            data['globals']['input_pointcloud'][2] = '{}/tile_{}.las'.format(pointcloud, i)
            data['globals']['output_cityjson'][2] = '{}/model/cityjson/tile_{}.city.json'.format(output, i)
            data['globals']['output_obj_lod12'][2] = '{}/model/obj/tile_{}_lod12.obj'.format(output, i)
            data['globals']['output_obj_lod13'][2] = '{}/model/obj/tile_{}_lod13.obj'.format(output, i)
            data['globals']['output_obj_lod22'][2] = '{}/model/obj/tile_{}_lod22.obj'.format(output, i)

        with open('{}/flowcharts/reconstruct{}.json'.format(output, i), 'w') as file:
            json.dump(data, file, indent=2)

        with open('{}/flowcharts/reconstruct{}_.json'.format(output, i), 'w') as file:
            data = reconstruct_
            data['globals']['input_footprint'][2] = '{}/tile_{}.shp'.format(footprints, i)
            data['globals']['input_pointcloud'][2] = '{}/tile_{}.las'.format(pointcloud, i)
            data['globals']['output_cityjson'][2] = '{}/model/cityjson/tile_{}.city.json'.format(output, i)
            data['globals']['output_obj_lod12'][2] = '{}/model/obj/tile_{}_lod12.obj'.format(output, i)
            data['globals']['output_obj_lod13'][2] = '{}/model/obj/tile_{}_lod13.obj'.format(output, i)
            data['globals']['output_obj_lod22'][2] = '{}/model/obj/tile_{}_lod22.obj'.format(output, i)

        with open('{}/flowcharts/reconstruct{}_.json'.format(output, i), 'w') as file:
            json.dump(data, file, indent=2)

    commands = [
        "geof {}/flowcharts/reconstruct{}.json".format(output, j)
        for j in range(len(os.listdir(f"{output}/pointcloud_tiles")))
    ]
    
    processes = []
    
    for cmd in commands:
        while psutil.virtual_memory().percent > 90:
            time.sleep(2)
        
        process = subprocess.Popen(cmd, shell=True)
        processes.append(process)
    
    # Wait for all processes to complete
    for process in processes:
        process.wait()

    end = time.time()
    processTime = end - start

    print("All buildings reconstructed successfully")
    click.echo("Time: {}".format(time.strftime("%H:%M:%S", time.gmtime(processTime))))

@click.command()
@click.option('--cityjson', help='CityJSON files directory.', type=click.Path(exists=True), default="output/model/cityjson", show_default=True)

def post(cityjson):
    '''
    Postprocess the generated CityJSON files.
    '''
    start = time.time()

    i = 0
    for filename in os.listdir(cityjson):
        with open('{}/{}'.format(cityjson, filename)) as file:
            data = json.load(file)
            twin = copy.deepcopy(data)

            for (key, value) in data['CityObjects'].items():
                children = twin['CityObjects'][key].get('children')
                parents = twin['CityObjects'][key].get('parents')

                if (children):
                    for j in range(len(children)):
                        children[j] = 'T{}_{}'.format(i,children[j])

                if (parents):
                    for j in range(len(parents)):
                        parents[j] = 'T{}_{}'.format(i,parents[j])

                twin['CityObjects']['T{}_{}'.format(i,key)] = twin['CityObjects'].pop(key)

        with open('{}/{}'.format(cityjson, filename), 'w') as file:
            json.dump(twin, file, indent=2)

        print(".done: tile_{}.city.json".format(i))
        i += 1

    end = time.time()
    processTime = end - start

    print("All files corrected successfully")
    click.echo("Time: {}".format(time.strftime("%H:%M:%S", time.gmtime(processTime))))

cli.add_command(index2d)
cli.add_command(index3d)
cli.add_command(tiler3d)
cli.add_command(reconstruct)
cli.add_command(post)


if __name__ == '__main__':
    multiprocessing.freeze_support()
    cli(prog_name='optim3d')
