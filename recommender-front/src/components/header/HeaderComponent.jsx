import React from 'react';
import Slider from '@mui/material/Slider';
import Typography from '@mui/material/Typography';
import Grid from '@mui/material/Grid';
import LoadingIndicatorComponent from './LoadingIndicatorComponent';
import InfoComponent from './InfoComponent';
import parseSliderLabels from '../../utils/HeaderUtils';
import PreferenceSelector from '../selector/PreferenceSelector';
import logo from '../../assets/WeatherBasedRecommender.svg';
import '../../assets/style.css';
import MedicalSelector from '../selector/MedicalSelector';
import AccessibilitySelector from '../selector/AccessibilitySelector';
import SettingsSelector from '../selector/SettingsSelector';

function HeaderComponent({
  handleChange, times, sliderValue, onChange, isMobile, open, handleOpen,
  handleClose, poiData, availableCategories,
  selectedCategories, setSelectedCategories,
  medicalCategories, setMedicalCategories, handleProfileChange,
}) {
  const hours = parseSliderLabels(times);
  return (
    <Grid
      container
      spacing={1}
      my={1}
      key="main"
      className="header-container"
    >
      <Grid
        item
        xs={6}
        sm={6}
        md={3}
        lg={3}
        order={{ lg: 1, md: 1, sm: 1, xs: 1 }}
        key="title"
        display="flex"
        justifyContent="center"
      >
        <img src={logo} alt="Weather-Based Recommender" className="logo" />
        <SettingsSelector
          onProfileChange={handleProfileChange}
        />
      </Grid>
      <Grid
        item
        xs={5}
        sm={5}
        md={3}
        lg={3}
        order={{ lg: 2, md: 2, sm: 4, xs: 4 }}
        display="flex"
        justifyContent="center"
      >
        <MedicalSelector
          selectedCategories={medicalCategories}
          onCategoryChange={setMedicalCategories}
        />
        <PreferenceSelector
          availableCategories={availableCategories}
          selectedCategories={selectedCategories}
          onCategoryChange={setSelectedCategories}
        />
        <AccessibilitySelector
          onCategoryChange={handleChange}
        />
      </Grid>
      <Grid
        item
        xs={3}
        sm={3}
        md={3}
        lg={3}
        order={{ lg: 4, md: 4, sm: 2, xs: 2 }}
        display="flex"
        justifyContent="center"
      >
        <InfoComponent open={open} handleOpen={handleOpen} handleClose={handleClose} />
      </Grid>
      <Grid item xs={11} sm={11} md={11} lg={11} className="slider-item" key="slider" order={{ lg: 5, md: 5, sm: 3, xs: 3 }}>
        <Typography variant="h2">Time</Typography>
        {poiData.length === 0 ? <LoadingIndicatorComponent />
          : (
            <Slider
              value={sliderValue}
              onChange={onChange}
              min={0}
              max={isMobile ? 10 : 24}
              marks={hours}
            />
          )}
      </Grid>
    </Grid>
  );
}

export default HeaderComponent;
