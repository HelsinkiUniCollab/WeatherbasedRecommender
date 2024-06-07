from activity_definitions import ActivityAttributes, recommended_activities
from .weather_utils import get_weather_data

FORCE_RAIN = False
FORCE_HEAT = False


def filter_POIs(
    db, med_cond, location, ignore_rain, ignore_heat, preferred_activities, n_results=10
):
    # Gather the recommendation criteria for explaining the recommendations
    rec_criteria = set()

    # For debugging
    if FORCE_RAIN:
        print("FORCE_RAIN")
    if FORCE_HEAT:
        print("FORCE HEAT")

    # Medical condition based recommedation
    activity_types = recommended_activities[med_cond]
    activity_types = [t.name for t in activity_types]
    in_array = []
    nin_array = []
    query = {}
    if med_cond != "None":
        in_array.extend(activity_types)
        rec_criteria.add("medical_condition")
    if med_cond == "Pregnancy":
        # Don't recommended traumatic sports to pregrant women
        nin_array.append(ActivityAttributes.TRAUMATIC.name)
        rec_criteria.add("pregnant")

    # Weather based recommedations
    temperature, precipitation, _ = get_weather_data()
    high_temp = False
    raining = False

    # FMI considers "heat (helle)" to be over 25C.
    if FORCE_HEAT or (not ignore_heat and temperature >= 25):
        print("It's hot outside!")
        rec_criteria.add("high_temperature")
        high_temp = True
    else:
        high_temp = False
    if FORCE_RAIN or (not ignore_rain and precipitation > 0):
        print("It's raining outside")
        rec_criteria.add("rain")
        raining = True
    else:
        raining = False

    # Don't recommend outdoor activities during that time.
    if high_temp or raining:
        print("It's bad weather outside!")
        nin_array.append(ActivityAttributes.OUTDOOR.name)

    if in_array or nin_array:
        query["attributes"] = {}
        if in_array:
            query["attributes"]["$in"] = in_array
        if nin_array:
            query["attributes"]["$nin"] = nin_array

    # Filter by preferred activities
    if preferred_activities:
        query["unit_class"] = {"$in": preferred_activities}

    # Filter by location
    query["location"] = {
        "$near": {
            "$geometry": {
                "type": "Point",
                "coordinates": [location[1], location[0]],
            }
        }
    }

    res = db.find(query, {"_id": 0}).limit(n_results)

    return res, rec_criteria
