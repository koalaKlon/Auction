import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/Login.css';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [fieldErrors, setFieldErrors] = useState({ username: '', password: '' }); // Для ошибок полей
  const navigate = useNavigate();

  const validateFields = () => {
    let isValid = true;
    const errors = { username: '', password: '' };

    if (!username.trim()) {
      errors.username = 'Имя пользователя обязательно';
      isValid = false;
    }

    if (!password) {
      errors.password = 'Пароль обязателен';
      isValid = false;
    } else if (password.length < 6) {
      errors.password = 'Пароль должен содержать минимум 6 символов';
      isValid = false;
    }

    setFieldErrors(errors);
    return isValid;
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!validateFields()) {
      return; // Останавливаем выполнение, если валидация не прошла
    }

    fetch('http://localhost:8000/api/login/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
    })
      .then((response) => {
        if (!response.ok) {
          return response.json().then((errData) => {
            throw new Error(`Ошибка: ${errData.error || 'Неизвестная ошибка'}`);
          });
        }
        return response.json();
      })
      .then((data) => {
        if (data.access && data.refresh) {
          alert('Авторизация успешна!');
          localStorage.setItem('access_token', data.access);
          localStorage.setItem('refresh_token', data.refresh);

          // Выводим токены в консоль
          console.log('Access Token:', data.access);
          console.log('Refresh Token:', data.refresh);

          navigate('/');
        } else {
          setError('Неверный логин или пароль');
        }
      })
      .catch((error) => {
        console.error('Ошибка:', error);
        setError(error.message);
      });
  };

  return (
    <div className="login-container">
      <h2 className="login-title">Авторизация</h2>
      <form className="login-form" onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="username">Имя пользователя</label>
          <input
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          {fieldErrors.username && <p className="field-error">{fieldErrors.username}</p>}
        </div>
        <div className="form-group">
          <label htmlFor="password">Пароль</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          {fieldErrors.password && <p className="field-error">{fieldErrors.password}</p>}
        </div>
        {error && <p className="error-message">{error}</p>}
        <button className="submit-button" type="submit">
          Войти
        </button>
      </form>
    </div>
  );
};

export default Login;
