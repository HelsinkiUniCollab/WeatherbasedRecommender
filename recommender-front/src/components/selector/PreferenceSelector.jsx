import React, { useState } from 'react';
import Checkbox from '@mui/material/Checkbox';
import FormControlLabel from '@mui/material/FormControlLabel';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import IconButton from '@mui/material/IconButton';
import MenuIcon from '@mui/icons-material/Menu';
import CloseIcon from '@mui/icons-material/Close';
import '../../assets/style.css';
import Typography from '@mui/material/Typography';

function PreferenceSelector({ availableCategories, selectedCategories, onCategoryChange }) {
  const allCategories = ['Weightlifting', 'Jogging', 'Skateboarding', 'Cycling', 'Swimming', 'Climbing', 'Football', 'Walking'];

  const isAllChecked = selectedCategories.includes('All');

  const handleAllCheckboxChange = () => {
    onCategoryChange(isAllChecked ? [] : ['All']);
  };

  const handleCategoryCheckboxChange = (category) => {
    if (selectedCategories.includes(category)) {
      onCategoryChange(selectedCategories.filter((item) => item !== category));
    } else {
      onCategoryChange([...selectedCategories.filter((item) => item !== 'All'), category]);
    }
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
      <Typography variant="h7" onClick={handleMenuClick}>Activities</Typography>
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
        <MenuItem>
          <FormControlLabel
            control={(
              <Checkbox
                checked={isAllChecked}
                onChange={handleAllCheckboxChange}
                name="allCheckbox"
                className="icon-button-selector"
                color="primary"
              />
            )}
            label="All"
          />
        </MenuItem>
        {allCategories.map((category) => (
          <MenuItem key={category}>
            <FormControlLabel
              control={(
                <Checkbox
                  checked={selectedCategories.includes(category)}
                  onChange={() => handleCategoryCheckboxChange(category)}
                  name={`${category}Checkbox`}
                  color="primary"
                  disabled={!availableCategories.includes(category)}
                />
              )}
              label={category}
            />
          </MenuItem>
        ))}
      </Menu>
    </div>
  );
}

export default PreferenceSelector;
