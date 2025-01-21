import React from 'react';
import '../styles/Filter.css';

const Filters = ({ filters, onFilterChange, onApplyFilters, categories}) => {
  return (
    <div className="filters-container">
      <div className="search-container">
        <input
          type="text"
          name="search"
          placeholder="Поиск по имени товара"
          value={filters.search}
          onChange={onFilterChange}
          className="filter-input"
        />
        <button className="apply-filters-btn" onClick={onApplyFilters}>
        🔍
        </button>
      </div>

      <div className="filters-dropdowns">
      <select
        name="category"
        value={filters.category}
        onChange={onFilterChange}
        className="filter-select"
      >
        <option value="">Все категории</option>
        {categories.map((category) => (
          <option key={category.id} value={category.id}>
            {category.name}
          </option>
        ))}
      </select>
        <select
          name="type"
          value={filters.type}
          onChange={onFilterChange}
          className="filter-select"
        >
          <option value="">Все типы</option>
          <option value="single">Одиночный</option>
          <option value="multiple">Множественный</option>
        </select>
        <select
          name="sort_by"
          value={filters.sort_by}
          onChange={onFilterChange}
          className="filter-select"
        >
          <option value="start_time">Дата начала</option>
          <option value="end_time">Дата окончания</option>
        </select>
      </div>
    </div>
  );
};

export default Filters;
