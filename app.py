import geopandas as gpd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import tkinter.font as tkFont
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from storm import Storm
from run_analysis import run_analysis
import os

class AnalysisApp(tk.Tk):
    """
    A Tkinter GUI application for running the hurricane analysis and displaying the results.
    """
    def __init__(self) -> None:
        """
        Initializes the Hurricane Analysis application window with various input fields, buttons, and a table.

        The window is set up with a title and a predefined size. It contains input fields for the dataset file path,
        shapefile path, minimum year, maximum year, and the method of analysis (point or line). It also includes browse
        buttons for selecting the dataset and shapefile, a button to run the analysis, and a scrollable table to display
        the results.

        The shapefile is read and dissolved into a single geometry, and an error message is printed if there is an issue
        loading the shapefile. The table for displaying results is set up within a canvas with both vertical and horizontal
        scrollbars.

        Attributes:
            dataset_file_path (tk.StringVar): Variable to store the path of the dataset file.
            shapefile_path (tk.StringVar): Variable to store the path of the shapefile.
            min_year (tk.IntVar): Variable to store the minimum year for analysis.
            max_year (tk.IntVar): Variable to store the maximum year for analysis.
            method (tk.StringVar): Variable to store the selected method of analysis (point or line).
            state_gdf (geopandas.GeoDataFrame): GeoDataFrame to store the dissolved shapefile geometry.
            canvas (tk.Canvas): Canvas widget to hold the table for displaying results.
            v_scrollbar (tk.Scrollbar): Vertical scrollbar for the canvas.
            h_scrollbar (tk.Scrollbar): Horizontal scrollbar for the canvas.
            table_frame (tk.Frame): Frame widget to hold the contents of the table.
        """
        super().__init__() # Initialize the superclass
        self.title("Hurricane Analysis") # Set the title of the window
        self.geometry("648x864")  # Set the size of the window

        # Input fields with default values
        self.dataset_file_path = tk.StringVar(value=os.path.join("data", "hurdat2-atl-02052024.txt")) # Dataset file path
        self.shapefile_path = tk.StringVar(value=os.path.join("data", "cb_2018_12_bg_500k.shp"))  # Shapefile path

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

    def browse_file(self, file_type: str) -> None:
        """
        Open a file dialog and set the file path for the selected file type (dataset or shapefile).

        Parameters:
        - file_type (str): The type of file to browse for ('dataset' or 'shapefile').

        Returns:
        - None
        """      
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
                # If an exception occurs, set state_gdf to None and print an error message
                self.state_gdf = None
                print(f"Error loading shapefile: {e}")

    def display_storm_plot(self, storm: Storm) -> None:
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
        popup_window.geometry("600x600") # Set the size of the popup window

        fig, ax = plt.subplots(figsize=(8, 6)) # Create a figure and axes for the plot
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

        ax.set_title(storm_info)  # Set the title of the plot
     
        # Calculate the dimensions for the canvas widget
        canvas_width = int(popup_window.winfo_width() * 0.8)
        canvas_height = int(popup_window.winfo_height() * 0.8)

        canvas = FigureCanvasTkAgg(fig, master=popup_window) # Create a canvas widget and display the plot in the popup window
        canvas.draw()  # Draw the figure on the canvas
        canvas.get_tk_widget().pack() # Pack the canvas widget in the popup window
        
    def find_hurricanes_making_landfall(self) -> None:
        """
        Run the calculations and display the results in the table.

        Parameters:
        - None

        Returns:
        - None
        """   
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
                          
                 # Create labels for the table headings
                headings = ["Name", "Max Wind Speed (knots)", "Landfall Date/Time", "Grapher"]
                for j, heading in enumerate(headings):
                    tk.Label(self.table_frame, text=heading, borderwidth=1, relief="solid",  font=tkFont.Font(weight="bold")).grid(row=0, column=j, sticky="nsew")
                
                # Iterate over the rows in the table
                for i, storm in enumerate(table, start=1): 
                    # Create an entry widget for each value, and place the entry widgets in the table
                    name_entry  = tk.Entry(self.table_frame, borderwidth=1, relief="solid", justify="center") 
                    name_entry.insert(0, storm.name) 
                    name_entry.grid(row=i, column=0, sticky="nsew")            
                    
                    max_wind_speed_entry = tk.Entry(self.table_frame, borderwidth=1, relief="solid", justify="center")
                    max_wind_speed_entry.insert(0, str(storm.max_wind_speed))
                    max_wind_speed_entry.grid(row=i, column=1, sticky="nsew")  
                    
                    intersection_time_entry = tk.Entry(self.table_frame, borderwidth=1, relief="solid", justify="center")
                    intersection_time_entry.insert(0, str(storm.intersection_time))
                    intersection_time_entry.grid(row=i, column=2, sticky="nsew") 

                    # Create a button to open the popup window for each storm
                    tk.Button(
                        self.table_frame, 
                        text="Click to Graph!", 
                        command=lambda r=storm: self.display_storm_plot(r), 
                        borderwidth=1, 
                        relief="solid", 
                        bg="grey",  
                        foreground="white"
                    ).grid(row=i, column=3, sticky="nsew")        
                
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
