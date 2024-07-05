import { useCallback, useEffect } from 'react';

function PathUtil({ origin, destination, setRouteCoordinates, settings, pathActivity }) {
  const handleSendCoords = useCallback(async () => {
    if (!settings || pathActivity === 'Location') {
      setRouteCoordinates([]);
      return;
    }
    let path = '/api/path?';
    if (origin[0] === destination[0] && origin[1] === destination[1]) {
      path = '/api/circle?';
    }
    try {
      const apiUrl = process.env.REACT_APP_BACKEND_URL;
      const queryParams = new URLSearchParams({
        start: origin.join(','),
        end: destination.join(','),
        route_len: settings.route_len,
        route_type: settings.route_type,
        mobility_type: settings.mobility_type,
      });

      const response = await fetch(`${apiUrl}${path}${queryParams}`);
      const routeCoordinates = await response.json();

      await setRouteCoordinates(routeCoordinates);
    } catch (error) {
      console.error('Error sending coordinates:', error);
    }
  }, [origin, destination, setRouteCoordinates]);

  useEffect(() => {
    if (origin && destination && origin.length === 2 && destination.length === 2) {
      handleSendCoords();
    }
  }, [origin, destination, handleSendCoords]);

  return null;
}

export default PathUtil;
