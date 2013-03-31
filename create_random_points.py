from osgeo import ogr
import random
import osgeo
import pyproj
import json

def subset_layer_to_initial_gisjoin(layer, initial_gisjoin_list):
  length = len(initial_gisjoin_list[0])
	features_to_keep = [feat for feat in layer if feat.GetFieldAsString(feat.GetFieldIndex("GISJOIN"))[0:length] in initial_gisjoin_list]
	return features_to_keep

def get_random_points_from_feature(feature, n):
	return [get_random_point_from_feature(feature) for i in range(n)]

def get_random_point_from_feature(feature):
	project = pyproj.Proj(r'+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +x_0=0 +y_0=0 +ellps=GRS80 +datum=NAD83 +units=m +no_defs')
	# project from "USA Contiguous Albers Equal Area Conic"
	
	geometry = feature.GetGeometryRef()
	point = None
	while not point or not feature.GetGeometryRef().Contains(point):
		minx, maxx, miny, maxy = geometry.GetEnvelope()
		x = random.uniform(minx,maxx)
		y = random.uniform(miny,maxy)
		point = ogr.Geometry(ogr.wkbPoint)
		point.SetPoint(0, x, y)
	lon, lat = project(x, y, inverse=True)
	return {'lon' : lon, 'lat' : lat}

def create_random_points_from_shapefile(
	infile,
	layer_name,
	initial_gisjoin_list,
	outfile_name,
	num_points_per_tract = 100
	):

	ds = ogr.Open(infile)
	layer = ds.GetLayerByName(layer_name)
	layer.ResetReading()
	SFlayer = subset_layer_to_initial_gisjoin(layer, initial_gisjoin_list)
	points_dict = {}
	for feature in SFlayer:
		points = get_random_points_from_feature(feature, num_points_per_tract)
		gisjoin = feature.GetFieldAsString(feature.GetFieldIndex("GISJOIN"))
		points_dict[gisjoin] = points
	with open(outfile_name, 'w') as outfile:
		outfile.write(json.dumps(points_dict))

def get_field_names(infile, layer_name):
	ds = ogr.Open(infile)
	layer = ds.GetLayerByName(layer_name)
	defn = layer.GetLayerDefn()
	feat = layer[10]
	print "\n"
	print feat.GetFieldAsString(feat.GetFieldIndex("GISJOIN"))[0:6]
	for i in range(defn.GetFieldCount()):
		#largely copied from:
		#http://www.gdal.org/ogr/ogr_apitut.html
		print defn.GetFieldDefn(i).GetName()
		field_defn = defn.GetFieldDefn(i)
		if field_defn.GetType() == ogr.OFTInteger:
			print "%d" % feat.GetFieldAsInteger(i)
		elif field_defn.GetType() == ogr.OFTReal:
			print "%.3f" % feat.GetFieldAsDouble(i)
		elif field_defn.GetType() == ogr.OFTString:
			print "%s" % feat.GetFieldAsString(i)
		else:
			print "%s" % feat.GetFieldAsString(i)

if __name__ == '__main__':
	initial_gisjoin_list = ["G060081", "G060041", "G060001", "G060013", "G060075"]
	#get_field_names("../data/nhgis0004_shape/tract_2000/US_tract_2000.shp","US_tract_2000")
	#get_field_names("../data/nhgis0004_shape/tract_2010/US_tract_2010.shp","US_tract_2010")
	print "starting 2010"
	create_random_points_from_shapefile(
		"../data/nhgis0004_shape/tract_2010/US_tract_2010.shp",
		"US_tract_2010",
		initial_gisjoin_list,
		"../data/points_dict_2010.json",
		num_points_per_tract = 300
		)
	print "starting 2000"
	create_random_points_from_shapefile(
		"../data/nhgis0004_shape/tract_2000/US_tract_2000.shp",
		"US_tract_2000",
		initial_gisjoin_list,
		"../data/points_dict_2000.json",
		num_points_per_tract = 300
		)
