from enum import Enum

# File contains various constants and mappings related to medical conditions 
# and activities

ActivityAttributes = Enum(
    "ActivityAttributes",
    ["AEROBIC", "STRENGTH", "OUTDOOR", "WINTER", "SUMMER", "TRAUMATIC"],
)

medical_conditions = [
    "Mental stress",
    "Obesity",
    "Diabetes (Type I)",
    "Diabetes (Type II)",
    "Hypertension",
    "Coronary heart disease",
    "Bronchial asthma",
    "Osteoporosis",
    "Back pain",
    "Pregnancy",
    "None",
]
# fmt: off
# Activitiy types that are recommended for different medical conditions 
recommended_activities = {
    'Mental stress': [ActivityAttributes.AEROBIC, ActivityAttributes.STRENGTH],
    'Obesity': [ActivityAttributes.AEROBIC, ActivityAttributes.STRENGTH],
    'Diabetes (Type I)': [ActivityAttributes.AEROBIC, ActivityAttributes.STRENGTH], 
    'Diabetes (Type II)': [ActivityAttributes.AEROBIC, ActivityAttributes.STRENGTH],
    'Hypertension': [ActivityAttributes.AEROBIC, ActivityAttributes.STRENGTH], 
    'Coronary heart disease': [ActivityAttributes.AEROBIC], 
    'Bronchial asthma': [ActivityAttributes.AEROBIC],
    'Osteoporosis': [ActivityAttributes.AEROBIC, ActivityAttributes.STRENGTH],
    'Back pain': [ActivityAttributes.AEROBIC, ActivityAttributes.STRENGTH],
    'Pregnancy': [ActivityAttributes.AEROBIC],
    'None': list(ActivityAttributes),
    }

