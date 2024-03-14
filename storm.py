from datetime import datetime
from typing import List, Optional
import geopandas as gpd
from shapely.geometry import (GeometryCollection, LineString, MultiLineString,
                              MultiPoint, Point)

from reading import Reading


class Storm:
    """
    A class for storing and processing information about a storm from the HURDAT2 dataset.
    """
    def __init__(self) -> None:
        # Initialize attributes for each storm
        self.code: Optional[str] = None  # Code of the storm
        self.name: Optional[str] = None  # Name of the storm
        self.count: Optional[int] = None  # Number of readings for the storm
        self.basin: Optional[str] = None  # Basin in which the storm occurred
        self.cyclone_number: Optional[int] = None  # Cyclone number of the storm
        self.year: Optional[int] = None  # Year of the storm
        self.readings: Optional[List[Reading]] = None  # List of readings for the storm
        self.intersection_point: Optional[Point] = None # Intersection point with the state
        self.max_wind_speed: Optional[int] = None # Max Wind Speed (Calculated Later)
        self.intersection_time: Optional[str] = None # Intersecion Point (Calculated Later)

    def read_values(self, line: str) -> None:
        """
        Parse a line from the HURDAT2 dataset and populate the attributes of the Storm instance.

        Parameters:
        - line (str): A line from the HURDAT2 dataset.

        Returns:
        - None
        """
        try:
             # Split the line by comma and assign values
            self.code, self.name, self.count, _ = line.strip().split(',')
            
            self.code = self.code.strip() # Strip whitespace from the code
            self.basin = self.code[0:2].strip() # Extract basin from the code
            self.cyclone_number = int(self.code[2:4]) # Extract cyclone number from the code
            self.year = int(self.code[4:8]) # Extract year from the code
            
            self.name = self.name.strip() # Strip whitespace from the name
            self.count = int(self.count) # Convert count to integer
            self.readings = [Reading() for i in range(self.count)] # Initialize the readings list
        except Exception as e:
            print(f"Error while reading values: {e}")
    
    def sort_readings(self) -> None:
        """
        Sort the readings of the storm by datetime in ascending order.

        Returns:
        - None
        """
        try:
            self.readings = sorted(self.readings, key=lambda r: r.datetime)
        except Exception as e:
            print(f"Error while sorting readings: {e}")
    
    def is_hurricane(self) -> bool:
        """
        Check if the storm is classified as a hurricane based on its readings.

        Returns:
        - bool: True if the storm is a hurricane, False otherwise.
        """
        try:
            #Iterate over readings
            for reading in self.readings:
                if reading.status == 'HU': # Return True if any reading has status 'HU' (hurricane)
                    return True
        except Exception as e:
            print(f"Error while checking if hurricane: {e}")
        return False # Return False if no reading has status 'HU'
                  
    def calculate_max_wind_speed(self) -> int:
        """
        Calculate the maximum wind speed (in knots) among all readings of the storm.

        Returns:
        - int: Maximum wind speed
        """
        try:
            #Iterate over readings and return max wind speed
            return max(reading.msw_kts for reading in self.readings)
        except Exception as e:
            print(f"Error while calculating max wind speed: {e}")
            return 0
    
    def check_point_intersection(self, state_gdf: gpd.GeoDataFrame) -> bool:
        """
        Check if any point of the storm's path lies inside the specified state geometry.

        Parameters:
        - state_gdf (geopandas.GeoDataFrame): The geometry of the state to check for intersection.

        Returns:
        - bool: True if there is an intersection, False otherwise. 
        If True, also sets the values of  `max_wind_speed` and `intersection_time` attributes.
        """
        try:
            #Iterate through readings
            for reading in self.readings:
                # Create a point from the reading's longitude and latitude
                point = Point(reading.long, reading.lat)
                
                #If point lies inside state geometry
                if state_gdf.contains(point).any():
                    self.intersection_point = point  # Set the intersection point
                    self.max_wind_speed = self.calculate_max_wind_speed() # Calculate the maximum wind speed
                    self.intersection_time = reading.datetime # Set the intersection datetime
                    return True # Return True because found intersection
        
        except Exception as e:
            print(f"Error while checking point intersection: {e}")
        return False #Return False due to exception or no intersection
                 
    def check_line_intersection(self, state_gdf: gpd.GeoDataFrame) -> bool:
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
                reading_1 = self.readings[i] # Get the first reading of the pair
                reading_2 = self.readings[i+1] # Get the second reading of the pair

                # Create LineString from two consecutive points
                line_segment = LineString([(reading_1.long, reading_1.lat), (reading_2.long, reading_2.lat)])

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
                    self.max_wind_speed = self.calculate_max_wind_speed() 
                
                    # Interpolate the time of intersection based on the line segment and intersection point.
                    self.intersection_time = self.interpolate_time_line_intersection(reading_1, reading_2, intersection_point)
                    
                    return True #Return True because found intersection
        except Exception as e:
            print(f"Error while checking line intersection: {e}")
            return False #Return False due to exception
        return False #Return False due to no intersection

    def interpolate_time_line_intersection(self, reading_1: Reading, reading_2: Reading, intersection_point: Point) -> datetime:
        """
        Interpolate the time of intersection between a line segment of the storm's path and the state geometry.

        Parameters:
        - reading_1 (Reading): The first reading of the line segment.
        - reading_2 (Reading): The second reading of the line segment.
        - intersection_point (shapely.geometry.Point): The intersection point between the line segment and the state geometry.

        Returns:
        - datetime.datetime: The interpolated time of intersection.
        """
        try:
            # Calculate the distances between the points
            distance_1_to_intersection = ((intersection_point.x - reading_1.long)**2 + (intersection_point.y - reading_1.lat)**2)**0.5
            distance_2_to_intersection = ((intersection_point.x - reading_2.long)**2 + (intersection_point.y - reading_2.lat)**2)**0.5
            
            # Calculate the total distance between the two readings
            total_distance = distance_1_to_intersection + distance_2_to_intersection

            # Calculate the ratio of the distances
            ratio = distance_1_to_intersection / total_distance

            # Calculate the time difference between dt1 and dt2
            time_difference = reading_2.datetime - reading_1.datetime

            # Interpolate the timestamp for the intersection point
            intersection_timestamp = reading_1.datetime + ratio * time_difference

            # Return the interpolated timestamp
            return intersection_timestamp
        except Exception as e:
            print(f"Error while interpolating time: {e}")
            return None
