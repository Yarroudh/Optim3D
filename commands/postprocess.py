for i, filename in enumerate(os.listdir('{}/cityjson'.format(output))):
        with open('output/cityjson/{}'.format(filename)) as file:
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
                
                
        with open('{}/cityjson/{}'.format(output, filename), 'w') as file:
            json.dump(twin, file, indent=2)