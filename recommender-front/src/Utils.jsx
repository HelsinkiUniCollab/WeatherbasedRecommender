export const defaultLocation = { lat: 60.198805, lon: 24.935671 };
export const AREA_RADIUS = 1085 * 2; // 30 minutes by walk
export const REC_NUM = 10;

const LEVELS = [{ level: 18, diffX: 0.003932, diffY: 0.001197 },
  { level: 17, diffX: 0.011838 / 2, diffY: 0.004397 / 2 },
  { level: 16, diffX: 0.011838, diffY: 0.004397 },
  { level: 15, diffX: 0.040779 / 2, diffY: 0.018259 / 2 },
  { level: 14, diffX: 0.040779, diffY: 0.018259 },
  { level: 13, diffX: 0.164346 / 2, diffY: 0.075009 / 2 },
  { level: 12, diffX: 0.164346, diffY: 0.075009 }];

const getMinMax = function (routeCoordinates) {
  let maxX = Number.MIN_VALUE;
  let maxY = Number.MIN_VALUE;
  let minX = Number.MAX_VALUE;
  let minY = Number.MAX_VALUE;
  routeCoordinates.forEach((point) => {
    const x = point[0];
    const y = point[1];
    if (maxX < x) {
      maxX = x;
    }
    if (maxY < y) {
      maxY = y;
    }
    if (minX > x) {
      minX = x;
    }
    if (minY > y) {
      minY = y;
    }
  });
  return [minX, maxX, minY, maxY];
};

export const getMapPosition = function (routeCoordinates, userPosition) {
  if (routeCoordinates.length === 0) {
    return userPosition;
  }
  const minMax = getMinMax(routeCoordinates);
  return [(minMax[0] + minMax[1]) / 2, (minMax[2] + minMax[3]) / 2];
};

export const getZoom = function (routeCoordinates, minZoom) {
  if (routeCoordinates.length === 0) {
    return 15;
  }
  const minMax = getMinMax(routeCoordinates);
  const diffX = Math.abs(minMax[0] - minMax[1]);
  const diffY = Math.abs(minMax[2] - minMax[3]);
  for (let i = 0; i < LEVELS.length; i += 1) {
    const current = LEVELS[i];
    if (diffX < current.diffX && diffY < current.diffY) {
      return current.level;
    }
  }
  return minZoom;
};

export const getAllowedActivities = function (availableActivities, selectedActivities) {
  if (selectedActivities.length === 0 || selectedActivities.includes('All')) {
    return availableActivities;
  }
  const allowedActivities = selectedActivities.filter((activity) => availableActivities
    .includes(activity));
  return allowedActivities;
};
