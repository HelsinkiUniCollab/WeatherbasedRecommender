import React, { useState, useEffect } from 'react';
import { Helmet, HelmetProvider } from 'react-helmet-async';
import { ThemeProvider } from '@mui/material/styles';
import useMediaQuery from '@mui/material/useMediaQuery';
import Grid from '@mui/material/Grid';
import Box from '@mui/material/Box';
import Tab from '@mui/material/Tab';
import TabContext from '@mui/lab/TabContext';
import TabList from '@mui/lab/TabList';
import TabPanel from '@mui/lab/TabPanel';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import WeatherAlert from './components/warning/WeatherAlert';
import MapComponent from './components/map/MapComponent';
import HeaderComponent from './components/header/HeaderComponent';
import PathUtil from './utils/PathComponent';
import SimulatorPage from './pages/SimulatorPage';
import 'leaflet/dist/leaflet.css';
import '@fontsource/roboto/300.css';
import theme from './assets/theme';
import './assets/style.css';
// eslint-disable-next-line import/no-extraneous-dependencies
import 'leaflet.markercluster/dist/MarkerCluster.css';
// eslint-disable-next-line import/no-extraneous-dependencies
import 'leaflet.markercluster/dist/MarkerCluster.Default.css';
import covertMedicalCategories from './MedicalFilter';
import { defaultLocation, getAllowedActivities } from './Utils';
import RecommendationList from './components/header/RecommendationList';

