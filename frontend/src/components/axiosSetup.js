import axios from 'axios';

// Функция для обновления токена
// Функция для обновления токена
const refreshToken = async () => {
  try {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
      return null;
    }

    const response = await axios.post('/api/token/refresh/', {
      refresh: refreshToken,
    });

    localStorage.setItem('access_token', response.data.access);
    return response.data.access;
  } catch (error) {
    console.error('Ошибка обновления токена:', error);
    // Если ошибка при обновлении, токен истек, возможно, нужно удалить оба токена и перенаправить на страницу входа
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    return null;
  }
};

// Добавляем перехватчик для подстановки токена в каждый запрос
axios.interceptors.request.use(
  async (config) => {
    const accessToken = localStorage.getItem('access_token');
    if (accessToken) {
      config.headers['Authorization'] = `Bearer ${accessToken}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Перехватчик для обработки ошибок 401 (неавторизован)
axios.interceptors.response.use(
  (response) => response, // успешный ответ
  async (error) => {
    const originalRequest = error.config;

    // Если ошибка 401 и токен истек, пробуем обновить токен
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const newAccessToken = await refreshToken();
      if (newAccessToken) {
        originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;
        // Повторяем запрос с новым токеном
        return axios(originalRequest);
      }
      // Если обновить токен не удалось, перенаправляем на страницу входа
      window.location.href = '/login';
    }

    return Promise.reject(error);
  }
);


export default axios;
