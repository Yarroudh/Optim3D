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
import xml.etree.ElementTree as ET

sys.path.append(os.path.dirname(__file__))
from utils import OrderedGroup, Point, Bounds, QuadTree, tile, run_command_in_terminal

from rich.console import Console
from rich.progress import Progress
from rich.tree import Tree

import warnings
warnings.filterwarnings('ignore')

copyright = """
Optim3D CLI tool is developed by the GeoScITY Lab of the University of Liège.
Licensed under the BSD 3-Clause License.
"""

@click.group(cls=OrderedGroup, help="CLI tool to manage full optimized reconstruction of large-scale 3D building models.")
def cli():
    pass

console = Console()

@click.command()
@click.option('--output', type=click.Path(), default="output", show_default=True, help="Output directory.")
@click.option('--footprint_tiles', type=click.Path(), default="footprint_tiles", show_default=True, help="Footprint tiles directory.")
@click.option('--indexed_pointcloud', type=click.Path(), default="indexed_pointcloud", show_default=True, help="Indexed pointcloud directory.")
@click.option('--model', type=click.Path(), default="model", show_default=True, help="Model directory.")
@click.option('--pointcloud_tiles', type=click.Path(), default="pointcloud_tiles", show_default=True, help="Pointcloud tiles directory.")
@click.option('--folder_structure', type=click.Path(), default="folder_structure.xml", show_default=True, help="Folder structure file.")

def prepare(output, footprint_tiles, indexed_pointcloud, model, pointcloud_tiles, folder_structure):
    """
    Prepare the output folder structure.
    """
    os.makedirs(os.path.join(output, footprint_tiles), exist_ok=True)
    os.makedirs(os.path.join(output, indexed_pointcloud, "ept-data"), exist_ok=True)
    os.makedirs(os.path.join(output, indexed_pointcloud, "ept-hierarchy"), exist_ok=True)
    os.makedirs(os.path.join(output, indexed_pointcloud, "ept-sources"), exist_ok=True)
    os.makedirs(os.path.join(output, model, "cityjson"), exist_ok=True)
    os.makedirs(os.path.join(output, model, "obj"), exist_ok=True)
    os.makedirs(os.path.join(output, pointcloud_tiles), exist_ok=True)

    # Create XML file to store folder hierarchy
    root = ET.Element("output_structure")
    ET.SubElement(root, "footprint_tiles").text = footprint_tiles
    ET.SubElement(root, "indexed_pointcloud").text = indexed_pointcloud
    ET.SubElement(root, "model").text = model
    ET.SubElement(root, "pointcloud_tiles").text = pointcloud_tiles

    tree = ET.ElementTree(root)
    tree.write(os.path.join(output, folder_structure))

    # Display the folder structure
    console.print(f"{copyright}")
    console.print("[bold cyan]Preparation of output folder structure[/bold cyan]\n")

    structure = Tree(f"{output}")
    structure.add(footprint_tiles)
    structure.add(indexed_pointcloud)
    structure.add(model)
    structure.add(pointcloud_tiles)

    console.print(structure)
    console.print(f"[green]\nOutput folder structure prepared at:[/green] {os.path.abspath(output)}")
    console.print(f"Please refer to [bold]{folder_structure}[/bold] for the folder structure.")



@click.command()
@click.argument("footprints", type=click.Path(exists=True), required=False)
@click.option("--output", type=click.Path(), default="output", show_default=True, help="Output directory.")
@click.option("--folder-structure", type=click.Path(), default="folder_structure.xml", show_default=True, help="Folder structure file.")
@click.option("--osm", nargs=4, type=float, default=(-1, -1, -1, -1), show_default=True, metavar=("WEST", "NORTH", "EAST", "SOUTH"), help="Download footprints from OSM in [west north east south] format.")
@click.option("--osm-save-path", type=click.Path(), default=None, help="Path to save downloaded OSM footprints (optional).")
@click.option("--quadtree-fname", type=click.Path(), default="quadtree.gpkg", show_default=True, help="Filename for the QuadTree file (forced to GPKG format).")
@click.option("--processing-areas-fname", type=click.Path(), default="processing_areas.gpkg", show_default=True, help="Filename for the processing areas file (forced to GPKG format).")
@click.option("--crs", type=int, help="Coordinate Reference System (EPSG).")
@click.option("--max", type=int, default=3500, show_default=True, help="Max number of buildings per tile.")

