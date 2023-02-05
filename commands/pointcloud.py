# Copyright (c) 2022-2023 - University of Liège
# Author : Anass Yarroudh (ayarroudh@uliege.be), Geomatics Unit of ULiege
# This file is distributed under the BSD-3 licence. See LICENSE file for complete text of the license.

import click
import json
import os
import tempfile

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
