demographics_2000_to_2010
=========================

# Demo

# Why I used D3 for this

# Data

## Demographics

The data come from: Minnesota Population Center. National Historical Geographic Information System (https://www.nhgis.org/). To get it, you'll need to make an account. The demographic data is all in on CSV that you get by selecting the right tables. From their data description:

-------------------------------
Time series layout: Time varies by row
Geographic level:   Census Tract (by State--County)
Years:              1970, 1980, 1990, 2000, 2010
 
Tables:
 
1. Persons of Hispanic or Latino Origin
   Valid years in file: 1970, 1980, 1990, 2000, 2010
   Code: A35
 
2. Persons Who Are Not Hispanic or Latino by Race Combination [70]
   Valid years in file: 1990, 2000, 2010
   Code: AF0


## Shapefiles

You'll get shapefiles for 2000 and 2010. It's really nice that NHGIS picks out the right shapefiles for you. I've learned by getting burned once that "2000 census tract shapefiles" isn't completely unambiguous, for confusing reasons.

# Data processing

* First I (*create_random_points.py*) create a dictionary for each year whose keys are census tracts and whose values are lists of points within that census tract. like this: "{"G0600810609500": [{"lat": 37.50626816926859, "lon": -122.28318844914996}, {"lat": 37.50466208009152, "lon": -122.28494199026409}, ... }"
* Then I (*process_demographics_csv.py*) randomly assign points to demographics groups by:
 1. choosing a random tract (weighted by populations)
 2. taking the next point in the list of points in that tract
 3. assigning a random demographic group to that point according to the population proportions within the tract

This results in a data structure that looks like: 

{"2000": {"population": 4123740.0, "points": [{"lat": 37.974293937529644, "group": "hispanic", "lon": -122.3320905363558}, {"lat": 38.02111860511683, "group": "hispanic", "lon": -121.9181554520208}

