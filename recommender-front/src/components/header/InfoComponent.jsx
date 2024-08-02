import React from 'react';
import { Button, Dialog, DialogContent, DialogTitle } from '@mui/material';
import IconButton from '@mui/material/IconButton';
import CloseIcon from '@mui/icons-material/Close';
import InfoIcon from '@mui/icons-material/Info';
import Typography from '@mui/material/Typography';

function InfoComponent({ open, handleOpen, handleClose }) {
  return (
    <div>
      <Button onClick={handleOpen} variant="contained" color="primary">
        <InfoIcon />
      </Button>
      <Dialog open={open} onClose={handleClose}>
        <DialogTitle>
          <Typography variant="infotitle">Info</Typography>
          <IconButton onClick={handleClose} style={{ position: 'absolute', top: '0', right: '0' }}>
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        <DialogContent>
          <Typography variant="infotext">The website uses data from the following services & APIs:</Typography>
          <ul>
            <li>
              <Typography variant="infotext"><a href="https://palvelukartta.hel.fi/en">Servicemap</a></Typography>
            </li>
            <li>
              <Typography variant="infotext"><a href="https://www.openstreetmap.org/#map=14/60.2046/24.9633">OpenStreetMap</a></Typography>
            </li>
            <li>
              <Typography variant="infotext"><a href="https://en.ilmatieteenlaitos.fi/">Finnish meteorological institute</a></Typography>
            </li>
            <li>
              <Typography variant="infotext"><a href="https://www.graphhopper.com/">GraphHopper</a></Typography>
            </li>
            <li>
              <Typography variant="infotext"><a href="https://ionic.io/ionicons">Ionicons</a></Typography>
            </li>
          </ul>
        </DialogContent>
      </Dialog>
    </div>
  );
}

export default InfoComponent;
