// icons are taken from https://ionic.io/ionicons
import React from 'react';
import { SliderMarkLabel } from '@mui/material';
import Box from '@mui/material/Box';
import clouds from '../../assets/weatherIcons/clou.svg';
import partSunny from '../../assets/weatherIcons/psun.svg';
import sunny from '../../assets/weatherIcons/sunn.svg';
import rain from '../../assets/weatherIcons/rain.svg';
import snow from '../../assets/weatherIcons/snow.svg';

function WeatherMark(props) {
  const { style } = props;
  const { 'data-index': indexStr } = props;
  const index = Number(indexStr);
  const { ownerState: { marks } } = props;
  const mark = marks[index];
  const { label } = mark;
  const splitLabel = label.split(';');
  const hour = splitLabel[0];
  const weather = splitLabel[1];
  const temperature = splitLabel[2];
  const { ownerState: { value } } = props;
  return (
    <SliderMarkLabel
      style={style}
    >
      <Box sx={{ position: 'relative', left: '-7px', paddingTop: '13px' }}>
        <span className={value === index ? 'hour_active' : 'hour_inactive'}>{hour}</span>
        <br />
        {weather === 'clou' ? (
          <img src={clouds} alt="Clouds" className="weather_icon" />
        ) : null }
        {weather === 'psun' ? (
          <img src={partSunny} alt="Partly sunny" className="weather_icon" />
        ) : null }
        {weather === 'sunn' ? (
          <img src={sunny} alt="Sunny" className="weather_icon" />
        ) : null }
        {weather === 'rain' ? (
          <img src={rain} alt="Rain" className="weather_icon" />
        ) : null }
        {weather === 'snow' ? (
          <img src={snow} alt="Snow" className="weather_icon" />
        ) : null }
        <br />
        <span className={value === index ? 'temperature_active' : 'temperature_inactive'}>{temperature}</span>
      </Box>
    </SliderMarkLabel>
  );
}

export default WeatherMark;
