from typing import List
import geopandas as gpd
from storm import Storm

def run_analysis(dataset_file_path: str, 
                 state_gdf: gpd.GeoDataFrame, 
                 min_year: int, 
                 max_year: int, 
                 method: str) -> List[Storm]:
    """
    Run the analysis to identify hurricanes that made landfall in the specified state within a given year range.

    Parameters:
    - dataset_file_path (str): Path to the HURDAT2 dataset file.
    - state_gdf (geopandas.GeoDataFrame): The geometry of the state to check for landfall.
    - min_year (int): The minimum year to consider in the analysis.
    - max_year (int): The maximum year to consider in the analysis.
    - method (str): The method to use for checking intersection ('point' or 'line').

    Returns:
    - list: A list of Storm instances that made landfall in the specified state within the given year range.
    """
    # Initialize a list to store the final results
    landfall_hurricanes  = []
    
    try:
        #Open the dataset file
        with open(dataset_file_path, "r") as file:
            while True:
                # Read a line from the file
                line = file.readline()
                
                if not line:
                    break # Break the loop if the end of the file is reached
                    
                # Create a new Storm object
                storm = Storm()
                
                # Populate the storm's attributes
                storm.read_values(line)
                
                # Iterate over the number of readings for the storm
                for i in range(storm.count):
                    # Populate the reading's attributes
                    storm.readings[i].read_values(file.readline())
                    
                # Check if the storm's year is within the specified range
                if storm.year < min_year or storm.year > max_year:
                    # Skip the storm if it's not within the range
                    continue
                
                # Check if the storm is a hurricane
                if not storm.is_hurricane():
                    # Skip the storm if it's not a hurricane
                    continue
                    
                # Sort the storm's readings by datetime
                storm.sort_readings()                            
        
                # Check if the point method is specified
                if method == 'point':
                    makes_landfall = storm.check_point_intersection(state_gdf)
                
                # Check if the line method is specified
                elif method == 'line':
                    makes_landfall = storm.check_line_intersection(state_gdf)
                
                # Check if an intersection was found
                if makes_landfall:
                    # Append the result to the final answer list
                    landfall_hurricanes.append(storm)
                    
    except FileNotFoundError:
        print(f"File not found: {dataset_file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")
    
    # Return the final answer list
    return landfall_hurricanes 
