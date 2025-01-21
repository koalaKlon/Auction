import React, { useState, useEffect } from 'react';

const EditProfile = () => {
  const [profileData, setProfileData] = useState({
    phone_number: '',
    first_name: '',
    last_name: '',
    profile_picture: null,
    rating: 0,
  });
  const [error, setError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    // Получаем текущие данные профиля при монтировании компонента
    const accessToken = localStorage.getItem('access_token');

    if (accessToken) {
      fetch('http://localhost:8000/api/profile/', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
        },
      })
        .then((response) => response.json())
        .then((data) => {
          setProfileData(data);  // Загружаем данные в состояние
        })
        .catch((err) => setError('Ошибка загрузки профиля'));
    }
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setProfileData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setProfileData((prevData) => ({
      ...prevData,
      profile_picture: file,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setIsSubmitting(true);
  
    const accessToken = localStorage.getItem('access_token');
    const formData = new FormData();
  
    // Добавляем только те поля, которые были изменены или содержат данные
    if (profileData.phone_number) {
      console.log('Phone number:', profileData.phone_number);  // Выводим номер телефона
      formData.append('phone_number', profileData.phone_number);
    }
    if (profileData.first_name) formData.append('first_name', profileData.first_name);
    if (profileData.last_name) formData.append('last_name', profileData.last_name);
    if (profileData.rating !== undefined) formData.append('rating', profileData.rating);
    if (profileData.profile_picture) formData.append('profile_picture', profileData.profile_picture);
  
    fetch('http://localhost:8000/api/profile/update/', {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
      },
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        console.log('Server response:', data);  // Проверка данных, возвращаемых сервером
        setIsSubmitting(false);
        
        if (data.error) {
          setError(data.error);
          window.location.href = '/profile';  // Перенаправляем на профиль в случае ошибки
        } else {
          alert('Профиль обновлен');
          setProfileData(data);  // Обновляем данные в интерфейсе
          window.location.href = '/profile';  // Перенаправляем на профиль в случае успеха
        }
      })      
      .catch((err) => {
        setIsSubmitting(false);
        setError('Ошибка при обновлении');
        window.location.href = '/profile';  // Перенаправляем на профиль в случае ошибки
      });
  };
  

  return (
    <div>
      <h2>Редактировать профиль</h2>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <form onSubmit={handleSubmit}>
        <div>
          <label>Имя</label>
          <input
            type="text"
            name="first_name"
            value={profileData.first_name}
            onChange={handleInputChange}
          />
        </div>
        <div>
          <label>Фамилия</label>
          <input
            type="text"
            name="last_name"
            value={profileData.last_name}
            onChange={handleInputChange}
          />
        </div>
        <div>
          <label>Номер телефона</label>
          <input
            type="text"
            name="phone_number"
            value={profileData.phone_number}
            onChange={handleInputChange}
          />
        </div>
        <div>
          <label>Фото профиля</label>
          <input
            type="file"
            name="profile_picture"
            onChange={handleFileChange}
          />
        </div>
        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Обновление...' : 'Сохранить'}
        </button>
      </form>
    </div>
  );
};

export default EditProfile;
