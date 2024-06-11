import React, { useState } from 'react';
import Button from '@mui/material/Button';
import { useMap } from 'react-leaflet';
import RotateRightIcon from '@mui/icons-material/RotateRight';
import { defaultLocation } from '../../Utils';

function CircleButton({ handleCircleRoute, userPosition }) {
  const [locating, setLocating] = useState(false);

  const buttonStyle = {
    position: 'absolute',
    bottom: '60px',
    right: '120px',
    zIndex: 1000,
    backgroundColor: 'white',
    padding: '5px',
    borderRadius: '5px',
  };

  const map = useMap();

  const buildPath = () => {
    let position = userPosition;
    if (userPosition === null) {
      position = [defaultLocation.lat, defaultLocation.lon];
    }
    map.flyTo([position[0], position[1]], map.getZoom());
    handleCircleRoute(position[0], position[1]);
    setLocating(false);
  };

  const handleClick = () => {
    if (!locating) {
      setLocating(true);
      buildPath();
    }
  };

  return (
    <div style={buttonStyle}>
      <Button variant="text" data-testid="locate-button" onClick={handleClick} disabled={locating}>
        <RotateRightIcon />
      </Button>
    </div>
  );
}

export default CircleButton;
