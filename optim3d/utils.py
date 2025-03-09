# Copyright (c) 2022-2023 - University of Liège
# Author : Anass Yarroudh (ayarroudh@uliege.be), GeoScITY Lab of ULiege
# This file is distributed under the BSD-3 licence. See LICENSE file for complete text of the license.

import click
import json
import os
import sys
import rich

env_base = sys.prefix
proj_lib_path = os.path.join(env_base, 'Library', 'share', 'proj')
os.environ['PROJ_LIB'] = proj_lib_path

import geopandas as gpd
import pdal
from typing import List, Any, Union
import math
import collections
import shapely.geometry as geometry
import psutil
import subprocess

def run_command_in_terminal(cmd):
    try:
        # Run the command directly without creating a new terminal window
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running command {cmd}: {e}")
    except Exception as e:
        print(f"Unexpected error running command {cmd}: {e}")

def memory_check():
    # Return the percentage of memory used
    return psutil.virtual_memory().percent

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

def tile(index, features, indexed_path, tiles_path, in_crs, out_crs):
    minx = features.bounds.iloc[index].minx
    maxx = features.bounds.iloc[index].maxx
    miny = features.bounds.iloc[index].miny
    maxy = features.bounds.iloc[index].maxy

    data ={
        "pipeline": [
            {
                "type": "readers.ept",
                "filename":f"{indexed_path}/ept.json",
                "bounds":f"([{minx},{maxx}],[{miny},{maxy}])"
            }
        ]
    }

    if in_crs is not None and out_crs is not None:
        data["pipeline"].append({
            "type":"filters.reprojection",
            "in_srs":in_crs,
            "out_srs":out_crs
        })

    data["pipeline"].append({
        "type":"writers.las",
        "filename":f"{tiles_path}/tile_{index}.las"
    })

    pipeline = pdal.Pipeline(json.dumps(data))
    pipeline.execute()