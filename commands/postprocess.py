# Copyright (c) 2022-2023 - University of Liège
# Author : Anass Yarroudh (ayarroudh@uliege.be), Geomatics Unit of ULiege
# This file is distributed under the BSD-3 licence. See LICENSE file for complete text of the license.

import click
import json
import copy
import time

@click.command()
@click.option('--cityjson', help='CityJSON files directory.', type=click.Path(exists=True), default="./output/model/cityjson", show_default=True)
@click.option('--output', help='Output directory.', type=click.Path(exists=False), default="./output", show_default=True)

def post(cityjson, output):
    '''
    Post-processing generated CityJSON files.
    '''
    start = time.time()

    for i, filename in enumerate(cityjson):
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
                    
        with open('{}/{}'.format(cityjson, filename)) as file:
            json.dump(twin, file, indent=2)

        print(".done: tile_{}.city.json".format(i))

    end = time.time()
    processTime = end - start

    print("All files corrected successfully")
    click.echo("Time: {}".format(time.strftime("%H:%M:%S", time.gmtime(processTime))))
