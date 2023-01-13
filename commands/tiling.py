import click
import os
import json
import geopandas as gpd
import multiprocessing
import pdal

def tile(index, feature, path, output):
    minx = feature.bounds.minx
    maxx = feature.bounds.maxx
    miny = feature.bounds.miny
    maxy = feature.bounds.maxy
        
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

    print(".done: tile_{}.las", flush=True)


@click.command()
@click.argument('areas', type=click.Path(exists=True), required=True)
@click.option('--indexed', help='Indexed 3D point cloud directory.', type=click.Path(exists=True), default="./output/indexed_pointcloud", show_default=True)
@click.option('--output', help='Output directory.', type=click.Path(exists=False), default="./output", show_default=True)

def tiler3d(input, indexed, output):
    '''
    Tiling of 3D point cloud using calculated processing areas.
    '''
    
    if (os.path.exists(output)==False):
        os.mkdir(output)
    if (os.path.exists('{}\\pointcloud_tiles'.format(output))==False):
        os.mkdir('{}\\pointcloud_tiles'.format(output))  

    areas = gpd.read_file(input)

    processes = [multiprocessing.Process(target=tile, args=(i, row, indexed, output)) for i, row in areas.iterrows()]

    # Start all processes
    for process in processes:
        process.start()

    # Wait for all processes to complete
    for process in processes:
        process.join()

    print('All tiles generated successfully')