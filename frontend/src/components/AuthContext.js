import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);  // State for the user

  const loadUser = async () => {
    if (isAuthenticated && user) return;  // Если пользователь уже загружен, не делаем запрос

    try {
      const accessToken = localStorage.getItem('access_token');
      if (accessToken) {
        const response = await axios.get('http://localhost:8000/api/current_user/', {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        });
        console.log(response);
        setUser(response.data);
        setIsAuthenticated(true);
      } else {
        console.error('No access token available');
        setUser(null);
        setIsAuthenticated(false);
      }
    } catch (error) {
      console.error('Failed to load user:', error);
      setUser(null);
      setIsAuthenticated(false);
    }
  };

  // Функция для изменения роли пользователя
  const changeRole = async () => {
    try {
      const accessToken = localStorage.getItem('access_token');
      const response = await axios.post('http://localhost:8000/api/users/change-role/', {}, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });
  
      console.log(response.data);
      if (response.data.message) {
        setUser(prevUser => ({
          ...prevUser,
          role: response.data.message.includes('seller') ? 'seller' : 'user',
        }));
      }
    } catch (error) {
      console.error('Error changing role:', error.response ? error.response.data : error.message);
    }
  };
  
  useEffect(() => {
    loadUser(); // Загрузка пользователя при монтировании компонента
  }, []);  // Этот эффект выполняется один раз при монтировании

  // Логика для входа
  const login = async () => {
    setIsAuthenticated(true);
    loadUser();  // Загрузка данных пользователя при логине
  };

  // Логика для выхода
  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setIsAuthenticated(false);
    setUser(null);  // Очищаем данные пользователя при выходе
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, user, login, logout, changeRole }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