def index2d(footprints, output, folder_structure, osm, osm_save_path, quadtree_fname, processing_areas_fname, crs, max):
    """
    QuadTree indexing and tiling of 2D building footprints.
    """
    start_time = time.time()

    # Print header
    console.print(f"{copyright}")
    console.print("[bold cyan]QuadTree indexing and tiling of 2D building footprints[/bold cyan]\n")

    # Read folder structure XML file
    try:
        folder_structure = os.path.join(output, folder_structure) if not os.path.exists(folder_structure) else folder_structure
        tree = ET.parse(folder_structure)
    except ET.ParseError:
        console.print("[bold red]Error: {folder_structure} does not exist or is not a valid XML file.[/bold red]")
        return
    
    root = tree.getroot()
    tiles_path = root.find("footprint_tiles").text

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

    # Export QuadTree and read it back
    quadtree_path = os.path.join(output, quadtree_fname)
    quadTree.create().to_file(quadtree_path, driver="GPKG")
    boundings = gpd.read_file(quadtree_path)
    boundings.crs = buildings.crs

    # Spatial join (efficient replacement for nested loops)
    buildings = buildings.sjoin(boundings, how="left", predicate="intersects")
    buildings.rename(columns={"index_right": "node"}, inplace=True)

    # Group buildings by node and create bounding boxes
    grouped = buildings.drop(columns=["centroid"]).groupby("node")

    bbox_geoms = grouped.apply(lambda g: g.dissolve().boundary.iloc[0].envelope.buffer(10) if not g.dissolve().boundary.empty else None)
    bbox_gdf = gpd.GeoDataFrame(geometry=bbox_geoms, crs=f"EPSG:{crs}")
    processing_areas_path = os.path.join(output, processing_areas_fname)
    bbox_gdf.to_file(processing_areas_path, driver="GPKG")

    # Save individual footprint tiles
    with Progress() as progress:
        task = progress.add_task("[cyan]Tiling", total=len(grouped))
        for node, group in grouped:
            tile_path = f"{tiles_full_path}/tile_{node}.shp"
            group['OIDN'] = range(1, len(group) + 1)
            group.to_file(tile_path, encoding="utf-8")
            progress.update(task, advance=1)

    # Completion message with execution time
    elapsed_time = time.time() - start_time

    structure = Tree(output)
    structure.add(tiles_path)
    console.print(f"[green]\nQuadTree saved at:[/green] {os.path.abspath(quadtree_path)}")
    console.print(f"[green]Processing areas saved at:[/green] {os.path.abspath(processing_areas_path)}")
    console.print(f"[green]All tiles generated successfully and saved at:[/green] {os.path.abspath(tiles_full_path)}")
    console.print(structure)
    console.print(f"\nElapsed time: {time.strftime('%H:%M:%S', time.gmtime(elapsed_time))}")


@click.command()
@click.argument("pointcloud", type=str)
@click.option('--output', help='Output directory.', type=click.Path(exists=False), default="output", show_default=True)
@click.option('--folder-structure', type=click.Path(), default="folder_structure.xml", show_default=True, help="Folder structure file.")
@click.option('--threads', type=int, default=None, show_default=True, help="Number of threads for parallelization.")
@click.option('--force', type=bool, default=False, show_default=True, help="Force a new indexing.")
@click.option('--srs', type=int, default=None, show_default=True, help="Coordinate system for the point cloud [EPSG code].")
@click.option('--reprojection', type=int, default=None, show_default=True, help="Coordinate system reprojection for the point cloud [EPSG code].")
@click.option('--maxnodesize', type=int, default=None, show_default=True, help="Soft point count at which nodes may overflow.")
@click.option('--minnodesize', type=int, default=None, show_default=True, help="Soft minimum on the point count of nodes.")
@click.option('--cachesize', type=int, default=None, show_default=True, help="Number of recently-unused nodes to hold in reserve.")
@click.option('--kwargs', type=click.Path(exists=True), default=None, help="Additional keyword arguments for Entwine [.json].")

