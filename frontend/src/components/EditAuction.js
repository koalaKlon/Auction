import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useParams, useNavigate } from 'react-router-dom';
import '../styles/EditAuction.css';

const EditAuction = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [auction, setAuction] = useState(null);
  const [error, setError] = useState(null);
  const [file, setFile] = useState(null);

  useEffect(() => {
    axios.get(`http://localhost:8000/api/auction/${id}/`)
      .then(response => {
        setAuction(response.data);
      })
      .catch(err => {
        setError('Ошибка загрузки данных');
      });
  }, [id]);

  const handleChange = (e) => {
    if (e.target.type === 'file') {
      setFile(e.target.files[0]);
    } else {
      setAuction({ ...auction, [e.target.name]: e.target.value });
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    const token = localStorage.getItem("access_token");
    const formData = new FormData();
    formData.append('name', auction.name);
    formData.append('start_time', auction.start_time);
    formData.append('end_time', auction.end_time);

    if (file) {
      formData.append('banner_image', file);
    }

    axios.put(`http://localhost:8000/api/auction/${id}/update/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        Authorization: `Bearer ${token}`,
      },
    })
    .then(() => {
      navigate(`/auctions/${id}`);
    })
    .catch(err => {
      setError('Ошибка при сохранении данных');
    });
  };

  const handleDelete = () => {
    const confirmed = window.confirm("Вы уверены, что хотите удалить этот аукцион?");
    if (!confirmed) return;

    const token = localStorage.getItem("access_token");
    axios.delete(`http://localhost:8000/api/auction/${id}/delete/`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
    .then(() => {
      navigate('/'); // Перенаправляем на главную страницу после удаления
    })
    .catch(err => {
      setError('Ошибка при удалении аукциона');
    });
  };

  if (!auction) return <div className="loading">Загрузка...</div>;
  if (error) return <div className="error">{error}</div>;

  const formatDate = (date) => {
    return new Date(date).toISOString().slice(0, 16);
  };

  return (
    <form onSubmit={handleSubmit} className="edit-auction-form">
      <div className="form-group">
        <label htmlFor="banner_image">Текущее изображение:
          <input
            type="file"
            name="banner_image"
            accept="image/*"
            onChange={handleChange}
            className="file-input"
          />
        </label>
      </div>
      <div className="form-group">
        <label htmlFor="start_time">Дата начала:
          <input
            type="datetime-local"
            name="start_time"
            value={formatDate(auction.start_time)}
            onChange={handleChange}
            className="datetime-input"
          />
        </label>
      </div>
      <div className="form-group">
        <label htmlFor="end_time">Дата окончания:
          <input
            type="datetime-local"
            name="end_time"
            value={formatDate(auction.end_time)}
            onChange={handleChange}
            className="datetime-input"
          />
        </label>
      </div>

      <button type="submit" className="submit-btn">Сохранить изменения</button>
      <button type="button" onClick={handleDelete} className="delete-btn">
        Удалить аукцион
      </button>
    </form>
  );
};

export default EditAuction;
