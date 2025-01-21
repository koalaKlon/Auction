import React from 'react';

const BidsList = ({ bids }) => {
  if (!bids || bids.length === 0) {
    return <p>Ставок нет.</p>;
  }

  return (
    <div className="bids-list">
      <h3>Все ставки</h3>
      <ul>
        {bids.map((bid) => (
          <li key={bid.id}>
            <p>Ставка: {bid.amount}</p>
            <p>Пользователь: {bid.buyer_username}</p>
            <p>Время: {new Date(bid.timestamp).toLocaleString()}</p>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default BidsList;
