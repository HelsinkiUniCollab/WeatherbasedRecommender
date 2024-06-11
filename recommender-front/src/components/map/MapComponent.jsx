import React from 'react';
import { MapContainer, TileLayer, Polyline } from 'react-leaflet';
import MarkersComponent from './MarkersComponent';
import UserLocationMarker from './UserLocationComponent';
import LocateButton from '../buttons/LocateButton';
import '../../assets/style.css';
import CircleButton from '../buttons/CircleButton';

function MapComponent({
  poiData, time, handleSetOrigin, userPosition, handleSetDestination, routeCoordinates,
  headerHidden, handleCircleRoute, position,
}) {
  const minZoom = 12;
  const maxZoom = 18;
  const bounds = [[60, 24.6], [60.35, 25.355]];
  const viscosity = 1;

  return (
    <div className={`map-container${headerHidden ? ' fullscreen' : ''}`}>
      <MapContainer
        id="map"
        center={position}
        scrollWheelZoom={false}
        zoom={minZoom}
        minZoom={minZoom}
        maxZoom={maxZoom}
        maxBounds={bounds}
        maxBoundsViscosity={viscosity}
        className="leaflet-map"
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution={
            '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          }
        />
        <LocateButton
          positionToFlyTo={position}
          handleSetOrigin={handleSetOrigin}
        />
        <CircleButton
          userPosition={userPosition}
          handleCircleRoute={handleCircleRoute}
        />
        {userPosition && (
          <UserLocationMarker
            userPosition={userPosition}
            handleSetOrigin={handleSetOrigin}
          />
        )}
        <MarkersComponent
          poiData={poiData}
          time={time}
          handleSetDestination={handleSetDestination}
        />
        {routeCoordinates && (
          <Polyline data-testid="map-polyline" positions={routeCoordinates} />
        )}
      </MapContainer>
    </div>
  );
}

export default MapComponent;
