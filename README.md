# FloridaHurricaneTracker

## KCC – Software Development Technical Assignment

**Task:** The NOAA Best Track Data (HURDAT2) contains historical data on storms, including their paths and intensities. The objective of this analysis is to identify all hurricanes that have made landfall in Florida since 1900 and to generate a report listing their names, dates of landfall, and maximum wind speeds.

https://github.com/nihaal7/FloridaHurricaneTracker/assets/40913961/b0f82b87-4312-4ecb-942e-e22e407226b6

**Submitted by:** Nihaal Subhash
nihaal.subhash@gmail.com

## Installation

To set up the project, follow these steps:

1. Clone the repository:
```
git clone https://github.com/nihaal7/FloridaHurricaneTracker
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

## Features

**Data Parsing:** Efficiently parses HURDAT2 dataset to extract relevant information about each storm.

**Filtering:** Identifies storms classified as hurricanes and filters them based on the year of occurrence.

**Landfall Detection:** Employs both point and line methods to accurately determine if a hurricane has made landfall in Florida.

**Max Wind Speed Calculation:** Determines the maximum wind speed for each hurricane to assess its intensity.

**Output Generation:** Generates a comprehensive report listing the name, date of landfall, and maximum wind speed for each identified hurricane.

**Storm Path Visualization:** Provides graphical representation of each hurricane's path, allowing for easy visualization of its trajectory and landfall.

**GUI:** Features a user-friendly graphical interface for easy interaction and visualization of results.

![image](https://github.com/nihaal7/FloridaHurricaneTracker/assets/40913961/6bf35456-4c5b-4f18-80bd-58dd7385e4b0)

## Usage

The project is designed to be accessible and easy to use. Users can input parameters, run the analysis, and view the results through the GUI. The interface allows for the selection of datasets, specification of year range, and choice of landfall detection method.

## Contact
For any questions or suggestions, please contact Nihaal Subhash at nihaal.subhash@gmail.com.
