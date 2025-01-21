import React from 'react';
import { Link } from 'react-router-dom';
import '../styles/AuctionCardUser.css';

const AuctionCardUser = ({ auction }) => {
  return (
    <div className="auction-card">
      {auction.banner_image && (
        <img 
          src={auction.banner_image} 
          alt="Изображение аукциона" 
        />
      )}
      <div className="auction-info">
        <h3 className="auction-title">{auction.auction_type}</h3>
        <div className="info-row">
          <strong>Начало:</strong> {new Date(auction.start_time).toLocaleString()}
        </div>
        <div className="info-row">
          <strong>Окончание:</strong> {new Date(auction.end_time).toLocaleString()}
        </div>
        <div className="info-row">
          <strong>Статус:</strong> {auction.status}
        </div>
        <Link to={`/auctions/${auction.id}`} className="auction-link">
          Подробнее
        </Link>
      </div>
    </div>
  );
};

export default AuctionCardUser;