function App() {
  const DEFAULT_MED_CATEGORIES = ['Weightlifting', 'Jogging', 'Skateboarding', 'Cycling', 'Swimming', 'Climbing', 'Football'];
  const [accessibility, setAccessibility] = useState('');
  const [allPoiData, setAllPoiData] = useState([]);
  const [poiData, setPoiData] = useState([]);
  const [times, setTimes] = useState(0);
  const [selectedValue, setSelectedValue] = useState(0);
  const [open, setOpen] = useState(false);
  const [showAlert, setShowAlert] = useState(false);
  const [userPosition, setUserPosition] = useState(null);
  const [destination, setDestination] = useState(null);
  const [pathActivity, setPathActivity] = useState('none');
  const [routeCoordinates, setRouteCoordinates] = useState([]);
  const [warning, setWarning] = useState(false);
  const [headerHidden, setHeaderHidden] = useState(false);
  const [selectedCategories, setSelectedCategories] = useState(['All']);
  const [availableCategories, setAvailableCategories] = useState(DEFAULT_MED_CATEGORIES);
  const [medicalCategories, setMedicalCategories] = useState(['None']);
  const [profile, setProfile] = useState(['None']);
  const [rec, setRec] = useState(['None']);
  const [position, setPosition] = useState([60.2049, 24.9649]);
  let poisReceived = false;
  const toggleHeader = () => {
    setHeaderHidden(!headerHidden);
  };

  const handleOptionChange = (event) => {
    setAccessibility(event);
  };

  const handleSliderChange = (event) => {
    // remove
    console.log(rec);
    setSelectedValue(event.target.value);
  };

  const handleOpen = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  const handleSetOrigin = (latitude, longitude) => {
    setUserPosition([latitude, longitude]);
  };

  const handleCircleRoute = (latitude, longitude) => {
    setPathActivity('Walking');
    if (userPosition === null) {
      setUserPosition([latitude, longitude]);
      setDestination([latitude, longitude]);
    } else {
      setDestination([userPosition[0], userPosition[1]]);
    }
  };

  const handleSetDestination = (latitude, longitude, activity) => {
    if (activity === 'Walking') {
      let currentPosition = userPosition;
      if (currentPosition === null) {
        currentPosition = [defaultLocation.lat, defaultLocation.lon];
      }
      handleCircleRoute(currentPosition[0], currentPosition[1]);
      setPosition([currentPosition[0], currentPosition[1]]);
    } else {
      setPathActivity('Direct');
      setDestination([latitude, longitude]);
      setPosition([latitude, longitude]);
    }
  };

  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const filterPoiData = (
    data,
    access,
    selectedActivities,
    availableActivities,
    healthCategories,
  ) => {
    let filteredData = data;

    // Filter by accessibility
    if (access) {
      filteredData = filteredData.filter((poi) => !poi.not_accessible_for.includes(access));
    }

    // Get medical categories
    if (healthCategories.length > 0 && healthCategories[0] !== 'None') {
      // Narrow down categories based on medical conditions
      // console.log(filterCategories);
      const convertedCategories = covertMedicalCategories(healthCategories);
      // console.log(convertedCategories);
      filteredData = filteredData.filter((poi) => {
        const intersection = poi.activities.filter((element) => convertedCategories
          .includes(element));
        return intersection.length !== 0;
      });
    }
    const activities = getAllowedActivities(availableActivities, selectedActivities);
    // Filter by categories
    filteredData = filteredData.filter((p) => p.activities.some((r) => activities
      .includes(r)));

    setPoiData(filteredData);
  };

  async function fetchData() {
    try {
      if (poisReceived) {
        return;
      }
      poisReceived = true;
      const apiUrl = process.env.REACT_APP_BACKEND_URL;
      const warningResponse = await fetch(`${apiUrl}/api/warning`);
      const alert = await warningResponse.json();
      setWarning(alert);
      if (!alert) {
        const poiResponse = await fetch(`${apiUrl}/api/poi`);
        const poi = await poiResponse.json();
        setAllPoiData(poi);
        filterPoiData(
          poi,
          accessibility,
          selectedCategories,
          availableCategories,
          medicalCategories,
        );
      }
    } catch (error) {
      console.error('Error fetching the Point of Interests: ', error);
    }
  }

  useEffect(() => {
    if (pathActivity === 'Walking') {
      handleCircleRoute(userPosition[0], userPosition[1]);
    }
  }, [userPosition]);

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    filterPoiData(
      allPoiData,
      accessibility,
      selectedCategories,
      availableCategories,
      medicalCategories,
    );
  }, [accessibility, allPoiData, selectedCategories, availableCategories, medicalCategories]);

  useEffect(() => {
    if (medicalCategories.length > 0 && medicalCategories[0] !== 'None') {
      const convertedCategories = covertMedicalCategories(medicalCategories);
      setAvailableCategories(convertedCategories);
    } else {
      setAvailableCategories(DEFAULT_MED_CATEGORIES);
    }
  }, [medicalCategories]);

  useEffect(() => {
    if (poiData.length > 0) {
      setTimes(Object.keys(poiData[0].weather));
    }
  }, [poiData]);

  useEffect(() => {
    if (warning) {
      setShowAlert(true);
    }
  }, [warning]);
  const [value, setValue] = React.useState('1');
  const handleChange1 = (event, newValue) => {
    setValue(newValue);
  };

  return (
    <ThemeProvider theme={theme}>
      <HelmetProvider>
        <Helmet>
          <title>Weather-Based Recommender</title>
          <meta name="description" content="Weather-Based Recommender" />
          <meta
            name="viewport"
            content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no"
          />
        </Helmet>
        <PathUtil
          origin={userPosition}
          destination={destination}
          setRouteCoordinates={setRouteCoordinates}
          settings={profile}
        />
        <Router>
          <Routes>
            <Route
              path="/"
              element={(
                <Grid container overflow="scroll" className="app-container">
                  <Grid
                    item
                    xs={12}
                    className={`header-container${showAlert || headerHidden ? ' disabled' : ''}`}
                  >
                    <HeaderComponent
                      handleChange={handleOptionChange}
                      times={times}
                      sliderValue={selectedValue}
                      onChange={handleSliderChange}
                      open={open}
                      handleOpen={handleOpen}
                      handleClose={handleClose}
                      isMobile={isMobile}
                      poiData={poiData}
                      selectedCategories={selectedCategories}
                      setSelectedCategories={setSelectedCategories}
                      availableCategories={availableCategories}
                      medicalCategories={medicalCategories}
                      setMedicalCategories={setMedicalCategories}
                      handleProfileChange={setProfile}
                      userPosition={userPosition}
                      chooseRec={setRec}
                      handleSetDestination={handleSetDestination}
                    />
                  </Grid>
                  <Grid
                    item
                    xs={12}
                    className={`map-container${showAlert ? ' disabled' : ''}${headerHidden ? ' fullscreen' : ''}`}
                  >
                    <Box sx={{ width: '100%', typography: 'body1' }}>
                      <TabContext value={value}>
                        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                          <TabList onChange={handleChange1}>
                            <Tab label="Recommendations" value="1" />
                            <Tab label="Map" value="2" />
                          </TabList>
                        </Box>
                        <TabPanel value="1">
                          <RecommendationList
                            poiData={poiData}
                            userPosition={userPosition}
                            timeValue={times[selectedValue]}
                            availableActivities={availableCategories}
                            selectedActivities={selectedCategories}
                            handleSetDestination={handleSetDestination}
                          />
                        </TabPanel>
                        <TabPanel value="2">
                          <WeatherAlert showAlert={showAlert} />
                          <MapComponent
                            position={position}
                            accessibility={accessibility}
                            poiData={poiData}
                            time={times[selectedValue]}
                            isMobile={isMobile}
                            handleSetOrigin={handleSetOrigin}
                            userPosition={userPosition}
                            handleSetDestination={handleSetDestination}
                            handleCircleRoute={handleCircleRoute}
                            routeCoordinates={routeCoordinates}
                            toggleHeader={toggleHeader}
                          />
                        </TabPanel>
                      </TabContext>
                    </Box>
                  </Grid>
                </Grid>
                    )}
            />
            <Route path="/admin" element={<SimulatorPage />} />
          </Routes>
        </Router>
      </HelmetProvider>
    </ThemeProvider>
  );
}

export default App;
