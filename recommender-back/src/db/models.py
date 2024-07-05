from .db import get_db

db = get_db()
pois_collection = "db['pois']"

class Poi:
    """
    Represents a Point of Interest (POI) with attributes like name, location, accessibility, and categories.
    Provides methods for saving a POI to the database and retrieving all POIs.

    Attributes:
        name (str): The name of the POI.
        latitude (float): The latitude of the POI's location.
        longitude (float): The longitude of the POI's location.
        accessibility (list): List of strings indicating who the POI is not accessible for.
        categories (list): List of strings indicating the categories the POI belongs to.
    """

    def __init__(self, name, latitude, longitude, accessibility, categories):
        """
        Initializes a new POI instance.

        Args:
            name (str): The name of the POI.
            latitude (float): The latitude of the POI's location.
            longitude (float): The longitude of the POI's location.
            accessibility (list): List of strings indicating who the POI is not accessible for.
            categories (list): List of strings indicating the categories the POI belongs to.
        """
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.accessibility = accessibility
        self.categories = categories

    def save(self):
        """
        Saves the current POI instance to the database.

        Returns:
            pymongo.results.InsertOneResult: The result of the insertion operation.
        """
        return pois_collection.insert_one({
            'name': self.name,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'not_accessible_for': self.accessibility,
            'categories': self.categories
        })

    @staticmethod
    def get_all():
        """
        Retrieves all POIs from the database.

        Returns:
            list: A list of dictionaries representing all POIs.
        """
        all_documents = pois_collection.find()
        return list(all_documents)
