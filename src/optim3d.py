# Copyright (c) 2022-2023 - University of Liège
# Author : Anass Yarroudh (ayarroudh@uliege.be), Geomatics Unit of ULiege
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
import psutil
from typing import List, Any, Union
import math
import collections
import shapely.geometry as geometry

class OrderedGroup(click.Group):
    def __init__(self, name=None, commands=None, **attrs):
        super(OrderedGroup, self).__init__(name, commands, **attrs)
        self.commands = commands or collections.OrderedDict()

    def list_commands(self, ctx):
        return self.commands

class Point(object):
    x: float
    y: float
    data: Any

    def __init__(self, x, y, data=None):
        self.x = x
        self.y = y
        self.data = data

    def __repr__(self):
        return '<Point: ({0},{1})>'.format(self.x, self.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

class Bounds(object):
    x: float
    y: float
    width: float
    height: float

    def __init__(self, x: float, y: float, width: float = 0, height: float = 0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def __repr__(self):
        xmin, xmax, ymin, ymax = self.get_bbox()
        return '<Bounds: [{},{},{},{}]>'.format(xmin, xmax, ymin, ymax)

    def get_bbox(self):
        return [self.x, self.x + self.width, self.y, self.y + self.height]

    def intersects(self, other):
        self_xmin = self.x
        self_xmax = self.x + self.width
        self_ymin = self.y
        self_ymax = self.y + self.height
        other_xmin = other.x
        other_xmax = other.x + other.width
        other_ymin = other.y
        other_ymax = other.y + other.height

        if self_xmax < other_xmin:
            return False
        if self_xmin > other_xmax:
            return False
        if self_ymax < other_ymin:
            return False
        if self_ymin > other_ymax:
            return False
        return True

    def contain_point(self, point: Point):
        self_xmin = self.x
        self_xmax = self.x + self.width
        self_ymin = self.y
        self_ymax = self.y + self.height

        if point.x < self_xmin:
            return False
        if point.x > self_xmax:
            return False
        if point.y < self_ymin:
            return False
        if point.y > self_ymax:
            return False
        return True

def euclid_compare(one: Union[Bounds, Point], another: Union[Bounds, Point]) -> float:
    return (one.x - another.x)**2 + (one.y - another.y)**2

def euclid_distance(one: Union[Bounds, Point], another: Union[Bounds, Point]) -> float:
    return math.sqrt(euclid_compare(one, another))

class QuadTree(object):
    def __init__(self, bounds: Bounds, max_objects: int = 100, max_level: int = 4, level: int = 0):
        self.__max_objects = max_objects
        self.__max_levels = max_level
        self.__level = level
        self.__bounds = bounds
        self.__nodes = []
        self.__objects = []

    def __repr__(self):
        return "<QuadTree: ({}, {}), {}x{}>".format(self.__bounds.x, self.__bounds.y, self.__bounds.width, self.__bounds.height)

    def __iter__(self):
        for obj in self.__objects:
            yield obj
        if not self.__is_leaf():
            for i in range(len(self.__nodes)):
                yield from self.__nodes[i]

    def __is_leaf(self):
        return not self.__nodes

    @property
    def node_num(self):
        return self.__total_nodes()

    def __total_nodes(self) -> int:
        total = 0
        if self.__nodes:
            for i in range(len(self.__nodes)):
                total += 1
                total += self.__nodes[i].__total_nodes()
        return total

    def clear(self):
        self.__objects = []
        if self.__nodes:
            for i in range(len(self.__nodes)):
                self.__nodes[i].clear()
        self.__nodes = []

    def split(self):
        sub_width = self.__bounds.width / 2
        sub_height = self.__bounds.height / 2
        x = self.__bounds.x
        y = self.__bounds.y
        next_level = self.__level + 1

        self.__nodes.append(QuadTree(
            Bounds(x + sub_width, y, sub_width, sub_height),
            self.__max_objects,
            self.__max_levels,
            next_level)
        )

        self.__nodes.append(QuadTree(
            Bounds(x, y, sub_width, sub_height),
            self.__max_objects,
            self.__max_levels,
            next_level)
        )

        self.__nodes.append(QuadTree(
            Bounds(x, y + sub_height, sub_width, sub_height),
            self.__max_objects,
            self.__max_levels,
            next_level)
        )

        self.__nodes.append(QuadTree(
            Bounds(x + sub_width, y + sub_height, sub_width, sub_height),
            self.__max_objects,
            self.__max_levels,
            next_level)
        )

    def get_index(self, bounds: Union[Bounds, Point]):
        index = -1
        vertical_midpoint = self.__bounds.x + (self.__bounds.width / 2)
        horizontal_midpoint = self.__bounds.y + (self.__bounds.height / 2)
        is_north = bounds.y < horizontal_midpoint
        is_south = bounds.y > horizontal_midpoint
        is_west = bounds.x < vertical_midpoint
        is_east = bounds.x > vertical_midpoint

        if is_east and is_north:
            index = 0
        elif is_west and is_north:
            index = 1
        elif is_west and is_south:
            index = 2
        elif is_east and is_south:
            index = 3
        return index

    def insert(self, bounds: Union[Bounds, Point]):
        if self.__nodes:
            index = self.get_index(bounds)
            if index != -1:
                self.__nodes[index].insert(bounds)
                return
        self.__objects.append(bounds)
        if len(self.__objects) > self.__max_objects and self.__level < self.__max_levels:
            if not self.__nodes:
                self.split()
            for i in range(len(self.__objects)):
                index = self.get_index(self.__objects[i])
                if index != -1:
                    self.__nodes[index].insert(self.__objects[i])
            self.__objects.clear()

    def retrieve(self, bounds: Union[Bounds, Point]) -> List[Bounds]:
        index = self.get_index(bounds)
        return_objects = self.__objects

        if not self.__is_leaf():
            if index != -1:
                return_objects.extend(self.__nodes[index].retrieve(bounds))
            else:
                for i in range(len(self.__nodes)):
                    return_objects.extend(self.__nodes[i].retrieve(bounds))
        return return_objects

    def retrieve_intersections(self, bounds: Bounds) -> List[Union[Bounds, Point]]:
        found_bounds = []
        potentials: List[Union[Bounds, Point]] = self.retrieve(bounds)
        for i in range(len(potentials)):
            if isinstance(potentials[0], Bounds):
                if bounds.intersects(potentials[i]):
                    found_bounds.append(potentials[i])
            if isinstance(potentials[0], Point):
                if bounds.contain_point(potentials[i]):
                    found_bounds.append(potentials[i])
        return found_bounds

    def find(self, bounds: Union[Bounds, Point]) -> List[int]:
        index = self.get_index(bounds)
        if index != -1:
            self.__indices.append(index)
        if self.__nodes:
            index = self.get_index(bounds)
            if index != -1:
                self.__nodes[index].find(bounds)
        return self.__indices

    def contains_point(self, point: Point) -> bool:
        if self.__is_leaf():
            if self.__bounds.x <= point.x <= self.__bounds.x + self.__bounds.width and self.__bounds.y <= point.y <= self.__bounds.y + self.__bounds.height:
                return True
        return False

    def nearest_neighbors(self, point: Point, radius: float, max_num: int = 10, search_type: str = 'rectangle') -> List[Point]:
        nearest_results = []
        search_results = []
        if search_type == 'rectangle':
            bounds = Bounds(point.x - radius, point.y - radius, radius * 2, radius * 2)
            search_results.extend(self.retrieve_intersections(bounds))
        elif search_type == 'circle':
            pass
        nearest_results.extend(sorted(search_results, key=lambda another: euclid_compare(point, another)))
        return nearest_results[:max_num]

    def create(self):
        df = gpd.GeoDataFrame(columns=['geometry'], geometry='geometry')

        def draw_all_nodes(node):

            if (node.__is_leaf()==False):
                draw_rect(node)
                for i in range(len(node.__nodes)):
                    draw_rect(node.__nodes[i])
                    draw_all_nodes(node.__nodes[i])

        def draw_rect(node):
            if (node.__is_leaf()):
                df.loc[len(df.index)] = [geometry.box(node.__bounds.x, node.__bounds.y, node.__bounds.x + node.__bounds.width, node.__bounds.y + node.__bounds.height)]

        draw_all_nodes(self)
        return df

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

def geoflow(config, i):
    script = 'geof {}'.format(config)
    os.system(script)
    print('.done tile_{}'.format(i))

@click.group(cls=OrderedGroup, help="CLI tool to manage full optimized reconstruction of large-scale 3D building models.")
def cli():
    pass

@click.command()
@click.argument('footprints', type=click.Path(exists=True), required=False)
@click.option('--output', help='Output directory.', type=click.Path(exists=False), default="./output", show_default=True)
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
@click.option('--output', help='Output directory.', type=click.Path(exists=False), default="./output", show_default=True)

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

    with open('{}\\config.json'.format(tmp),'w') as file:
        json.dumps(json.dump(config, file, indent=2))

    os.system('entwine build -c {}\\config.json'.format(tmp))

@click.command()
@click.option('--areas', help='The calculated processing areas.', type=click.Path(exists=True), default="./output/processing_areas.gpkg", show_default=True)
@click.option('--indexed', help='Indexed 3D point cloud directory.', type=click.Path(exists=True), default="./output/indexed_pointcloud", show_default=True)
@click.option('--output', help='Output directory.', type=click.Path(exists=False), default="./output", show_default=True)

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
@click.option('--pointcloud', help='3D point cloud tiles directory.', type=click.Path(exists=True), default="./output/pointcloud_tiles", show_default=True)
@click.option('--footprints', help='2D building footprints tiles directory.', type=click.Path(exists=True), default="./output/footprint_tiles", show_default=True)
@click.option('--output', help='Output directory.', type=click.Path(exists=False), default="./output", show_default=True)

def reconstruct(footprints, pointcloud, output):
    '''
    Optimized 3D reconstruction of buildings using GeoFlow.
    '''

    start = time.time()

    with open("config/reconstruct_.json") as file:
        reconstruct_ = json.load(file)

    with open("config/reconstruct.json") as file:
        reconstruct = json.load(file)

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

    commands = []
    for j in range(len(os.listdir('{}/pointcloud_tiles'.format(output)))):
        commands.append("geof {}/flowcharts/reconstruct{}.json".format(output, j))

    # # define a function to run the commands in parallel
    # def run_commands(commands):
    #     if os.name == 'nt': # if running on Windows
    #         for cmd in commands:
    #             subprocess.Popen(f'start cmd /c {cmd}', shell=True)
    #     else: # if running on Linux/Unix
    #         for cmd in commands:
    #             subprocess.Popen(['gnome-terminal', '-e', cmd])

    # # run the commands in parallel
    # run_commands(commands)

    processes = [multiprocessing.Process(target=geoflow, args=('{}/flowcharts/reconstruct{}.json'.format(output, j), j)) for j in range(len(os.listdir('{}/pointcloud_tiles'.format(output))))]

    for k, process in enumerate(processes):
        while (psutil.virtual_memory()[2] > 90):
            time.sleep(2)
        process.start()

    for process in processes:
        process.join()

    end = time.time()
    processTime = end - start

    print("All buildings reconstructed successfully")
    click.echo("Time: {}".format(time.strftime("%H:%M:%S", time.gmtime(processTime))))

@click.command()
@click.option('--cityjson', help='CityJSON files directory.', type=click.Path(exists=True), default="./output/model/cityjson", show_default=True)

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