def index3d(pointcloud, folder_structure, output, threads, force, srs, reprojection, maxnodesize, minnodesize, cachesize, kwargs):
    """
    OcTree indexing of 3D point cloud using Entwine.
    """
    
    start_time = time.time()

    # Print header
    console.print(f"{copyright}")
    console.print("[bold cyan]OcTree indexing of 3D point cloud[/bold cyan]\n")

    # Print Entwine information
    console.print("The Entwine tool is used for indexing 3D point clouds.")
    console.print("Please ensure that Entwine is installed on your system.")
    console.print("For more information, visit: https://entwine.io/\n")

    # Check if Entwine is installed
    response = os.system("entwine --version")
    if response != 0:
        console.print("[bold red]Error: Entwine is not installed. Please install it using 'conda install -c conda-forge entwine'[/bold red]")
        return

    # Read folder structure XML file
    try:
        folder_structure = os.path.join(output, folder_structure) if not os.path.exists(folder_structure) else folder_structure
        tree = ET.parse(folder_structure)
    except ET.ParseError:
        console.print("[bold red]Error: {folder_structure} does not exist or is not a valid XML file.[/bold red]")
        return
    
    root = tree.getroot()
    tiles_path = root.find("indexed_pointcloud").text

    # Assert pointcloud is a valid file or directory
    if not os.path.exists(pointcloud):
        console.print(f"[bold red]Error: {pointcloud} does not exist.[/bold red]")
        return

    if os.path.isdir(pointcloud):
        if not any(os.scandir(pointcloud)):
            console.print(f"[bold red]Error: Directory {pointcloud} is empty.[/bold red]")
            return

    # Ensure output directories exist
    os.makedirs(output, exist_ok=True)
    tiles_full_path = os.path.join(output, tiles_path)
    os.makedirs(tiles_full_path, exist_ok=True)

    # Create temporary directory
    tmp = tempfile.mkdtemp()

    # Entwine configuration
    config = {
        "input": os.path.abspath(pointcloud),
        "output": os.path.abspath(tiles_full_path),
        "force": force
    }

    # Add options that are not None
    if threads:
        config["threads"] = threads
    if srs:
        config["srs"] = f"EPSG:{srs}"
    if reprojection:
        config["reprojection"] = {"out": f"EPSG:{reprojection}"}
    if maxnodesize:
        config["maxNodeSize"] = maxnodesize
    if minnodesize:
        config["minNodeSize"] = minnodesize
    if cachesize:
        config["cacheSize"] = cachesize

    # Allowed keyword arguments
    allowed = ["tmp", "dataType", "hierarchyType", "span", "allowOriginId", "bounds", "schema", "trustHeader", "absolute", "scale", "run", "subset", "overflowDepth", "hierarchyStep"]

    # Check for invalid keyword arguments
    if kwargs is not None:
        for key in kwargs:
            assert key in allowed, f"Invalid keyword argument: {key}"
        config.update(kwargs)

    # Save configuration to a file
    config_file = os.path.join(tmp, "config.json")
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)

    # Run Entwine and wait for completion
    command = f"entwine build -c {config_file}"
    run_command_in_terminal(command)

    # Completion message with execution time
    elapsed_time = time.time() - start_time
    structure = Tree(output)
    structure.add(tiles_path)
    console.print(f"[green]\n3D point cloud indexed successfully and saved at:[/green] {os.path.abspath(tiles_full_path)}")
    console.print(structure)
    console.print(f"\nElapsed time: {time.strftime('%H:%M:%S', time.gmtime(elapsed_time))}")



@click.command()
@click.option('--output', help='Output directory.', type=click.Path(exists=False), default="output", show_default=True)
@click.option('--folder-structure', type=click.Path(), default="folder_structure.xml", show_default=True, help="Folder structure file.")
@click.option('--areas', type=click.Path(), default="processing_areas.gpkg", show_default=True, help="Processing areas file.")
@click.option('--max-workers', type=int, default=os.cpu_count(), show_default=True, help="Maximum number of workers for tiling.")
@click.option('--crs', type=int, default=None, show_default=True, help="Coordinate system for the point cloud [EPSG code].")
@click.option('--reprojection', type=int, default=None, show_default=True, help="Coordinate system reprojection for the point cloud [EPSG code].")

