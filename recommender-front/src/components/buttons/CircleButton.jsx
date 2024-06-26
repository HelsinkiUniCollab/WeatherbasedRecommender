import React, { useState } from 'react';
import Grid from '@mui/material/Grid';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import { useMap } from 'react-leaflet';
import DirectionsWalkIcon from '@mui/icons-material/DirectionsWalk';
import IconButton from '@mui/material/IconButton';
import CloseIcon from '@mui/icons-material/Close';
import Typography from '@mui/material/Typography';
import Slider from '@mui/material/Slider';
import { Radio, RadioGroup } from '@mui/material';
import MenuItem from '@mui/material/MenuItem';
import FormControlLabel from '@mui/material/FormControlLabel';
import Menu from '@mui/material/Menu';
import { defaultLocation } from '../../Utils';

function CircleButton({ handleCircleRoute, userPosition }) {
  const mobilityTypes = [{ name: 'Foot', val: 'foot' }, { name: 'Wheelchair', val: 'wheelchair' }];
  const [locating, setLocating] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);
  const defaultRouteLen = 1000;
  const [routeLen, setRouteLen] = React.useState(defaultRouteLen);
  const defaultRouteType = 'fast';
  const defaultMobilityType = 'foot';
  let mobilityType = defaultMobilityType;

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
    map.flyTo([position[0], position[1]], 15);
    handleCircleRoute(
      position[0],
      position[1],
      { route_len: routeLen, route_type: defaultRouteType, mobility_type: mobilityType },
    );
    setLocating(false);
  };

  const openMenu = (event) => {
    setAnchorEl(event.currentTarget);
  };
  const handleBuildPath = () => {
    if (!locating) {
      setLocating(true);
      buildPath();
    }
    setAnchorEl(null);
  };
  const menuClose = () => {
    setAnchorEl(null);
  };
  const routeLenChange = (event, newValue) => {
    setRouteLen(newValue);
  };

  const handleMobilityTypeChange = (type) => {
    mobilityType = type;
    console.log(mobilityType);
  };

  return (
    <div style={buttonStyle}>
      <Button variant="text" data-testid="locate-button" onClick={openMenu} disabled={locating}>
        <DirectionsWalkIcon />
      </Button>
      <Menu
        id="category-menu"
        anchorEl={anchorEl}
        keepMounted
        open={Boolean(anchorEl)}
        onClose={menuClose}
      >
        <IconButton
          aria-label="Close"
          aria-controls="category-menu"
          aria-haspopup="true"
          style={{ position: 'absolute', top: 0, right: 0, zIndex: 1 }}
          onClick={menuClose}
        >
          <CloseIcon />
        </IconButton>
        <Typography variant="h7" sx={{ ml: 2, mt: 2 }}>
          Roundtrip length (in meters):
          {routeLen}
        </Typography>
        <Slider
          min={50}
          max={5000}
          defaultValue={defaultRouteLen}
          value={routeLen}
          onChange={routeLenChange}
          aria-labelledby="continuous-slider"
        />
        <Typography variant="h7" sx={{ ml: 2, mt: 2 }}>Mobility</Typography>
        <RadioGroup defaultValue={defaultMobilityType}>
          <Box style={{ display: 'flex' }}>
            {mobilityTypes.map((category) => (
              <MenuItem key={category.val}>
                <FormControlLabel
                  control={<Radio />}
                  label={category.name}
                  value={category.val}
                  onChange={() => handleMobilityTypeChange(category.val)}
                />
              </MenuItem>
            ))}
          </Box>
        </RadioGroup>
        <Grid container justifyContent="flex-end" sx={{ padding: '5px' }}>
          <Button variant="contained" onClick={handleBuildPath}>Build path</Button>
        </Grid>
      </Menu>
    </div>
  );
}

export default CircleButton;
