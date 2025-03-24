import React, { useEffect, useState } from 'react';
import { fetchStats } from '../api/api';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  PieChart,
  Pie,
  Cell,
  Legend,
  LineChart,
  Line,
  ResponsiveContainer,
} from 'recharts';

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

  // Данные для круговой диаграммы (активные пользователи)
  const pieDataUsers = [
    { name: 'Активные пользователи', value: stats.active_users },
    { name: 'Неактивные пользователи', value: stats.total_users - stats.active_users },
  ];

  // Данные для круговой диаграммы (аукционы)
  const pieDataAuctions = [
    { name: 'Активные аукционы', value: stats.active_auctions },
    { name: 'Завершенные аукционы', value: stats.total_products - stats.active_auctions },
  ];

  // Данные для столбчатой диаграммы (общая статистика)
  const barData = [
    { name: 'Пользователи', value: stats.total_users },
    { name: 'Продукты', value: stats.total_products },
    { name: 'Аукционы', value: stats.active_auctions },
    { name: 'Ставки', value: stats.total_bids },
  ];

  // Данные для линейной диаграммы
  const lineData = [
    { name: 'Средняя ставка', value: stats.average_bid },
    { name: 'Макс. ставка', value: stats.max_bid || stats.average_bid * 1.5 }, // примерное значение
    { name: 'Мин. ставка', value: stats.min_bid || stats.average_bid * 0.5 },
  ];

  const COLORS = ['#0088FE', '#FF8042', '#00C49F', '#FFBB28'];

  return (
    <div>
      <h1>Статистика</h1>

      <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'space-around', margin: '20px 0' }}>
        {/* Круговая диаграмма пользователей */}
        <PieChart width={300} height={300}>
          <Pie
            data={pieDataUsers}
            cx="50%"
            cy="50%"
            outerRadius={100}
            fill="#8884d8"
            dataKey="value"
            label
          >
            {pieDataUsers.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Legend />
        </PieChart>

        {/* Круговая диаграмма аукционов */}
        <PieChart width={300} height={300}>
          <Pie
            data={pieDataAuctions}
            cx="50%"
            cy="50%"
            outerRadius={100}
            fill="#82ca9d"
            dataKey="value"
            label
          >
            {pieDataAuctions.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Legend />
        </PieChart>

        {/* Столбчатая диаграмма */}
        <BarChart width={400} height={300} data={barData}>
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="value" fill="#82ca9d" />
        </BarChart>

        {/* Линейная диаграмма */}
        <ResponsiveContainer width="90%" height={300}>
          <LineChart data={lineData}>
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="value" stroke="#FF8042" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>

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