def tile3d(areas, output, folder_structure, reprojection, max_workers):
    """
    Tiling of point cloud using the calculated processing areas.
    """

    start = time.time()

    # Print header
    console.print(f"{copyright}")
    console.print("[bold cyan]Tiling of point cloud using the calculated processing areas[/bold cyan]\n")

    # Read folder structure XML file
    try:
        folder_structure = os.path.join(output, folder_structure) if not os.path.exists(folder_structure) else folder_structure
        tree = ET.parse(folder_structure)
    except ET.ParseError:
        console.print("[bold red]Error: {folder_structure} does not exist or is not a valid XML file.[/bold red]")
        return
    
    root = tree.getroot()
    tiles_path = root.find("pointcloud_tiles").text
    tiles_full_path = os.path.join(output, tiles_path)
    indexed_path = root.find("indexed_pointcloud").text
    indexed_full_path = os.path.join(output, indexed_path)

    # Ensure the indexed point cloud exists
    assert os.path.exists(indexed_full_path), "Indexed point cloud directory not found"
    assert os.path.exists(os.path.join(indexed_full_path, "ept-data")), "ept-data not found in the indexed point cloud directory"
    assert os.path.exists(os.path.join(indexed_full_path, "ept-hierarchy")), "ept-hierarchy not found in the indexed point cloud directory"
    assert os.path.exists(os.path.join(indexed_full_path, "ept-sources")), "ept-sources not found in the indexed point cloud directory"
    assert os.path.exists(os.path.join(indexed_full_path, "ept-build.json")), "ept.json not found in the indexed point cloud directory"
    assert os.path.exists(os.path.join(indexed_full_path, "ept.json")), "ept.json not found in the indexed point cloud directory"
    
    # Check if areas file exists inside or outside the output directory
    areas = os.path.join(output, areas) if not os.path.exists(areas) else areas
    assert os.path.exists(areas), "Processing areas file not found"

    # Get CRS from ept.json
    if crs is None:
        with open(os.path.join(indexed_full_path, "ept.json")) as f:
            ept = json.load(f)
            crs = ept['srs']['horizontal'] if 'srs' in ept else None
            in_crs = f"EPSG:{crs}" if crs is not None else None
    else:
        in_crs = f"EPSG:{crs}"

    out_crs = f"EPSG:{reprojection}" if reprojection is not None else None

    # Ensure output directories exist
    os.makedirs(output, exist_ok=True)
    tiles_full_path = os.path.join(output, tiles_path)
    os.makedirs(tiles_full_path, exist_ok=True)

    # Load processing areas and indexed point cloud
    tiles = gpd.read_file(areas)

    # Use ThreadPoolExecutor for tiling the point cloud with tile function
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(tile, idx, tiles, indexed_full_path, tiles_full_path, in_crs, out_crs) for idx in range(len(tiles))]
        
        with Progress() as progress:
            task = progress.add_task("[cyan]Tiling point cloud", total=len(futures))
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    console.print(f"[bold red]Error: {e}[/bold red]")
                finally:
                    progress.update(task, advance=1)

    # Completion message with execution time
    elapsed_time = time.time() - start
    structure = Tree(output)
    structure.add(tiles_path)
    console.print(f"[green]\n3D point cloud tiled successfully and saved at:[/green] {os.path.abspath(tiles_full_path)}")
    console.print(structure)
    console.print(f"\nElapsed time: {time.strftime('%H:%M:%S', time.gmtime(elapsed_time))}")


@click.command()
@click.option('--output', help='Output directory.', type=click.Path(exists=False), default="output", show_default=True)
@click.option('--folder-structure', type=click.Path(), default="folder_structure.xml", show_default=True, help="Folder structure file.")
@click.option('--max-workers', type=int, default=os.cpu_count(), show_default=True, help="Maximum number of workers for reconstruction.")

def reconstruct(output, folder_structure, max_workers):
    """
    Optimized 3D reconstruction of buildings using GeoFlow.
    """

    start = time.time()

    # Print header
    console.print(f"{copyright}")
    console.print("[bold cyan]Optimized 3D reconstruction of buildings using GeoFlow[/bold cyan]\n")

    # Print GeoFlow information
    console.print("The GeoFlow-bundle tool is used for 3D reconstruction of buildings.")
    console.print("Please ensure that GeoFlow is installed on your system.")
    console.print("For more information, visit: https://github.com/geoflow3d/geoflow-bundle/\n")

    # Read folder structure XML file
    try:
        folder_structure = os.path.join(output, folder_structure) if not os.path.exists(folder_structure) else folder_structure
        tree = ET.parse(folder_structure)
    except ET.ParseError:
        console.print("[bold red]Error: {folder_structure} does not exist or is not a valid XML file.[/bold red]")
        return
    
    root = tree.getroot()
    footprints_path = root.find("footprint_tiles").text
    pointcloud_path = root.find("pointcloud_tiles").text
    model_path = root.find("model").text
    footprints_full_path = os.path.join(output, footprints_path)
    pointcloud_full_path = os.path.join(output, pointcloud_path)
    model_full_path = os.path.join(output, model_path)

    # Ensure output directories exist
    os.makedirs(model_full_path, exist_ok=True)
    os.makedirs(os.path.join(model_full_path, "cityjson"), exist_ok=True)
    assert os.path.exists(footprints_full_path), "Footprint tiles directory not found"
    assert os.path.exists(pointcloud_full_path), "Pointcloud tiles directory not found"

    # Load the configuration files
    config_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config')
    config_file = os.path.join(config_dir, 'reconstruct.json')
    config_file_ = os.path.join(config_dir, 'reconstruct_.json')

    # Copy the config files to the output directory
    script_dir = os.getcwd()
    shutil.copy(config_file, os.path.join(script_dir, 'reconstruct.json'))
    shutil.copy(config_file_, os.path.join(script_dir, 'reconstruct_.json'))

    commands = [
        f"geof reconstruct.json --input_footprint={footprints_full_path}/tile_{i}.shp --input_pointcloud={pointcloud_full_path}/tile_{i}.las --output_cityjson={output}/model/cityjson/tile_{i}.city.json"
        for i in range(len(os.listdir(f"{output}/pointcloud_tiles")))
    ]

    # Using ThreadPoolExecutor for managing concurrent execution
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []

        for cmd in commands:
            futures.append(executor.submit(run_command_in_terminal, cmd))

        with Progress() as progress:
            task = progress.add_task("[cyan]Reconstructing buildings", total=len(futures))
            for future in as_completed(futures):
                try:
                    future.result()  # Check if any exceptions occurred in the threads
                except Exception as e:
                    console.print(f"[bold red]Error with command execution: {e}[/bold red]")
                finally:
                    progress.update(task, advance=1)

    # Delete the config files after execution
    os.remove(os.path.join(script_dir, 'reconstruct.json'))
    os.remove(os.path.join(script_dir, 'reconstruct_.json'))

    # Completion message with execution time
    elapsed_time = time.time() - start
    structure = Tree(output)
    structure.add(model_path)
    console.print(f"[green]\n3D buildings reconstructed successfully and saved at:[/green] {os.path.abspath(model_full_path)}")
    console.print(structure)
    console.print(f"\nElapsed time: {time.strftime('%H:%M:%S', time.gmtime(elapsed_time))}")


