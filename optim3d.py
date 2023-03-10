# Copyright (c) 2022-2023 - University of Liège
# Author : Anass Yarroudh (ayarroudh@uliege.be), Geomatics Unit of ULiege
# This file is distributed under the BSD-3 licence. See LICENSE file for complete text of the license.

import click
import collections
from commands import pointcloud, footprints, tiling, reconstruction

class OrderedGroup(click.Group):
    def __init__(self, name=None, commands=None, **attrs):
        super(OrderedGroup, self).__init__(name, commands, **attrs)
        self.commands = commands or collections.OrderedDict()

    def list_commands(self, ctx):
        return self.commands

@click.group(cls=OrderedGroup, help="CLI tool to manage full optimized reconstruction of large-scale 3D building models.")
def cli():
    pass

cli.add_command(pointcloud.index3d)
cli.add_command(footprints.index2d)
cli.add_command(tiling.tiler3d)
cli.add_command(reconstruction.reconstruct)

if __name__ == '__main__':
    cli(prog_name='optim3d')
