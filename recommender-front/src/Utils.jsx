export const defaultLocation = { lat: 60.198805, lon: 24.935671 };
export const AREA_RADIUS = 1085 * 2; // 30 minutes by walk
export const REC_NUM = 10;

export const getAllowedActivities = function (availableActivities, selectedActivities) {
  if (selectedActivities.length === 0 || selectedActivities.includes('All')) {
    return availableActivities;
  }
  const allowedActivities = selectedActivities.filter((activity) => availableActivities
    .includes(activity));
  return allowedActivities;
};
