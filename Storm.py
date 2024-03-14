from shapely.geometry import shape, Point, LineString, MultiPoint, MultiLineString, GeometryCollection
import geopandas as gpd
import matplotlib.pyplot as plt
from datetime import datetime
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import tkinter.font as tkFont
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from Reading import Reading

class Storm:
    """
    A class for storing and processing information about a storm from the HURDAT2 dataset.
    """

    def __init__(self):
        # Initialize attributes for each storm
        self.code = None # Code of the storm
        self.name = None # Name of the storm
        self.count = None # Number of readings for the storm
        self.basin = None # Basin in which the storm occurred
        self.cyclone_number = None # Cyclone number of the storm
        self.year = None # Year of the storm
        self.readings = None # List of readings for the storm
        self.intersection_point = None # Intersection point with the state
        self.max_wind_speed = None # Max Wind Speed (Calculated Later)
        self.intersection_time = None # Intersecion Point (Calculated Later)

    def read_values(self, line):
        """
        Parse a line from the HURDAT2 dataset and populate the attributes of the Storm instance.

        Parameters:
        - line (str): A line from the HURDAT2 dataset.

        Returns:
        - None
        """

        try:
            self.code, self.name, self.count, _ = line.strip().split(',') # Split the line by comma and assign values
            
            self.code = self.code.strip() # Strip whitespace from the code
            self.basin = self.code[0:2].strip() # Extract basin from the code
            self.cyclone_number = int(self.code[2:4]) # Extract cyclone number from the code
            self.year = int(self.code[4:8]) # Extract year from the code
            
            self.name = self.name.strip() # Strip whitespace from the name
            self.count = int(self.count) # Convert count to integer
            self.readings = [0] * self.count # Initialize the readings list with zeros
        except Exception as e:
            print(f"Error while reading values: {e}")
    
    def sort_readings(self):
        """
        Sort the readings of the storm by datetime in ascending order.

        Returns:
        - None
        """
        try:
            self.readings = sorted(self.readings, key=lambda r: r.datetime)
        except Exception as e:
            print(f"Error while sorting readings: {e}")
    
    def is_hurricane(self):
        """
        Check if the storm is classified as a hurricane based on its readings.

        Returns:
        - bool: True if the storm is a hurricane, False otherwise.
        """

        # Check if the storm is a hurricane (status 'HU')
        try:
            for reading in self.readings:
                if reading.status == 'HU': # Return True if any reading has status 'HU' (hurricane)
                    return True
        except Exception as e:
            print(f"Error while checking if hurricane: {e}")
        return False # Return False if no reading has status 'HU'
                  
    def calculate_max_wind_speed(self):
        """
        Calculate the maximum wind speed (in knots) among all readings of the storm.

        Returns:
        - None
        """
        try:
            self.max_wind_speed = max(reading.msw_kts for reading in self.readings)
        except Exception as e:
            print(f"Error while calculating max wind speed: {e}")
            return 0
    
    def check_point_intersection(self, state_gdf):
        """
        Check if any point of the storm's path lies inside the specified state geometry.

        Parameters:
        - state_gdf (geopandas.GeoDataFrame): The geometry of the state to check for intersection.

        Returns:
        - bool: True if there is an intersection, False otherwise. 
        If True, also sets the values of  `max_wind_speed` and `intersection_time` attributes.
        """
        try:
            for reading in self.readings:
                point = Point(reading.long, reading.lat) # Create a point from the reading's longitude and latitude
                if state_gdf.contains(point).any():
                    self.intersection_point = point  # Set the intersection point
                    self.calculate_max_wind_speed() # Calculate the maximum wind speed
                    self.intersection_time = reading.datetime # Set the intersection datetime
                    return True # Return True because found intersection
        except Exception as e:
            print(f"Error while checking point intersection: {e}")
        return False #Return False due to exception or no intersection
                 
    def check_line_intersection(self, state_gdf):
        """
        Check if any line segment of the storm's path intersects with the specified state geometry.

        Parameters:
        - state_gdf (geopandas.GeoDataFrame): The geometry of the state to check for intersection.

        Returns:
        - bool: True if there is an intersection, False otherwise.
        If True, also sets the values of  `max_wind_speed` and `intersection_time` attributes.
        """

        try:
            first_reading = Point(self.readings[0].long, self.readings[0].lat) # Create a point from the first reading's coordinates
            
            if state_gdf.contains(first_reading).any():
                # If the first point intersects with the state geometry, check for point intersection
                return self.check_point_intersection(state_gdf)
                
            # Iterate over each pair of consecutive points in the storm path.
            for i in range(self.count-1):
                reading1 = self.readings[i] # Get the first reading of the pair
                reading2 = self.readings[i+1] # Get the second reading of the pair

                # Create LineString from two consecutive points
                line_segment = LineString([(reading1.long, reading1.lat), (reading2.long, reading2.lat)])

                # Check if the line intersects the state geometry
                intersection_point = state_gdf.intersection(line_segment).any()

                if intersection_point:
                    if isinstance(intersection_point, Point):
                        # If it's a point, no further action is needed.
                        pass
        
                    elif isinstance(intersection_point, MultiPoint):
                        # For a single LineString, take the first point.
                        intersection_point = intersection_point.geoms[0]
                        
                    elif isinstance(intersection_point, LineString):
                        # For a single LineString, take the first point
                        intersection_point = Point(intersection_point.coords[0])

                    elif isinstance(intersection_point, (MultiLineString, GeometryCollection)):
                        # For MultiLineString or GeometryCollection, take the first point of the first geometry
                        first_geometry = next(iter(intersection_point.geoms))
                        if isinstance(first_geometry, LineString):
                            intersection_point = Point(first_geometry.coords[0])
                        else:
                            print("No valid intersection point found")
                    else:
                        # If the intersection type is unexpected, log it and return.
                        print("Unexpected intersection type:", type(intersection_point))
                        return
                    # Store the intersection point.
                    self.intersection_point = intersection_point     
                    
                    # Calculate the maximum wind speed of the storm.
                    self.calculate_max_wind_speed()
                
                    # Interpolate the time of intersection based on the line segment and intersection point.
                    self.intersection_time = self.interpolate_time_line_intersection(reading1, reading2, intersection_point)
                    
                    return True #Return True because found intersection
        except Exception as e:
            print(f"Error while checking line intersection: {e}")
        return False #Return False due to exception or no intersection

    def interpolate_time_line_intersection(self,reading1, reading2, intersection_point):
        """
        Interpolate the time of intersection between a line segment of the storm's path and the state geometry.

        Parameters:
        - reading1 (Reading): The first reading of the line segment.
        - reading2 (Reading): The second reading of the line segment.
        - intersection_point (shapely.geometry.Point): The intersection point between the line segment and the state geometry.

        Returns:
        - datetime.datetime: The interpolated time of intersection.
        """
        try:
            # Calculate the distances between the points
            distance_1_to_intersection = ((intersection_point.x - reading1.long)**2 + (intersection_point.y - reading1.lat)**2)**0.5
            distance_2_to_intersection = ((intersection_point.x - reading2.long)**2 + (intersection_point.y - reading2.lat)**2)**0.5
            
            # Calculate the total distance between the two readings
            total_distance = distance_1_to_intersection + distance_2_to_intersection

            # Calculate the ratio of the distances
            ratio = distance_1_to_intersection / total_distance

            # Calculate the time difference between dt1 and dt2
            time_difference = reading2.datetime - reading1.datetime

            # Interpolate the timestamp for the intersection point
            intersection_timestamp = reading1.datetime + ratio * time_difference

            # Return the interpolated timestamp
            return intersection_timestamp
        except Exception as e:
            print(f"Error while interpolating time: {e}")
            return None