# The POIs are in a hierarchical structure and inherit all the attributes of their parents
# Example:
#   A POI (leaf) in jogging track class has the following route to the root:
#
#       root
#         |
#       Cross-country sports facilities         (OUTDOOR)
#          |
#        Sports and outdoor recreations routes' ()
#           |
#         Jogging track                         (AEROBIC)
#            |
#           POI
#
#   And thus will have the union (as in set theory) of all attributes of its parents:
#   {OUTDOOR, AEROBIC}
class_related_attributes = {
   #
   'Cross-country sports facilities': {ActivityAttributes.OUTDOOR},
   ## Sports and outdoor recreations routes
   'Climbing venues' : {ActivityAttributes.AEROBIC, ActivityAttributes.STRENGTH, ActivityAttributes.TRAUMATIC},
   'Ski slopes and downhill ski resorts': {ActivityAttributes.AEROBIC, ActivityAttributes.WINTER, ActivityAttributes.TRAUMATIC},
   'Sports and outdoor recreations routes': set(),
   ###
   'Jogging track' : {ActivityAttributes.AEROBIC},
   'Outdoor route': {ActivityAttributes.AEROBIC},
   'Ski track': {ActivityAttributes.AEROBIC, ActivityAttributes.WINTER, ActivityAttributes.TRAUMATIC},
   'Nature trail': {ActivityAttributes.AEROBIC},
   'Cross-country biking route': {ActivityAttributes.AEROBIC, ActivityAttributes.TRAUMATIC},
   'Canoe route': {ActivityAttributes.AEROBIC, ActivityAttributes.SUMMER},
   'Biking route': {ActivityAttributes.AEROBIC, ActivityAttributes.TRAUMATIC},
   'Hiking route': {ActivityAttributes.AEROBIC},
   'Water route': {ActivityAttributes.AEROBIC},
   ##
   'Cross-country ski resorts': {ActivityAttributes.AEROBIC, ActivityAttributes.WINTER},
   'Orienteering area': {ActivityAttributes.AEROBIC},
   ###
   'Ski orienteering area' : {ActivityAttributes.WINTER, ActivityAttributes.TRAUMATIC},
   'Mountain bike orienteering area': {ActivityAttributes.SUMMER, ActivityAttributes.TRAUMATIC},
   'Orienteering area': set(),
   #
   'Indoor sports facilites': set(),
   ##
   'Ice-skating arenas': {ActivityAttributes.AEROBIC, ActivityAttributes.TRAUMATIC},
   'Fitness centres and sports halls': set(),
   ###
   'Martial arts halls': {ActivityAttributes.AEROBIC, ActivityAttributes.TRAUMATIC},
   'Fitness centre': {ActivityAttributes.AEROBIC, ActivityAttributes.STRENGTH},
   'Gym': {ActivityAttributes.AEROBIC, ActivityAttributes.STRENGTH},
   'Gymnastics hall': {ActivityAttributes.AEROBIC, ActivityAttributes.STRENGTH},
   'Weight training hall': {ActivityAttributes.STRENGTH},
   ##
   'Sports halls': {ActivityAttributes.AEROBIC},
   ###
   'Floorball hall': {ActivityAttributes.TRAUMATIC},
   'Football hall': {ActivityAttributes.TRAUMATIC},
   'Skateboarding hall': {ActivityAttributes.TRAUMATIC},
   'Squash hall': {ActivityAttributes.TRAUMATIC},
   'Badminton hall': {ActivityAttributes.TRAUMATIC},
   'Tennis hall': {ActivityAttributes.TRAUMATIC},
   ##
   'Indoor venues of various sports' : set(),
   ###
   'Fencing venue': {ActivityAttributes.AEROBIC, ActivityAttributes.TRAUMATIC},
   'Parkour hall': {ActivityAttributes.AEROBIC, ActivityAttributes.TRAUMATIC},
   'Table tennis venue': {ActivityAttributes.AEROBIC},
   'Indoor shooting range': set(),
   'Indoor climbing wall': {ActivityAttributes.AEROBIC, ActivityAttributes.STRENGTH, ActivityAttributes.TRAUMATIC},
   'Dance studio': {ActivityAttributes.AEROBIC},
   'Artistic gymnastics facility': {ActivityAttributes.AEROBIC, ActivityAttributes.TRAUMATIC},
   'Stand-alone athletics venue': {ActivityAttributes.AEROBIC, ActivityAttributes.TRAUMATIC},
   #
   'Outdoor fields and sports parks' : {ActivityAttributes.OUTDOOR},
   ##
   'Golf courses': set(),
   'Ice sports areas and sites with natural ice': {ActivityAttributes.AEROBIC, ActivityAttributes.TRAUMATIC, ActivityAttributes.WINTER},
   'Neighbourhood sports facilities and parks': set(),
   ###
   'Disc golf course': {ActivityAttributes.AEROBIC, ActivityAttributes.STRENGTH},
   'Sports park': {ActivityAttributes.AEROBIC, ActivityAttributes.STRENGTH},
   'Neighbourhood sports area': {ActivityAttributes.AEROBIC, ActivityAttributes.STRENGTH},
   'Parkour area': {ActivityAttributes.AEROBIC, ActivityAttributes.STRENGTH, ActivityAttributes.TRAUMATIC},
   'Cycling area': {ActivityAttributes.AEROBIC, ActivityAttributes.TRAUMATIC},
   'Velodrome': {ActivityAttributes.AEROBIC, ActivityAttributes.TRAUMATIC},
   'Skateboarding/roller-blading rink': {ActivityAttributes.AEROBIC, ActivityAttributes.TRAUMATIC},
   'Fitness training park': {ActivityAttributes.AEROBIC, ActivityAttributes.STRENGTH},
   ##
   'Ball games courts': {ActivityAttributes.AEROBIC, ActivityAttributes.TRAUMATIC},
   'Athletics fields and venues': {ActivityAttributes.AEROBIC},
   #
   'Water sports facilities': {ActivityAttributes.AEROBIC},
   ##
   'Open air pools and beaches': {ActivityAttributes.OUTDOOR},
   ###
   'Winter swimming area': {ActivityAttributes.WINTER},
   ##
   'Indoor swimming pools, halls and spas': set()
}
# fmt: on
