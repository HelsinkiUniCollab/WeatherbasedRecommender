import React from 'react';
import MapComponent from './components/MapComponent';
import 'leaflet/dist/leaflet.css';
import WeatherComponent from './components/WeatherComponent';

function App() {
  return (
    <center>
      <h1>
        Weather-Based Recommender
      </h1>
      <div>
        <WeatherComponent />
      </div>
      <div>
        <MapComponent />
      </div>
    </center>
  );
}

export default App;
