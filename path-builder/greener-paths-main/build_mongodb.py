import requests
from pymongo import MongoClient

from activity_definitions import class_related_attributes

# Classes to ignore (in current view useless sports)
ignored = {
    "Animal sports areas",
    "Electronic services and forms related to sports",
    "Physical education guidance",
    "Boating, aviation and motor sports",
    "Recreational destinations and services",
    "Senior sports",
    "Shooting sports facilities",
    "Bowling alleys",
    "Ski jumping hills",
    "Curling sheet",
}

# Functions for traversing the hierarchy


def get_node(url):
    resp = requests.get(url)
    resp.raise_for_status()
    resp = resp.json()
    return resp["results"][0]


def traverse_children(node, attributes, path):
    node_name = node["name"]["en"]
    if node_name in ignored:
        return []

    if node_name in class_related_attributes.keys():
        new_attributes = attributes.union(class_related_attributes[node["name"]["en"]])
    else:
        new_attributes = attributes
    new_path = path + [node_name]

    if node["children"]:
        units = []
        for child_id in node["children"]:
            url = f"https://api.hel.fi/servicemap/v2/service_node/?id={child_id}"
            temp_units = traverse_children(get_node(url), new_attributes, new_path)
            units.extend(temp_units)
        return units
    else:
        # Leafs have related services
        temp_units = []
        for service in node["related_services"]:
            url = f"https://api.hel.fi/servicemap/v2/unit/?service={service}&only=id,name,location"
            resp = requests.get(url)
            resp.raise_for_status()
            resp = resp.json()
            resp = resp["results"]

            for unit in resp:
                unit["attributes"] = [att.name for att in new_attributes]
                unit["path"] = new_path
                unit["unit_class"] = new_path[-1]
                temp_units.append(unit)
        return temp_units


if __name__ == "__main__":
    # Build the database of servicemap units by traversing the servicemap hierarchy

    # Connect to mongodb
    url = "mongodb://mongodb:27017"
    client = MongoClient(url)

    dbnames = client.list_database_names()
    if "activities" in dbnames:
        print("There already is a database called activities.")
        print("Dropping old database...")
        client.drop_database("activities")
        print("Rebuilding database...")
    # Create new databse
    db = client["activities"]
    # Create new collection
    coll = db["units"]

    root_id = 551  # Sports class id
    url = f"https://api.hel.fi/servicemap/v2/service_node/?id={root_id}"
    root_node = get_node(url)

    print("Traversing the hierarchy...")
    units = traverse_children(root_node, set(), [])
    print("Done traversing!")

    # Add the units to the collection
    coll.insert_many(units)

    # Create an index for geospatiol queries
    coll.create_index([("location", "2dsphere")])

    # Close the MongoDB connection
    client.close()
