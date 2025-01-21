import axios from 'axios';

const API_URL = 'http://localhost:8000/api/';  // Объявляем глобальную переменную

const getAuthHeaders = () => {
  const token = localStorage.getItem('access_token');
  if (!token) {
    throw new Error('Необходима авторизация. Токен отсутствует.');
  }
  return { 'Authorization': `Bearer ${token}` };
};
export const fetchStats = async () => {
  try {
    const response = await axios.get(`${API_URL}stats/`, {  // без лишнего слэша
      headers: getAuthHeaders(),
    });
    
    return response.data;
  } catch (error) {
    console.error("Error fetching stats:", error);
    // Обработка ошибок (например, вывод уведомления)
  }
};
// Создаем экземпляр axios для общения с сервером
const api = axios.create({
  baseURL: API_URL,  // Используем переменную API_URL
  headers: {
    'Content-Type': 'application/json',
  },
});
const handleApiError = (error) => {
  if (error.response) {
    // Сервер ответил с ошибкой
    console.error(`Ошибка ${error.response.status}: ${error.response.data.detail || error.response.data}`);
  } else if (error.request) {
    // Запрос был отправлен, но ответа нет
    console.error('Сервер не отвечает. Проверьте соединение.');
  } else {
    // Что-то пошло не так при настройке запроса
    console.error(`Ошибка: ${error.message}`);
  }
  throw error; // Пробрасываем ошибку дальше для обработки
};

// Измененная функция для регистрации пользователя с почтой
export const registerUser = (username, password, email) => {
  return api.post('register/', { username, password, email });
};

export const loginUser = (username, password) => {
  return api.post('login/', { username, password });
};
// Функции для работы с API
export const getProducts = () => api.get('products/');
export const getProductDetail = (id) => api.get(`products/${id}/`);
export const getAuctions = (filters = {}) => {
  const params = new URLSearchParams(filters).toString();
  return api.get(`auctions/?${params}`);
};

export const getAuctionDetail = (id) => api.get(`auctions/${id}/`);
export const createAuction = async (auctionData) => {
  try {
    return await api.post('create-auction/', auctionData, {
      headers: getAuthHeaders(),
    });
  } catch (error) {
    handleApiError(error);
  }
};
export const logoutUser = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  console.log('Вы вышли из системы.');
};
export const createProduct = (productData) => {
  const token = localStorage.getItem('access_token'); // Получаем токен из localStorage

  return api.post('create-product/', productData, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
};
export const getCategories = async () => {
  const token = localStorage.getItem('access_token');
  return api.get('categories/', {
    headers: {
      'Authorization': `Bearer ${token}`, // Если категории доступны только авторизованным пользователям
    },
  });
};
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Проверяем, что ошибка связана с авторизацией и не является повторным запросом
    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // Получаем refresh_token из localStorage
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) {
          throw new Error('Refresh token отсутствует');
        }

        // Отправляем запрос на обновление access_token
        const { data } = await axios.post(`${API_URL}token/refresh/`, {
          refresh_token: refreshToken,
        });

        // Обновляем access_token в localStorage
        localStorage.setItem('access_token', data.access_token);

        // Устанавливаем новый токен в заголовок запроса
        originalRequest.headers['Authorization'] = `Bearer ${data.access_token}`;

        // Повторяем оригинальный запрос
        return api(originalRequest);
      } catch (refreshError) {
        console.error('Ошибка обновления токена:', refreshError);
        // Если обновление не удалось, удаляем токены и перенаправляем на страницу входа
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    // Если ошибка не связана с авторизацией, пробрасываем её дальше
    return Promise.reject(error);
  }
);
// Экспортируйте экземпляр axios для дальнейшего использования
export default api;
