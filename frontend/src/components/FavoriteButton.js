import React from 'react';

const FavoriteButton = ({ isFavorite, onToggle }) => (
  <button onClick={onToggle}>
    {isFavorite ? "Удалить из избранного" : "Добавить в избранное"}
  </button>
);

export default FavoriteButton;
