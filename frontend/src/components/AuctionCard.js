import React, { useEffect, useState } from 'react';
import api from '../api/api'; // Исправлено: используем api
import '../styles/AuctionCard.css';
import { useNavigate } from 'react-router-dom';

const AuctionCard = React.memo(({ filters }) => {
  const [auctions, setAuctions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchAuctions = async () => {
      setLoading(true);
      try {
        // Исправлено: используем api.get для получения данных
        const response = await api.get('auctions/', { params: filters });
        setAuctions(response.data);
      } catch (err) {
        setError('Ошибка загрузки данных');
      } finally {
        setLoading(false);
      }
    };

    fetchAuctions();
  }, [filters]);

  if (loading) return <div>Загрузка...</div>;
  if (error) return <div>{error}</div>;

  return (
    <div className="cardContainer">
      {auctions.length === 0 ? (
        <div className="card">
          <span>Нет доступных аукционов</span>
        </div>
      ) : (
        auctions.map((auction) => (
          <div
            key={auction.id}
            className="card"
            onClick={() => navigate(`/auctions/${auction.id}/`)} // Исправлено: добавлены кавычки
          >
            <div className="product-name">{auction.product_name || 'Без названия'}</div>
            <div className="auction-info">
              <div className="info-row status">
                <strong>Статус:</strong> {auction.status || 'Неизвестный статус'}
              </div>
              <div className="info-row starting-price">
                <strong>Начальная ставка:</strong> {auction.starting_price || 'Не установлена'}
              </div>
              <div className="info-row auction-time">
                <strong>Начало:</strong> {new Date(auction.start_time).toLocaleString()}
              </div>
              <div className="info-row auction-time">
                <strong>Конец:</strong> {new Date(auction.end_time).toLocaleString()}
              </div>
              {auction.banner_image && (
                <div className="info-row auction-banner">
                  <img src={auction.banner_image} alt="banner" />
                </div>
              )}
            </div>
          </div>
        ))
      )}
    </div>
  );
});

export default AuctionCard;
