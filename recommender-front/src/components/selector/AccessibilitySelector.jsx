import React, { useState } from 'react';
import FormControlLabel from '@mui/material/FormControlLabel';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import IconButton from '@mui/material/IconButton';
import CloseIcon from '@mui/icons-material/Close';
import '../../assets/style.css';
import Typography from '@mui/material/Typography';
import MenuIcon from '@mui/icons-material/Menu';
import { Radio, RadioGroup } from '@mui/material';

function AccessibilitySelector({ onCategoryChange }) {
  const allCategories = [{ name: 'No restrictions', val: '' }, { name: 'Rollator accessible', val: 'rollator' },
    { name: 'Stroller accessible', val: 'stroller' }, { name: 'Wheelchair accessible', val: 'wheelchair' }, { name: 'Reduced mobility', val: 'reduced_mobility' },
    { name: 'Visually impaired', val: 'visually_impaired' }];

  const handleCategoryRadioChange = (category) => {
    onCategoryChange(category);
  };

  const [anchorEl, setAnchorEl] = useState(null);

  const handleMenuClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  return (
    <div className="preference-selector-container">
      <IconButton
        data-testid="menu-button"
        aria-controls="category-menu"
        aria-haspopup="true"
        onClick={handleMenuClick}
        color="primary"
        size="small"
      >
        <MenuIcon />
      </IconButton>
      <Typography variant="h7" onClick={handleMenuClick}>Accessibility</Typography>
      <Menu
        id="category-menu"
        anchorEl={anchorEl}
        keepMounted
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <IconButton
          aria-label="Close"
          aria-controls="category-menu"
          aria-haspopup="true"
          style={{ position: 'absolute', top: 0, right: 0, zIndex: 1 }}
          onClick={handleMenuClose}
        >
          <CloseIcon />
        </IconButton>
        <RadioGroup defaultValue="">
          {allCategories.map((category) => (
            <MenuItem key={category.val}>
              <FormControlLabel
                control={<Radio />}
                label={category.name}
                value={category.val}
                onChange={() => handleCategoryRadioChange(category.val)}
              />
            </MenuItem>
          ))}
        </RadioGroup>
      </Menu>
    </div>
  );
}

export default AccessibilitySelector;