@click.command()
@click.option('--output', help='Output directory.', type=click.Path(exists=False), default="output", show_default=True)
@click.option('--folder-structure', type=click.Path(), default="folder_structure.xml", show_default=True, help="Folder structure file.")

def post(output, folder_structure):
    """
    Postprocess the generated CityJSON files.
    """
    start = time.time()

    # Print header
    console.print(f"{copyright}")
    console.print("[bold cyan]Postprocessing CityJSON files[/bold cyan]\n")

    # Read folder structure XML file
    try:
        folder_structure = os.path.join(output, folder_structure) if not os.path.exists(folder_structure) else folder_structure
        tree = ET.parse(folder_structure)
    except ET.ParseError:
        console.print("[bold red]Error: {folder_structure} does not exist or is not a valid XML file.[/bold red]")
        return
    
    root = tree.getroot()
    model_path = root.find("model").text
    cityjson_path = os.path.join(model_path, "cityjson")
    model_full_path = os.path.join(output, model_path)
    cityjson_full_path = os.path.join(output, cityjson_path)

    # Ensure output directories exist
    assert os.path.exists(model_full_path), "Model directory not found"
    assert os.path.exists(cityjson_full_path), "CityJSON directory not found"

    # Postprocess the CityJSON files
    with Progress() as progress:
        task = progress.add_task("[cyan]Postprocessing CityJSON files", total=len(os.listdir(cityjson_full_path)))
        for i, filename in enumerate(os.listdir(cityjson_full_path)):
            with open(os.path.join(cityjson_full_path, filename)) as file:
                data = json.load(file)
                twin = copy.deepcopy(data)

                for key, value in data['CityObjects'].items():
                    children = twin['CityObjects'][key].get('children')
                    parents = twin['CityObjects'][key].get('parents')

                    if children:
                        for j in range(len(children)):
                            children[j] = f'T{i}_{children[j]}'

                    if parents:
                        for j in range(len(parents)):
                            parents[j] = f'T{i}_{parents[j]}'

                    twin['CityObjects'][f'T{i}_{key}'] = twin['CityObjects'].pop(key)

            with open(os.path.join(cityjson_full_path, filename), 'w') as file:
                json.dump(twin, file, indent=2)

            progress.update(task, advance=1)
    
    # Completion message with execution time
    elapsed_time = time.time() - start
    structure = Tree(output)
    structure.add(model_path)
    console.print(f"[green]\nCityJSON files postprocessed successfully and saved at:[/green] {os.path.abspath(cityjson_full_path)}")
    console.print(structure)
    console.print(f"\nElapsed time: {time.strftime('%H:%M:%S', time.gmtime(elapsed_time))}")


cli.add_command(prepare)
cli.add_command(index2d)
cli.add_command(index3d)
cli.add_command(tile3d)
cli.add_command(reconstruct)
cli.add_command(post)


if __name__ == '__main__':
    cli(prog_name='optim3d')
