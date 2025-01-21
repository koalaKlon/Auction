import React from 'react';
import { Link } from 'react-router-dom';

const AuctionInfo = ({ auction, winner }) => (
  <div>
    <h1>{auction.product_name || 'Неизвестный товар'}</h1>
    <p><strong>Тип аукциона:</strong> {auction.auction_type}</p>
    <p><strong>Текущий лидер:</strong> {auction.current_leader || 'Нет ставок'}</p>
    <p><strong>Победитель:</strong> {winner}</p>
    <p><strong>Текущая ставка:</strong> {auction.current_bid ? `${auction.current_bid} ₽` : 'Ставки нет'}</p>
    <p><strong>Начало:</strong> {new Date(auction.start_time).toLocaleString()}</p>
    <p><strong>Конец:</strong> {new Date(auction.end_time).toLocaleString()}</p>
    <p className="seller-link">
      <strong>Продавец: </strong>
      {auction.seller && (
        <Link to={`/profile/${auction.seller.id}`}>
          {auction.seller.username || "Профиль продавца"}
        </Link>
      )}
    </p>
  </div>
);

export default AuctionInfo;
