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

class Reading:
    """
    A class for storing and processing readings from the HURDAT2 dataset.
    Each reading represents a single observation of a storm at a specific time.
    """
    def __init__(self):
        # Initialize instance variables
        self.datetime = None   # Date and time of the reading
        self.msw_kts = None    # Wind speed in knots
        self.lat = None        # Latitude
        self.long = None       # Longitude
        self.status = None     # Status of the reading (e.g., 'HU', 'TD')
    
    def read_values(self, line):
        """
        Parse a line from the HURDAT2 dataset and populate the attributes of the Reading instance.

        Parameters:
        - line (str): A line from the HURDAT2 dataset.

        Returns:
        - None
        """
        # Split the line into a list of values
        try:
            line = line.strip().split(',')

            #Strip any leading or trailing whitespaces
            line = [element.strip() for element in line]
            
            #Extract date and time values and parse them into a datetime object
            datestamp = line[0]
            timestamp = line[1]
            self.datetime = self.parse_date_time(datestamp,timestamp)
            
            # Set the status
            self.status = line[3]
            
            # Convert latitude and longitude to decimal degrees
            self.lat, self.long =  self.convert_coordinates(line[4], line[5])
            
            # Set the wind speed in knots
            self.msw_kts = float(line[6])
        except (IndexError, ValueError) as e:
            #Handle parsing errors
            print(f"Error reading values from line '{line}': {e}") # Return None to indicate an error
        
    def convert_coordinates(self, latitude, longitude):
        """
        Convert latitude and longitude coordinates to decimal degrees.

        Parameters:
        - latitude (str): Latitude in degrees, minutes, seconds format.
        - longitude (str): Longitude in degrees, minutes, seconds format.

        Returns:
        - tuple: A tuple containing the latitude and longitude in decimal degrees.
        """
        
        try:
            # Extract degrees and direction from latitude and longitude strings
            lat_deg, lat_dir = float(latitude[:-1]), latitude[-1]
            lon_deg, lon_dir = float(longitude[:-1]), longitude[-1]

            if lat_dir in ['S']:
                lat_deg *= -1 # Negate the value for south direction

            if lon_dir in ['W']:
                lon_deg *= -1 # Negate the value for west direction

            return lat_deg, lon_deg
        except (IndexError, ValueError) as e:
            #Handle parsing errors
            print(f"Error converting coordinates '{latitude}', '{longitude}': {e}")
            return None, None # Return None to indicate an error
    
    def parse_date_time(self,datestamp, timestamp):      
        """
        Parse date and time components into a datetime object.

        Parameters:
        - datestamp (str): Date in YYYYMMDD format.
        - timestamp (str): Time in HHMM format.

        Returns:
        - datetime.datetime: A datetime object representing the date and time.
        """
        try:
            # Parse date components
            year = int(datestamp[:4])
            month = int(datestamp[4:6])
            day = int(datestamp[6:])

            # Parse time components
            hour = int(timestamp[:2])
            minute = int(timestamp[2:])

            # Return datetime object
            return datetime(year, month, day, hour, minute)
        except (ValueError, IndexError) as e:
             # Handle parsing errors
            print(f"Error parsing date and time: {e}")
            return None  # Return None to indicate an error

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
        
def run_analysis(dataset_file_path, state_gdf, min_year, max_year, method):
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
                    # Break the loop if the end of the file is reached
                    break
                
                # Create a new Storm object
                storm = Storm()
                
                # Populate the storm's attributes
                storm.read_values(line)
                
                # Iterate over the number of readings for the storm
                for i in range(storm.count):
                    # Create a new Reading object
                    reading = Reading()
                    # Populate the reading's attributes
                    reading.read_values(file.readline())
                    # Assign the reading to the storm's readings list
                    storm.readings[i] = reading
                    
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

