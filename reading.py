from datetime import datetime
from typing import Optional

class Reading:
    """
    A class for storing and processing readings from the HURDAT2 dataset.
    Each reading represents a single observation of a storm at a specific time.
    """
    def __init__(self) -> None:
        # Initialize instance variables
        self.datetime: Optional[datetime] = None   # Date and time of the reading
        self.msw_kts: Optional[float] = None       # Wind speed in knots
        self.lat: Optional[float] = None           # Latitude
        self.long: Optional[float] = None          # Longitude
        self.status: Optional[str] = None          # Status of the reading (e.g., 'HU', 'TD')
    
    def read_values(self, line: str):
        """
        Parse a line from the HURDAT2 dataset and populate the attributes of the Reading instance.

        Parameters:
        - line (str): A line from the HURDAT2 dataset.

        Returns:
        - None
        """        
        try:
            # Split the line into a list of values
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
        
    def convert_coordinates(self, latitude: str, longitude: str) -> tuple[float, float]:
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
    
    def parse_date_time(self, datestamp: str, timestamp: str) -> datetime: 
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
