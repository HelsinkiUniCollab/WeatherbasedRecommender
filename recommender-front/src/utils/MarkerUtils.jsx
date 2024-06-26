import L from 'leaflet';
import React from 'react';
import ReactDOM from 'react-dom/client';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import createMarkerIcon from './Icon';
import DestinationButton from '../components/buttons/DestinationButton';

const createMarkers = (poiData, time, handleSetDestination) => {
  if (!poiData || !time) {
    return [];
  }

  const handleSetDestinationButton = (event, marker, poi) => {
    marker.closePopup();
    handleSetDestination(poi.latitude, poi.longitude, false);
  };
  return poiData.map((poi) => {
    const tags = Object.entries(poi.weather[time]);
    const markerIcon = createMarkerIcon(poi.weather[time].Score);
    const marker = L.marker([poi.latitude, poi.longitude], {
      icon: markerIcon,
    });

    const container = (
      <center>
        <Typography variant="h6"><strong>{poi.name}</strong></Typography>
        <Typography variant="h8">
          <i>
            {poi.catetype}
            {' '}
            /
            {' '}
            {poi.category}
          </i>
        </Typography>
        <Grid
          container
          spacing={1}
          style={{ marginTop: 5 }}
          alignItems="center"
          justifyContent="center"
        >
          {tags.map(([key, value]) => (
            key !== 'Score' && (
            <Grid item xs={4} key={key}>
              <Typography variant="infotext" style={{ marginBottom: 1 }}>
                {key}
              </Typography>
              <h3>{value}</h3>
            </Grid>
            )
          ))}
        </Grid>
        <Grid
          container
          spacing={1}
          alignItems="center"
          justifyContent="center"
        >
          <Grid item xs={4} key="Score">
            <Typography variant="infotext" style={{ marginBottom: 1 }}>
              Score
              {' '}
              <i>(0-1)</i>
            </Typography>
            <h3>{tags[tags.length - 1][1]}</h3>
          </Grid>
          <Grid item>
            <DestinationButton
              onClick={(event) => handleSetDestinationButton(event, marker, poi)}
            />
          </Grid>
        </Grid>
      </center>
    );

    const scoreTag = tags.find(([key]) => key === 'Score');
    const scoreValue = scoreTag ? scoreTag[1] : null;
    const score = parseFloat(scoreValue);

    const divElement = document.createElement('div');
    const root = ReactDOM.createRoot(divElement);
    root.render(container);
    marker.bindPopup(divElement);

    return [marker, score];
  });
};

export default createMarkers;
