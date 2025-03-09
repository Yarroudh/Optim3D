import laspy

las = laspy.read('output/pointcloud_tiles/tile_0.las')

print(las.header.min)
print(las.header.max)