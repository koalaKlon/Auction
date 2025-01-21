import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { registerUser } from '../api/api';
import '../styles/Register.css'; // Подключение CSS

const RegisterForm = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [fieldErrors, setFieldErrors] = useState({ username: '', email: '', password: '' });
  const navigate = useNavigate();

  const validateFields = () => {
    let isValid = true;
    const errors = { username: '', email: '', password: '' };

    if (!username.trim()) {
      errors.username = 'Имя пользователя обязательно';
      isValid = false;
    }

    if (!email.trim()) {
      errors.email = 'Электронная почта обязательна';
      isValid = false;
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      errors.email = 'Некорректный формат электронной почты';
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

  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');

    if (!validateFields()) {
      return;
    }

    try {
      const response = await registerUser(username, password, email);

      if (response.data && response.data.access && response.data.refresh) {
        console.log('Пользователь зарегистрирован:', response.data);

        localStorage.setItem('access_token', response.data.access);
        localStorage.setItem('refresh_token', response.data.refresh);

        navigate('/');
      } else {
        setError('Произошла ошибка при регистрации');
      }
    } catch (error) {
      console.error('Ошибка регистрации:', error);
      setError('Произошла ошибка при регистрации');
    }
  };

  return (
    <div className="register-container">
      <h2 className="register-title">Регистрация</h2>
      <form onSubmit={handleRegister} className="register-form">
        <div className="form-group">
          <input
            type="text"
            placeholder="Имя пользователя"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="form-input"
          />
          {fieldErrors.username && <p className="error-message">{fieldErrors.username}</p>}
        </div>
        <div className="form-group">
          <input
            type="email"
            placeholder="Электронная почта"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="form-input"
          />
          {fieldErrors.email && <p className="error-message">{fieldErrors.email}</p>}
        </div>
        <div className="form-group">
          <input
            type="password"
            placeholder="Пароль"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="form-input"
          />
          {fieldErrors.password && <p className="error-message">{fieldErrors.password}</p>}
        </div>
        <button type="submit" className="submit-button">Зарегистрироваться</button>
        {error && <p className="error-message">{error}</p>}
      </form>
    </div>
  );
};

export default RegisterForm;