class AnalysisApp(tk.Tk):
    """
    A Tkinter GUI application for running the hurricane analysis and displaying the results.
    """
    def __init__(self):
        super().__init__() # Initialize the superclass
        self.title("Hurricane Analysis") # Set the title of the window
        self.geometry("600x400")  # Set the size of the window

        # Input fields with default values
        self.dataset_file_path = tk.StringVar(value="hurdat2-atl-02052024.txt")  # Dataset file path
        self.shapefile_path = tk.StringVar(value="cb_2018_12_bg_500k.shp")       # Shapefile path
        self.min_year = tk.IntVar(value=1900) # Minimum year
        self.max_year = tk.IntVar(value=2022)  # Maximum year
        self.method = tk.StringVar(value="point") # Method (point or line)

        try:
            self.state_gdf = gpd.read_file(self.shapefile_path.get()) # Read the shapefile
            self.state_gdf = self.state_gdf.dissolve() # Dissolve the shapefile into a single geometry
        except Exception as e:
            self.state_gdf = None
            print(f"Error loading shapefile: {e}")

        tk.Label(self, text="Dataset File Path:").grid(row=0, column=0, sticky="w") # Label for dataset file path
        tk.Entry(self, textvariable=self.dataset_file_path, width=50).grid(row=0, column=1, sticky="w") # Entry field for dataset file path
        tk.Button(self, text="Browse", command=lambda: self.browse_file("dataset")).grid(row=0, column=2, sticky="w") # Button to browse for dataset file

        tk.Label(self, text="Shapefile Path:").grid(row=1, column=0, sticky="w") # Label for shapefile path
        tk.Entry(self, textvariable=self.shapefile_path, width=50).grid(row=1, column=1, sticky="w")  # Entry field for shapefile path
        tk.Button(self, text="Browse", command=lambda: self.browse_file("shapefile")).grid(row=1, column=2, sticky="w") # Button to browse for shapefile

        tk.Label(self, text="Minimum Year:").grid(row=2, column=0, sticky="w")  # Label for minimum year
        tk.Entry(self, textvariable=self.min_year, width=10).grid(row=2, column=1, sticky="w") # Entry field for minimum year

        tk.Label(self, text="Maximum Year:").grid(row=3, column=0, sticky="w") # Label for maximum year
        tk.Entry(self, textvariable=self.max_year, width=10).grid(row=3, column=1, sticky="w") # Entry field for maximum year

        tk.Label(self, text="Method:").grid(row=4, column=0, sticky="w") # Label for method
        ttk.Combobox(self, textvariable=self.method, values=["point", "line"]).grid(row=4, column=1, sticky="w")  # Combobox for selecting the method

        tk.Button(self, text="Run Analysis", command=self.find_hurricanes_making_landfall).grid(row=5, column=1, pady=10, sticky="w") # Button to run the analysis

        # Canvas and scrollbars for the table
        self.canvas = tk.Canvas(self, width=560, height=200) # Canvas for the table
        self.v_scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview) # Vertical scrollbar
        self.h_scrollbar = tk.Scrollbar(self, orient="horizontal", command=self.canvas.xview) # Horizontal scrollbar
        self.canvas.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set) # Configure scrollbars
        self.canvas.grid(row=6, column=0, columnspan=3, sticky="nsew")  # Place the canvas in the grid
        self.v_scrollbar.grid(row=6, column=3, sticky="ns") # Place the vertical scrollbar in the grid
        self.h_scrollbar.grid(row=7, column=0, columnspan=3, sticky="ew") # Place the horizontal scrollbar in the grid

        # Create a frame inside the canvas for the table
        self.table_frame = tk.Frame(self.canvas) # Frame for the table
        self.canvas.create_window((0, 0), window=self.table_frame, anchor="n")  # Create a window inside the canvas for the table frame
        
        # Configure the grid to expand the table with the window
        self.grid_rowconfigure(6, weight=1)
        self.grid_columnconfigure(0, weight=1)   

    def browse_file(self, file_type):
        """
        Open a file dialog and set the file path for the selected file type (dataset or shapefile).

        Parameters:
        - file_type (str): The type of file to browse for ('dataset' or 'shapefile').

        Returns:
        - None
        """
        # Open a file dialog and set the file path for the selected file type
        
        # Open a file dialog and get the selected file path
        file_path = filedialog.askopenfilename()
        
        # Check if the file type is 'dataset'
        if file_type == "dataset":
            self.dataset_file_path.set(file_path) # Set the dataset file path
        
        # Check if the file type is 'shapefile'
        elif file_type == "shapefile":
            try:
                self.shapefile_path.set(file_path) # Set the shapefile path
                self.state_gdf = gpd.read_file(file_path) # Read the shapefile
                self.state_gdf = self.state_gdf.dissolve() # Dissolve the shapefile into a single geometry
            except Exception as e:
                self.state_gdf = None
                print(f"Error loading shapefile: {e}")

    def display_storm_plot(self, storm):
        """
        Open a popup window with a plot of the storm's path and the intersection point with the state.

        Parameters:
        - storm (Storm): The storm instance to plot.

        Returns:
        - None
        """
        
        storm_info = f"{storm.name} {storm.year}" # Combine the storm's name and year into a single string, for labelling

        popup_window = tk.Toplevel() # Create a new top-level window
        popup_window.title(storm_info) # Set the title of the popup window
        popup_window.geometry("1280x960") # Set the size of the popup window

        fig, ax = plt.subplots() # Create a figure and axes for the plot
        lats = [reading.lat for reading in storm.readings] # Extract latitudes from the storm's readings
        longs = [reading.long for reading in storm.readings] # Extract longitudes from the storm's readings
        
        # Plot the path of the storm
        ax.scatter(longs, lats, label='Path of Hurricane', color='blue', zorder=3) 

        #Loop to draw arrows that represent the movement of a storm between consecutive points
        for i in range(len(longs) - 1):
            dx = longs[i + 1] - longs[i] # Calculate the change in longitude between consecutive points
            dy = lats[i + 1] - lats[i]   # Calculate the change in latitude between consecutive points
            # Plot an arrow (quiver) showing the direction and magnitude of movement from one point to the next
            ax.quiver(longs[i], lats[i], dx, dy, angles='xy', scale_units='xy', scale=1, color='red', zorder=2)

        # Plot the boundary of the state
        self.state_gdf.plot(ax=ax, label='State Boundary', zorder=1)
        state_bounds = self.state_gdf.total_bounds  # Get the bounding box of the state_gdf
        x_margin = (state_bounds[2] - state_bounds[0]) * 0.3  # Calculate 30% margin for x-axis
        y_margin = (state_bounds[3] - state_bounds[1]) * 0.3 # Calculate 30% margin for y-axis
        ax.set_xlim(state_bounds[0] - x_margin, state_bounds[2] + x_margin)  # Set the limits for the x-axis (longitude)
        ax.set_ylim(state_bounds[1] - y_margin, state_bounds[3] + y_margin)  # Set the limits for the y-axis (latitude)

        # Plot the calculated landfall point
        ax.scatter(storm.intersection_point.x, storm.intersection_point.y, color='yellow', zorder=4, label='Calculated Landfall',marker = 'x')

        ax.legend()  # Add a legend to the plot  
    
        ax.set_xlabel('Longitude (°)') # Set the label for the x-axis
        ax.set_ylabel('Latitude (°)') # Set the label for the y-axis
     
        canvas = FigureCanvasTkAgg(fig, master=popup_window) # Create a canvas widget and display the plot in the popup window
        canvas.draw()  # Draw the figure on the canvas
        canvas.get_tk_widget().pack() # Pack the canvas widget in the popup window
        
        tk.Label(popup_window, text=storm_info).pack()  # Add a label with the storm's name and year to the popup window

    def find_hurricanes_making_landfall(self):
        # Run the calculations and display the results in the table
        dataset_file_path = self.dataset_file_path.get() # Get the dataset file path
        min_year = self.min_year.get() # Get the minimum year
        max_year = self.max_year.get() # Get the maximum year
        method = self.method.get() # Get the method

        # Check if all input fields are filled
        if dataset_file_path and min_year and max_year and method:
            try:
                min_year = int(min_year)
                max_year = int(max_year)
                
                if min_year > max_year:  # Year Validation: min_year must be <= max_year
                    raise ValueError("Minimum year must be less than or equal to maximum year.")
                
                if min_year < 0 or max_year < 0: # Year Validation: Cannot be Negative
                    raise ValueError("Year cannot be negative") 
                
                if method not in ["point", "line"]:  # Method Validation
                    raise ValueError("Invalid method selected.")

                table = run_analysis(dataset_file_path, self.state_gdf, min_year, max_year, method) # Run the analysis and get the results
                
                # Clear the previous table contents
                for widget in self.table_frame.winfo_children(): 
                    widget.destroy()
                headings = ["Name", "WindSpeed", "Landfall", "Grapher"]
                
                 # Create labels for the table headings
                for j, heading in enumerate(headings):
                    tk.Label(self.table_frame, text=heading, borderwidth=1, relief="solid",  font=tkFont.Font(weight="bold")).grid(row=0, column=j, sticky="nsew")
                
                for i, storm in enumerate(table, start=1): # Iterate over the rows in the table
                    name_entry  = tk.Entry(self.table_frame, borderwidth=1, relief="solid") # Create an entry widget for each value
                    name_entry.insert(0, storm.name) # Place the entry widget in the table
                    name_entry.grid(row=i, column=0, sticky="nsew")            
                    
                    max_wind_speed_entry = tk.Entry(self.table_frame, borderwidth=1, relief="solid")
                    max_wind_speed_entry.insert(0, str(storm.max_wind_speed)) # Place the entry widget in the table
                    max_wind_speed_entry.grid(row=i, column=1, sticky="nsew")  
                    
                    intersection_time_entry = tk.Entry(self.table_frame, borderwidth=1, relief="solid")
                    intersection_time_entry.insert(0, str(storm.intersection_time))
                    intersection_time_entry.grid(row=i, column=2, sticky="nsew") 

                    # Create a button to open the popup window for each storm
                    tk.Button(self.table_frame, text="Click to Graph!", command=lambda r=storm: self.display_storm_plot(r), borderwidth=1, relief="solid").grid(row=i, column=3, sticky="nsew")        
                
                self.table_frame.update_idletasks()  # Update the layout of the table frame
                self.canvas.config(scrollregion=self.canvas.bbox("all"))  # Update the scroll region of the canvas
            except Exception as e:
                # Clear the table and show the error message
                for widget in self.table_frame.winfo_children():
                    widget.destroy()
                tk.Label(self.table_frame, text=f"Error: {e}").grid(row=0, column=0)
        else:
            # Clear the previous output
            for widget in self.output_frame.winfo_children():
                widget.destroy()
            tk.Label(self.output_frame, text="Please fill in all fields.").grid(row=0, column=0)

if __name__ == "__main__":
    app = AnalysisApp() # Create an instance of the AnalysisApp class
    app.mainloop() # Start the Tkinter event loop