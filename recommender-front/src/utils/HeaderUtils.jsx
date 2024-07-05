// the rules are based on https://earthscience.stackexchange.com/questions/9435/is-there-a-standardized-way-to-define-weather-icons-based-on-quantifiable-data
// and https://en.wikipedia.org/wiki/Rain
const getPrecipitation = (weather) => Number(weather.Precipitation.replace(' mm', ''));
const getClouds = (weather) => Number(weather['Cloud amount'].replace(' %', ''));

const getWeatherLabel = (temperature, clouds, precipitation) => {
  if (precipitation >= 2.5) {
    if (temperature < 0) {
      return 'snow';
    }
    return 'rain';
  }
  if (clouds > 87.5) {
    return 'clou';
  }
  if (clouds > 37.5) {
    return 'psun';
  }
  return 'sunn';
};

const parseSliderLabels = (weather) => {
  const hours = [];
  if (!weather) {
    return hours;
  }
  const keys = Object.keys(weather);
  for (let i = 0; i <= keys.length; i += 1) {
    const currentWeather = weather[keys[i]];
    if (currentWeather) {
      const value = i;
      let label = keys[i] ? keys[i].split(':')[0] : '';
      if (label === 'Current') {
        label = 'Now';
      }
      const temperatureStr = currentWeather['Air temperature'].replace(' °C', '');
      const temperature = Math.round(Number(temperatureStr));
      const weatherLabel = getWeatherLabel(
        temperature,
        getClouds(currentWeather),
        getPrecipitation(currentWeather),
      );
      label = label.concat(';');
      label = label.concat(weatherLabel);
      label = label.concat(';');
      label = label.concat(temperature.toString().concat('°'));
      hours.push({ value, label });
    }
  }
  return hours;
};

export default parseSliderLabels;
