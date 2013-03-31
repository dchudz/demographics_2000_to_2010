import pandas
import os
import json
import random

def weighted_choice(weights):
  #http://eli.thegreenplace.net/2010/01/22/weighted-random-generation-in-python/
    rnd = random.random() * sum(weights)
    for i, w in enumerate(weights):
        rnd -= w
        if rnd < 0:
            return i

def get_random_group_from_census(df, row_index):
# A35AA:       Persons: Hispanic or Latino origin
# AF0AA:       Persons: Not Hispanic or Latino ~ Of one race
# AF0AB:       Persons: Not Hispanic or Latino ~ White (single race)
# AF0AC:       Persons: Not Hispanic or Latino ~ Black or African American (single race)
# AF0AD:       Persons: Not Hispanic or Latino ~ American Indian and Alaska Native (single race)
# AF0AE:       Persons: Not Hispanic or Latino ~ Asian (single race)
# AF0AF:       Persons: Not Hispanic or Latino ~ Native Hawaiian and Other Pacific Islander (single race)
# AF0AG:       Persons: Not Hispanic or Latino ~ Some Other Race (single race)
# AF0AH:       Persons: Not Hispanic or Latino ~ Two or More Races
	groups = ["hispanic", "white", "black", "asian", "other"]
	group_weights =[0 for item in groups]
	group_weights[groups.index("hispanic")] = df.A35AA[row_index]
	group_weights[groups.index("white")] = df.AF0AB[row_index]
	group_weights[groups.index("black")] = df.AF0AC[row_index]
	group_weights[groups.index("asian")] = df.AF0AE[row_index]
	group_weights[groups.index("other")] = df.AF0AD[row_index] +df.AF0AF[row_index] + df.AF0AG[row_index] + df.AF0AH[row_index]
	if sum(group_weights) > 0:
		choice = weighted_choice(group_weights)
		return groups[choice], sum(group_weights)
	else:
		return "no people!", 0


def subset_census_data_to_CA_only():
	if not os.path.exists("../data/census_CA.csv"):
		print "subsetting original data to CA only"
		census = pandas.read_csv("../data/nhgis0004_csv/nhgis0004_ts_tract.csv")
		census_SF = census[(census.STATEA == 6)]
		census_SF.to_csv("../data/census_CA.csv")
	else:
		census_SF = pandas.read_csv("../data/census_CA.csv")
	return census_SF

def subset_census_data_to_SF_only():
	if not os.path.exists("../data/census_SF.csv"):
		print "subsetting original data to SF only"
		census = pandas.read_csv("../data/nhgis0004_csv/nhgis0004_ts_tract.csv")
		census_SF = census[((census.STATEA == 6) & (census.COUNTYA == 75)) | ((census.STATEA == 17) & (census.COUNTYA == 31))]
		census_SF.to_csv("../data/census_SF.csv")
	else:
		census_SF = pandas.read_csv("../data/census_SF.csv")
	return census_SF

def process_demographic_for_year(year, infile, subsetting_function = subset_census_data_to_CA_only):
	print infile
	census = subsetting_function()
	print census
	with open(infile, "r") as random_points_file:
		random_points = json.load(random_points_file)
	tracts = []
	tract_weights = []
	for row_index in range(len(census)):
		if census.YEAR[row_index] == year:
			gis_join = census.GISJOIN[row_index]
			if gis_join in random_points.keys():
				for item in random_points[gis_join]:
					item['group'], sum_weights = get_random_group_from_census(census, row_index)
				tracts.append(gis_join)
				tract_weights.append(sum_weights)

	flat_points_list = []
	print "%d population: %d" % (year, sum(tract_weights))
	while True:
		choice = weighted_choice(tract_weights)
		tract = tracts[choice]
		point = random_points[tract].pop()
		if not random_points[tract]:
			break
		flat_points_list.append(point)
	flat_points_list = {'year' : year, 'population' : sum(tract_weights), 'points' : flat_points_list}
	return flat_points_list


if __name__ == '__main__':	
	flat_points_list2010 = process_demographic_for_year(2010, "../data/points_dict_2010.json")
	flat_points_list2000 = process_demographic_for_year(2000, "../data/points_dict_2000.json")
	with open("../data/flat_points_list.json", 'w') as outfile:
		outfile.write(json.dumps({'2000' : flat_points_list2000, '2010' : flat_points_list2010}))
