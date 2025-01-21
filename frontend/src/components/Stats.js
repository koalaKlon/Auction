// components/Stats.js
import React, { useEffect, useState } from 'react';
import { fetchStats } from '../api/api';

const Stats = () => {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    const getStats = async () => {
      const data = await fetchStats();
      setStats(data);
    };
    getStats();
  }, []);

  const handleAdminRedirect = () => {
    window.location.href = 'http://localhost:8000/admin';
  };

  if (!stats) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <h1>Статистика</h1>
      <ul>
        <li>Всего пользователей: {stats.total_users}</li>
        <li>Активных пользователей: {stats.active_users}</li>
        <li>Всего продуктов: {stats.total_products}</li>
        <li>Активных аукционов: {stats.active_auctions}</li>
        <li>Всего ставок: {stats.total_bids}</li>
        <li>Средняя ставка: {stats.average_bid.toFixed(2)}</li>
      </ul>

      <button onClick={handleAdminRedirect}>Перейти в админ панель</button>
    </div>
  );
};

export default Stats;
