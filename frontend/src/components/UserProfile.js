import React, { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import StarRatingInput from './StarRatingInput';
import AuctionCardUser from './AuctionCardUser'; // Импортируем карточку аукциона
import '../styles/StarRatingInput.css'; // Создайте CSS файл для стилизации

const UserProfile = () => {
  const { userId } = useParams();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const fetchProfile = useCallback(async () => {
    setLoading(true);
    try {
      const response = await axios.get(`http://localhost:8000/api/users/${userId}/profile/`);
      setProfile(response.data);
    } catch (err) {
      console.error('Ошибка загрузки:', err);
      setError(err.response?.data?.error || 'Ошибка загрузки профиля');
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    fetchProfile();
  }, [fetchProfile]);

  const handleRatingSubmit = async (rating) => {
    try {
        const token = localStorage.getItem("access_token"); // Получаем токен из локального хранилища
        const response = await axios.post(
            `http://localhost:8000/api/users/${userId}/rate/`,
            { rating },
            {
                headers: {
                    Authorization: `Bearer ${token}`, // Передаем токен в заголовке
                },
            }
        );
        setProfile((prevProfile) => ({
            ...prevProfile,
            rating: response.data.updated_rating,
        }));
    } catch (err) {
        console.error('Ошибка при выставлении рейтинга:', err);
        setError(err.response?.data?.error || 'Ошибка при выставлении рейтинга');
    }
};


  if (loading) return <div>Загрузка...</div>;
  if (error) return <div>Ошибка: {error}</div>;

  return (
    <div className="profile-container">
      <h2>Профиль пользователя</h2>
      {profile.profile_picture && (
        <img
          src={profile.profile_picture}
          alt={`${profile.username}'s profile`}
          className="profile-picture"
        />
      )}
      <p><strong>Псевдоним:</strong> {profile.username}</p>
      <p><strong>Email:</strong> {profile.email}</p>
      <p><strong>Телефон:</strong> {profile.phone_number}</p>
  
      <p><strong>Рейтинг:</strong> {profile.rating || 0}</p>
      <div className="rating-container">
        <StarRatingInput
          initialRating={profile.rating || null}
          onSubmit={handleRatingSubmit}
        />
      </div>
  
      <h3>Аукционы пользователя</h3>
      <div className="auctions-list">
        {profile.auctions.length > 0 ? (
          profile.auctions.map((auction) => <AuctionCardUser key={auction.id} auction={auction} />)
        ) : (
          <p>У пользователя нет активных аукционов.</p>
        )}
      </div>
    </div>
  );
};

export default UserProfile;
