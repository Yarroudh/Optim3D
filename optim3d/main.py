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
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, as_completed
import shutil
import psutil
import sys

sys.path.append('./')
from optim3d.utils import OrderedGroup, Point, Bounds, QuadTree, euclid_compare, euclid_distance, tile, geoflow, run_command_in_terminal, memory_check

from rich.console import Console
from rich.progress import Progress

import warnings
warnings.filterwarnings('ignore')

@click.group(cls=OrderedGroup, help="CLI tool to manage full optimized reconstruction of large-scale 3D building models.")
def cli():
    pass

console = Console()

@click.command()
@click.argument("footprints", type=click.Path(exists=True), required=False)
@click.option("--output", type=click.Path(), default="output", show_default=True, help="Output directory.")
@click.option("--osm", nargs=4, type=float, default=(-1, -1, -1, -1), show_default=True,
              metavar=("WEST", "NORTH", "EAST", "SOUTH"), help="Download footprints from OSM in [west north east south] format.")
@click.option("--osm-save-path", type=click.Path(), default=None, help="Path to save downloaded OSM footprints (optional).")
@click.option("--tiles-path", type=click.Path(), default="footprint_tiles",
              show_default=True, help="Directory to save footprint tiles.")
@click.option("--quadtree-path", type=click.Path(), default=None,
              help="Custom path to save the QuadTree file (optional). If not provided, defaults to 'output/quadtree.gpkg'.")
@click.option("--crs", type=int, help="Coordinate Reference System (EPSG).")
@click.option("--max", type=int, default=3500, show_default=True, help="Max number of buildings per tile.")

def index2d(footprints, output, osm, osm_save_path, tiles_path, quadtree_path, crs, max):
    """
    QuadTree indexing and tiling of 2D building footprints.
    """
    start_time = time.time()

    # Ensure output directories exist
    os.makedirs(output, exist_ok=True)
    tiles_full_path = os.path.join(output, tiles_path)
    os.makedirs(tiles_full_path, exist_ok=True)

    # Load building footprints (from OSM or file)
    if osm != (-1, -1, -1, -1):
        console.print(f"[bold cyan]Downloading building footprints from OSM for bounding box: {osm}[/bold cyan]")
        buildings = ox.features.features_from_bbox(osm, tags={"building": True}).dropna(subset=["geometry"])
        buildings.crs = "EPSG:4326"

        if osm_save_path:
            buildings.to_file(osm_save_path, driver="GPKG")
            console.print(f"[green]Saved OSM footprints to {osm_save_path}[/green]")

    else:
        buildings = gpd.read_file(footprints, encoding="utf-8")

    # Handle CRS conversion
    buildings = buildings.to_crs(epsg=crs) if crs else buildings
    crs = buildings.crs.to_epsg()  # Ensure CRS is numeric EPSG format

    # Compute centroids (vectorized for performance)
    if buildings.crs.is_geographic:
        buildings = buildings.to_crs(epsg=3857)  # Re-project to a projected CRS (e.g., EPSG:3857)
    buildings["centroid"] = buildings.geometry.centroid
    centroids = buildings.centroid.apply(lambda p: [p.x, p.y]).tolist()

    # Compute bounding box
    bounds = buildings.total_bounds  # [minx, miny, maxx, maxy]
    width, height = bounds[2] - bounds[0], bounds[3] - bounds[1]

    # Build QuadTree with progress bar
    quadTree = QuadTree(Bounds(bounds[0], bounds[1], width, height), max_objects=max)

    with Progress() as progress:
        task = progress.add_task("[cyan]Building QuadTree", total=len(centroids))
        for point in centroids:
            quadTree.insert(Point(*point))
            progress.update(task, advance=1)

    # Set default QuadTree path if not provided
    if not quadtree_path:
        quadtree_path = os.path.join(output, "quadtree.gpkg")

    # Export QuadTree and read it back
    quadTree.create().to_file(quadtree_path, driver="GPKG")
    boundings = gpd.read_file(quadtree_path)
    boundings.crs = buildings.crs
    console.print(f"[green]QuadTree saved at {quadtree_path}[/green]")

    # Spatial join (efficient replacement for nested loops)
    buildings = buildings.sjoin(boundings, how="left", predicate="intersects")
    buildings.rename(columns={"index_right": "node"}, inplace=True)

    # Group buildings by node and create bounding boxes
    grouped = buildings.drop(columns=["centroid"]).groupby("node")

    console.print(f"[bold cyan]Generating processing areas and tiles[/bold cyan]")

    bbox_geoms = grouped.apply(lambda g: g.dissolve().boundary.iloc[0].envelope.buffer(10) if not g.dissolve().boundary.empty else None)
    bbox_gdf = gpd.GeoDataFrame(geometry=bbox_geoms, crs=f"EPSG:{crs}")
    bbox_gdf.to_file(f"{output}/processing_areas.gpkg", driver="GPKG")

    # Save individual footprint tiles
    with Progress() as progress:
        task = progress.add_task("[cyan]Saving footprint tiles", total=len(grouped))
        for node, group in grouped:
            tile_path = f"{tiles_full_path}/tile_{node}.shp"
            group['OIDN'] = range(1, len(group) + 1)
            group.to_file(tile_path, encoding="utf-8")
            progress.update(task, advance=1)

    # Completion message with execution time
    elapsed_time = time.time() - start_time
    console.print("\n[bold green]All tiles generated successfully![/bold green]")
    console.print(f"[yellow]Time: {time.strftime('%H:%M:%S', time.gmtime(elapsed_time))}[/yellow]")
@click.command()
@click.argument('pointcloud', type=click.Path(exists=True), required=True)
@click.option('--output', help='Output directory.', type=click.Path(exists=False), default="output", show_default=True)

def index3d(pointcloud, output):
    '''
    OcTree indexing of 3D point cloud using Entwine.
    '''

    os.makedirs(output, exist_ok=True)
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

    os.makedirs(output, exist_ok=True)
    os.makedirs(f"{output}/pointcloud_tiles", exist_ok=True)

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

    # Copy the config files to the output directory
    script_dir = os.getcwd()
    shutil.copy(config_file, os.path.join(script_dir, 'reconstruct.json'))
    shutil.copy(config_file_, os.path.join(script_dir, 'reconstruct_.json'))

    with open(config_file) as file:
        reconstruct = json.load(file)

    with open(config_file_) as file:
        reconstruct_ = json.load(file)

    os.makedirs(f'{output}/model', exist_ok=True)
    os.makedirs(f'{output}/model/cityjson', exist_ok=True)

    commands = [
        f"geof reconstruct.json --input_footprint={footprints}/tile_{i}.shp --input_pointcloud={pointcloud}/tile_{i}.las --output_cityjson={output}/model/cityjson/tile_{i}.city.json"
        for i in range(len(os.listdir(f"{output}/pointcloud_tiles")))
    ]

    # Using ThreadPoolExecutor for managing concurrent execution
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        futures = []

        for cmd in commands:
            # Ensure memory usage is below 90%
            while psutil.virtual_memory().percent > 90:
                print(f"Memory usage high: {psutil.virtual_memory().percent}%. Waiting...")
                time.sleep(2)  # Wait before checking memory again

            futures.append(executor.submit(run_command_in_terminal, cmd))

        # Wait for all futures to complete
        for future in as_completed(futures):
            try:
                future.result()  # Check if any exceptions occurred in the threads
            except Exception as e:
                print(f"Error with command execution: {e}")

    # Delete the config files after execution
    os.remove(os.path.join(script_dir, 'reconstruct.json'))
    os.remove(os.path.join(script_dir, 'reconstruct_.json'))

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
