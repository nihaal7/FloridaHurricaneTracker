# FloridaHurricaneTracker

## KCC – Software Development Technical Assignment

**Task:** The NOAA Best Track Data (HURDAT2) contains historical data on storms, including their paths and intensities. The objective of this analysis is to identify all hurricanes that have made landfall in Florida since 1900 and to generate a report listing their names, dates of landfall, and maximum wind speeds.

**Submitted by:** Nihaal Subhash
nihaal.subhash@gmail.com

## Installation

To set up the project, follow these steps:

1. Clone the repository:
```
git clone https://github.com/nihaal7/FloridaHurricaneTracker`
```

2. Install the required dependencies:
```
pip install -r requirements.txt
```

3. Data Preparation 
Make sure the following files are located in the data folder within the project directory:
```
Dataset File: hurdat2-atl-02052024.txt
Shape File: cb_2018_12_bg_500k.shp
```
The application expects these files to be present in order to function properly.

4. To run the application, execute the following command:
```
python app.py
```

## Data Parsing
The HURDAT2 dataset is structured as a text file with each hurricane's data spread across multiple lines. The first line contains the hurricane's identifier, name, and the number of data entries, while subsequent lines contain data entries for different timestamps. The Reading class is used to represent individual data entries, and the Storm class represents the storm’s metadata and holds a list of Reading objects. The parsing logic involves reading the file line by line, creating Reading objects for each data entry, and associating them with the corresponding Storm object.

## Filtering

### Filtering based on storm classification
In the provided code, the "HU" tag is used to identify whether a particular storm is classified as a hurricane at any point during its recorded path. The is_hurricane method within the Storm class is responsible for this identification. It examines each reading (data point) associated with the storm to determine if the status is "HU", which denotes hurricane intensity.

### Filtering based on year
In the provided code, filtering based on the year is performed when processing each storm's data in the run_analysis function. Specifically, after reading and parsing the storm data the code checks if the storm's year falls within the specified range (given by min_year and max_year parameters). 

For the given task of identifying all hurricanes that have made landfall in Florida since 1900, you would set the min_year value to 1900 and the max_year value to the current year or the last year for which you have data.

### Checking if Hurricane makes Landfall

To do this the readings/path of the storms is compared to the shapefile of florida, with its internal boundaries dissolved for simplification, using the dissolve function, from the shapely library.

To identify hurricanes that have made landfall in Florida, two methods can be used: the point method and the line method. 

**Point Method**

In the point method, the hurricane's path is represented as a series of discrete points, each corresponding to a specific location and time in the hurricane's trajectory. To determine if the hurricane has made landfall, each point is checked to see if it falls within the boundaries of the target region. If any point is found to be inside the region, the hurricane is considered to have made landfall.

This method is straightforward and easy to implement, but it has a limitation: if the distance between consecutive points is large, it's possible that the hurricane's path might cross into the region between two points without any individual point actually being inside the region. This could lead to false negatives, where a hurricane that should be considered as having made landfall is not detected. For example, consider Hurricane Eloise, which hit the coast of Florida in 1985. The readings taken are both outside Florida, and hence the point method fails to identify the landfall location.

**Line Method**

To address the limitation of the point method, the line method represents the hurricane's path as a series of connected line segments rather than discrete points. Each line segment connects two consecutive points in the hurricane's trajectory. To determine if the hurricane has made landfall, each line segment is checked to see if it intersects with the boundaries of the target region. If any line segment intersects with the region, the hurricane is considered to have made landfall.

The line method provides greater accuracy than the point method for detecting hurricanes that make landfall, especially when the data points are spaced far apart. For example, let's consider Hurricane Eloise. The readings taken are both outside Florida, and hence the point method fails to identify the landfall location. But since the line method plots the path and checks if this path intersects the landmass of Florida, it is able to identify the landfall correctly.
In total, since 1900, the line method is able to identify 109 storms compared to 100 storms by the point method.

However, it is also more complex to implement, as it requires checking for intersections between line segments and the region, which can be computationally more intensive.

In the provided code, the time of intersection (landfall) is calculated using interpolation when the intersecting location (point of landfall) is found between two consecutive readings of a hurricane's path. This is done in the interpolate_time_line_intersection method of the Storm class.

Here's how the interpolation works:

**Calculate Distances:** The method calculates the distances between the intersection point and the two consecutive readings (points) of the hurricane's path. This is done using the Euclidean distance formula.

**Calculate Ratio:** The ratio of the distance from the first point to the intersection point to the total distance between the two points is calculated. This ratio represents how far along the line segment between the two points the intersection occurs.

**Interpolate Time:** The time difference between the two readings is multiplied by the ratio to determine how much time has passed from the first point to the intersection point. This value is then added to the time of the first point to get the interpolated time of intersection.

**Spline Interpolation Method (Experimental, not implemented)**

Another method that was experimented with was the spline interpolation method. Cubic spline interpolation  was used to create smooth curves for longitude and latitude as functions of time. This allows for a continuous estimate of the hurricane's path, even between discrete data points. More information about this method can be found in Appendix I.
 

### Calculating Max Wind Speed

The maximum wind speed for each hurricane is calculated using the calculate_max_wind_speed method in the Storm class. This method iterates through all the readings (data points) of the hurricane and finds the highest wind speed recorded. Here's how the method is implemented:

### Output Generation
After processing all hurricanes, the code generates a report listing the name, date of landfall, and maximum wind speed for each hurricane that made landfall in Florida. This report can be formatted as a table and output to a file or printed to the console.

### GUI Design

The Graphical User Interface (GUI) for the hurricane analysis application is built using the Tkinter library in Python. It provides a user-friendly interface for interacting with the program, allowing users to input parameters, run the analysis, and view the results. Here are some key features of the GUI:

**Input Fields:** The GUI includes input fields for the dataset file path, shapefile path, minimum year, maximum year, and the method (point or line) for determining landfall. These fields allow users to specify the parameters for the analysis. The 

**Browse Buttons:** Next to the dataset and shapefile path input fields, there are "Browse" buttons that open a file dialog, allowing users to easily navigate and select the appropriate files from their file system. This allows users to run the code on not only this dataset but also experiment with other datasets if they wish to.

**Run Analysis Button:** There is a "Run Analysis" button that, when clicked, triggers the execution of the analysis based on the input parameters. The program then processes the data and generates a report of hurricanes that made landfall in Florida within the specified year range.

**Results Table:** Below the input fields and buttons, there is a canvas area that displays the results of the analysis in a table format. The table lists the name, maximum wind speed, and landfall date for each hurricane that meets the criteria.

**Grapher Button:** In the results table, each hurricane entry has a "Click to Graph" button. Clicking this button opens a popup window that displays a graphical representation of the hurricane's path, along with the Florida boundary. This visualization helps users to see the trajectory of the hurricane and its intersection with Florida.

### Appendix I: Spline Interpolation Method

Cubic spline interpolation is employed to construct a smooth and continuous representation of a hurricane's trajectory over time. This technique involves the creation of parametric splines for both longitude and latitude as functions of temporal progression. The CubicSpline function is utilized, with time measured in seconds as the independent variable and the combined longitude and latitude coordinates as the dependent variables. Subsequently, interpolated points are generated at 100 uniformly spaced intervals between the initial and final timestamps of the original dataset, delineating the estimated path of the hurricane during these intervals.

A LineString object, derived from the interpolated points, is used to depict the hurricane's path. The intersection of this interpolated curve with the Florida boundary is examined to ascertain whether the hurricane has made landfall.

An alternative interpolation method, the RBFInterpolator, is subsequently employed to estimate the time of landfall. This interpolator is formulated with the original longitude and latitude points as the independent variables and time, measured in hours, as the dependent variable. The estimated landfall time is then computed and transformed back into a datetime format, providing an interpolated estimation of the landfall time.

Although this method is potent, particularly for crafting smooth representations of curves and computing precise landfall locations, it was discovered that the second interpolation — calculating time as a function of latitude and longitude to ascertain the landfall time — lacked stability. As a result, this approach was not incorporated into the final solution.
