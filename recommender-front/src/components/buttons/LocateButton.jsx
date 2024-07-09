import React, { useEffect, useState } from 'react';
import Button from '@mui/material/Button';
import MyLocationIcon from '@mui/icons-material/MyLocation';
import { useMap } from 'react-leaflet';
import { defaultLocation } from '../../Utils';

function LocateButton({ handleSetOrigin, positionToFlyTo, zoom }) {
  const [locating, setLocating] = useState(false);
  // let userPosition = null;

  const buttonStyle = {
    position: 'absolute',
    bottom: '60px',
    right: '40px',
    zIndex: 1000,
    backgroundColor: 'white',
    padding: '5px',
    borderRadius: '5px',
  };

  const map = useMap();

  const success = (position) => {
    map.flyTo([position.coords.latitude, position.coords.longitude], zoom);
    handleSetOrigin(position.coords.latitude, position.coords.longitude);
    // userPosition = [position.coords.latitude, position.coords.longitude];
    setLocating(false);
  };

  // I had to pass this property here to call flyTo
  useEffect(() => {
    if (positionToFlyTo && zoom) {
      map.flyTo([positionToFlyTo[0], positionToFlyTo[1]], zoom);
    }
  }, [positionToFlyTo, zoom]);

  const error = () => {
    console.log('Unable to retrieve your location');
    map.flyTo([defaultLocation.lat, defaultLocation.lon], zoom);
    handleSetOrigin(defaultLocation.lat, defaultLocation.lon);
    setLocating(false);
  };

  const handleClick = () => {
    if (!locating) {
      setLocating(true);

      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(success, error);
      } else {
        console.log('Geolocation not supported');
      }
    }
  };

  return (
    <div style={buttonStyle}>
      <Button variant="text" data-testid="locate-button" onClick={handleClick} disabled={locating}>
        <MyLocationIcon />
      </Button>
    </div>
  );
}

export default LocateButton;
