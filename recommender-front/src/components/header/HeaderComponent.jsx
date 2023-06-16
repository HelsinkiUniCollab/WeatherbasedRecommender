import React from 'react';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select from '@mui/material/Select';
import Slider from '@mui/material/Slider';
import Typography from '@mui/material/Typography';
import Grid from '@mui/material/Grid';
import useMediaQuery from '@mui/material/useMediaQuery';
// eslint-disable-next-line import/no-extraneous-dependencies
import { useTheme } from '@mui/system';

function HeaderComponent({
  accessibility, handleChange, times, sliderValue, onChange,
}) {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const hours = [];
  if (times) {
    for (let i = 0; i <= times.length; i += 1) {
      const value = i;
      const label = times[i];
      hours.push({ value, label });
    }
  }
  return (
    <Grid
      container
      spacing={1}
      justifyContent="center"
      alignItems="center"
      my={1}
      key="main"
    >
      <Grid item xs={5} sm={5} md={3} lg={3} key="title">
        <Typography variant="h1">Weather-Based Recommender</Typography>
      </Grid>
      <Grid item xs={7} sm={7} md={3} lg={3} className="dropdown-item" key="dropdown">
        <FormControl>
          <Select displayEmpty value={accessibility} onChange={handleChange}>
            <MenuItem value="">
              <Typography variant="h2">All attractions</Typography>
            </MenuItem>
            <MenuItem value="rollator">
              <Typography variant="h2">Rollator accessible</Typography>
            </MenuItem>
            <MenuItem value="stroller">
              <Typography variant="h2">Stroller accessible</Typography>
            </MenuItem>
            <MenuItem value="wheelchair">
              <Typography variant="h2">Wheelchair accessible</Typography>
            </MenuItem>
            <MenuItem value="reduced_mobility">
              <Typography variant="h2">Reduced mobility supported</Typography>
            </MenuItem>
            <MenuItem value="visually_impaired">
              <Typography variant="h2">Visually impaired supported</Typography>
            </MenuItem>
          </Select>
        </FormControl>
      </Grid>
      {isMobile ? (
        <Grid item xs={11} sm={11} className="slider-item" key="slider-mobile">
          <Typography variant="h2">Time</Typography>
          <Slider
            value={sliderValue}
            onChange={onChange}
            min={0}
            max={8}
            marks={hours}
          />
        </Grid>
      ) : (
        <Grid item xs={11} sm={11} md={10} lg={10} className="slider-item" key="slider">
          <Typography variant="h2">Time</Typography>
          <Slider
            value={sliderValue}
            onChange={onChange}
            min={0}
            max={24}
            marks={hours}
          />
        </Grid>
      )}
    </Grid>
  );
}
export default HeaderComponent;
