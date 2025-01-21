import React from 'react';
import { useAuth } from './AuthContext'; // Импортируем хук для аутентификации

const BidControls = ({ bidAmount, onPlaceBid, onRaiseBid, onBidAmountChange }) => {
  const { user } = useAuth(); // Получаем текущего пользователя

  if (!user || user.role !== 'user') {
    // Если пользователь не авторизован или его роль не 'user', не показываем интерфейс для ставки
    return <p>Для размещения ставки вам нужно быть покупателем.</p>;
  }

  return (
    <div>
      <h3>Сделать ставку</h3>
      <input
        type="number"
        value={bidAmount}
        onChange={(e) => onBidAmountChange(e.target.value)}
        placeholder="Введите сумму ставки"
      />
      <button onClick={onPlaceBid}>Сделать ставку</button>
      <button onClick={onRaiseBid}>Повысить ставку на 10%</button>
    </div>
  );
};

export default BidControls;
