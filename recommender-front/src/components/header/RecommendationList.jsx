import React, { useEffect } from 'react';
import '../../assets/style.css';
import Typography from '@mui/material/Typography';
import ReviewsIcon from '@mui/icons-material/Reviews';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import { defaultLocation, AREA_RADIUS, REC_NUM, getAllowedActivities } from '../../Utils';

const activities = new Set([
  'Climbing',
  'Football',
  'Jogging',
  'Weightlifting',
  'Cycling',
  'Swimming',
  'Skateboarding',
]);

function getDistance(poi, userLocation) {
  // based on https://www.movable-type.co.uk/scripts/latlong.html
  // Latitude/longitude spherical geodesy tools
  // (c) Chris Veness 2002-2021, MIT Licence
  const lat1 = poi.latitude;
  const lon1 = poi.longitude;
  const lat2 = userLocation[0];
  const lon2 = userLocation[1];
  const R = 6371e3; // metres
  const φ1 = lat1 * (Math.PI / 180); // φ, λ in radians
  const φ2 = lat2 * (Math.PI / 180);
  const Δφ = (lat2 - lat1) * (Math.PI / 180);
  const Δλ = (lon2 - lon1) * (Math.PI / 180);
  const a = Math.sin(Δφ / 2) * Math.sin(Δφ / 2)
      + Math.cos(φ1) * Math.cos(φ2)
      * Math.sin(Δλ / 2) * Math.sin(Δλ / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  const d = R * c; // in metres
  return d;
  // return ((poi.latitude - userLocation[0]) ** 2 + (poi.longitude - userLocation[1]) ** 2) ** 0.5;
}

function getOutdoorScore(poiData, timeValue) {
  let score = 0.0;
  let i = 0;
  while (i < poiData.length) {
    if (poiData[i].all_categories[poiData[i].all_categories.length - 1] === 'Neighbourhood sports areas') {
      score = poiData[i].weather[timeValue].Score;
      break;
    }
    i += 1;
  }
  return score;
}

function getWalking(poiData, timeValue) {
  const walking = {};
  walking.name = 'Walking';
  walking.latitude = defaultLocation.lat;
  walking.longitude = defaultLocation.lon;
  walking.catetype = 'Outdoor';
  walking.all_categories = ['All', 'Culture, sport and leisure', 'Culture and leisure',
    'Sports and physical exercise', 'Outdoor fields and sports parks',
    'Neighbourhood sports facilities and parks', 'Neighbourhood sports areas'];
  walking.score = getOutdoorScore(poiData, timeValue);
  walking.distance = 0.0;
  walking.activities = ['Walking'];
  walking.activity = 'Walking';
  return walking;
}

function makeNewPOIs(pois, timeValue, userPosition, allowedActivities) {
  let userPos = userPosition;
  if (userPosition == null) {
    userPos = [defaultLocation.lat, defaultLocation.lon];
  }
  const newPOIs = [];
  pois.forEach((element) => {
    const newObj = {};
    newObj.name = element.name;
    newObj.latitude = element.latitude;
    newObj.longitude = element.longitude;
    newObj.catetype = element.catetype;
    newObj.all_categories = element.all_categories;
    newObj.score = element.weather[timeValue].Score;
    newObj.distance = getDistance(element, userPos);
    newObj.activities = element.activities.filter((activity) => allowedActivities
      .includes(activity));
    newPOIs.push(newObj);
  });
  return newPOIs;
}

function getNecessaryPOIs(filteredPOIs, pois) {
  const selectedPOIs = [];
  activities.forEach((activity) => {
    let item = filteredPOIs.filter((poi) => poi.activities.includes(activity)
        && !selectedPOIs.includes(poi))[0];
    if (typeof item === 'undefined') {
      [item] = pois.filter((poi) => poi.activities.includes(activity)
        && !selectedPOIs.includes(poi));
    }
    if (typeof item !== 'undefined') {
      item.activity = activity;
      selectedPOIs.push(item);
    }
  });
  return selectedPOIs;
}

function addMissingPOIs(selectedPOIs, filteredPOIs) {
  if (selectedPOIs.length >= REC_NUM) {
    return;
  }
  let i = 0;
  while (i < filteredPOIs.length && selectedPOIs.length < REC_NUM) {
    const poi = filteredPOIs[i];
    if (!selectedPOIs.includes(poi)) {
      [poi.activity] = poi.activities;
      selectedPOIs.push(poi);
    }
    i += 1;
  }
}

function getRecs(poiData, timeValue, userPosition, allowedActivities) {
  const pois = makeNewPOIs(poiData, timeValue, userPosition, allowedActivities);
  pois.sort((a, b) => (a.score < b.score ? 1 : -1));
  const filteredPOIs = pois.filter((poi) => poi.distance < AREA_RADIUS);
  const selectedPOIs = getNecessaryPOIs(filteredPOIs, pois);
  selectedPOIs.push(getWalking(poiData, timeValue));
  addMissingPOIs(selectedPOIs, filteredPOIs);
  selectedPOIs.sort((a, b) => (a.score < b.score ? 1 : -1));
  console.log(selectedPOIs);
  return selectedPOIs;
}

function itemClick(element, handleSetDestination) {
  handleSetDestination(element.latitude, element.longitude, element.activity);
}

function SettingsSelector({ poiData, userPosition, timeValue,
  availableActivities, selectedActivities, handleSetDestination }) {
  const [dataToShow, setDataToShow] = React.useState([]);
  useEffect(() => {
    if (typeof timeValue === 'undefined') {
      return;
    }
    console.log('SettingsSelector');
    const allowedActivities = getAllowedActivities(availableActivities, selectedActivities);
    const pois = getRecs(poiData, timeValue, userPosition, allowedActivities);
    setDataToShow(pois);
  }, [userPosition, poiData, timeValue]);

  return (
    <div className="preference-selector-container">
      <List>
        {dataToShow.map((element) => (
          <ListItem key={element.name}>
            <ListItemButton onClick={() => {
              itemClick(element, handleSetDestination);
            }}
            >
              <ListItemIcon>
                <ReviewsIcon />
              </ListItemIcon>
              <div>
                <Typography variant="h7">{element.activity}</Typography>
                <br />
                <ListItemText primary={element.name} />
              </div>
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </div>
  );
}

export default SettingsSelector;
