import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import '../styles/AuctionList.css';
import AuctionCard from './AuctionCard';
import { useAuth } from './AuthContext';
import Filters from './Filters';
import Header from './Header';

const AuctionList = () => {
  const [filters, setFilters] = useState({
    category: '',
    type: '',
    search: '',
    sort_by: 'start_time',
  });
  const [appliedFilters, setAppliedFilters] = useState(filters);
  const { isAuthenticated, login, logout } = useAuth();
  const [categories, setCategories] = useState([]);
  const [, forceUpdate] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const checkAuthentication = async () => {
      const accessToken = localStorage.getItem('access_token');
      if (!accessToken) {
        try {
          const response = await axios.post('/api/token/refresh/', {
            refresh: localStorage.getItem('refresh_token'),
          });
          localStorage.setItem('access_token', response.data.access);
          login();
        } catch {
          logout();
        }
      } else {
        login();
      }
    };
    checkAuthentication();
  }, [login, logout]);

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/categories/');
        setCategories(response.data);
      } catch (error) {
        console.error("Ошибка загрузки категорий:", error);
      }
    };
    fetchCategories();
  }, []);

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters((prev) => ({ ...prev, [name]: value }));
  };

  const applyFilters = () => {
    setAppliedFilters(filters);
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    forceUpdate((prev) => !prev);
    navigate('/');
  };

  return (
    <div className="auction-list">
      <Header isAuthenticated={isAuthenticated} onLogout={handleLogout} />
      <Filters filters={filters} onFilterChange={handleFilterChange} onApplyFilters={applyFilters} categories={categories} />
      <AuctionCard filters={appliedFilters} />
    </div>
  );
};

export default AuctionList;
