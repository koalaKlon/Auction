import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useParams, useNavigate } from 'react-router-dom';
import AuctionInfo from './AuctionInfo';
import BidControls from './BidControls';
import FavoriteButton from './FavoriteButton';
import ProductList from './ProductList';
import BidsList from './BidsList';
import Chat from './Chat';
import '../styles/AuctionDetail.css';

const AuctionDetail = () => {
  const { id } = useParams();
  const [auction, setAuction] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isOwner, setIsOwner] = useState(false);
  const [lastBidTime, setLastBidTime] = useState(null);
  const [isFavorite, setIsFavorite] = useState(false);
  const [bidAmount, setBidAmount] = useState('');
  const [isAuctionEnded, setIsAuctionEnded] = useState(false);
  const [winner, setWinner] = useState(null);
  const [currentUser, setCurrentUser] = useState(null);

  const navigate = useNavigate();

  useEffect(() => {
    const accessToken = localStorage.getItem('access_token');

    // Загружаем данные аукциона
    axios
      .get(`http://localhost:8000/api/auction/${id}/`)
      .then((response) => {
        setAuction(response.data);
        setIsAuctionEnded(response.data.status === 'finished');
        if (response.data.status === 'finished') {
          setWinner(response.data.winner);
        }

        if (accessToken) {
          axios
            .get('http://localhost:8000/api/current_user/', {
              headers: { Authorization: `Bearer ${accessToken}` },
            })
            .then((profileResponse) => {
              const user = profileResponse.data;
              setCurrentUser(user);
              if (user.id === response.data.seller.id) {
                setIsOwner(true);
              }
            })
            .catch((profileError) =>
              console.error('Ошибка загрузки данных пользователя:', profileError)
            );

          axios
            .get(`http://localhost:8000/api/auction/${id}/is_favorite/`, {
              headers: { Authorization: `Bearer ${accessToken}` },
            })
            .then((favoriteResponse) => {
              setIsFavorite(favoriteResponse.data.is_favorite);
            })
            .catch((err) => console.error('Ошибка при проверке избранного:', err));
        }
      })
      .catch((err) => {
        console.error('Ошибка загрузки данных аукциона:', err);
        setError('Ошибка загрузки данных аукциона');
      })
      .finally(() => setLoading(false));

    // Устанавливаем WebSocket-соединение
    const socket = new WebSocket(`ws://localhost:8000/ws/auction/${id}/`);

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
    
      if (data.status) {
        // Если статус обновлен
        setAuction((prev) => ({
          ...prev,
          status: data.status,
        }));
        setIsAuctionEnded(data.status === 'finished');
        if (data.status === 'finished' && data.winner) {
          setWinner(data.winner);
          setIsAuctionEnded(true);
          alert(`Аукцион завершен! Победитель: ${data.winner}`);
        }
      } else if (data.message) {
        // Обновление ставок
        setAuction((prev) => ({
          ...prev,
          current_bid: data.message.current_bid,
          current_leader: data.message.current_leader,
        }));
        setLastBidTime(Date.now());
      }
    };
    

    return () => socket.close(); // Закрываем WebSocket при размонтировании
  }, [id]);

  const handleToggleFavorite = () => {
    const accessToken = localStorage.getItem('access_token');
    if (!accessToken) {
      alert('Пожалуйста, войдите в систему, чтобы добавить аукцион в избранное.');
      return;
    }

    const url = `http://localhost:8000/api/auction/${id}/${isFavorite ? 'favorite/remove/' : 'favorite/'}`;
    const method = isFavorite ? 'delete' : 'post';

    axios({ method, url, headers: { Authorization: `Bearer ${accessToken}` } })
      .then(() => {
        setIsFavorite(!isFavorite);
        alert(`Аукцион ${isFavorite ? 'удален' : 'добавлен'} в избранное!`);
      })
      .catch(() =>
        alert(`Ошибка при ${isFavorite ? 'удалении' : 'добавлении'} аукциона в избранное.`)
      );
  };

  const handlePlaceBid = () => {
    if (!bidAmount || parseFloat(bidAmount) <= parseFloat(auction.current_bid || 0)) {
      alert('Ставка должна быть выше текущей!');
      return;
    }

    const accessToken = localStorage.getItem('access_token');
    if (!accessToken) {
      alert('Пожалуйста, войдите в систему, чтобы сделать ставку.');
      return;
    }

    axios
      .post(
        `http://localhost:8000/api/auction/${id}/bid/`,
        { amount: bidAmount },
        { headers: { Authorization: `Bearer ${accessToken}` } }
      )
      .then((response) => {
        alert(response.data.message);
        setAuction((prevAuction) => ({  
          ...prevAuction,
          current_bid: response.data.current_bid,
          current_leader: response.data.current_leader,
        }));
        setBidAmount('');
        setLastBidTime(Date.now());
        setIsAuctionEnded(false);
      })
      .catch((err) => {
        console.error(err);
        alert('Ошибка при размещении ставки.');
      });
  };

  const handleRaiseBid = () => {
    const increment = auction.current_bid ? parseFloat(auction.current_bid) * 0.1 : 10;
    setBidAmount((parseFloat(auction.current_bid || 0) + increment).toFixed(2));
    handlePlaceBid();
  };
  useEffect(() => {
    const interval = setInterval(() => {
      axios.get(`http://localhost:8000/api/auction/${id}/`).then((response) => {
        setAuction(response.data);
        if (response.data.status === 'finished') {
          setIsAuctionEnded(true);
          setWinner(response.data.winner);
        }
      });
    }, 1000); 
  
    return () => clearInterval(interval);
  }, [id]);
  
  if (loading) return <div>Загрузка...</div>;
  if (error) return <div>{error}</div>;

  return (
    <div className="auction-detail-container">
      {auction.banner_image && (
        <img
          src={auction.banner_image}
          alt="баннер"
          style={{ width: '100%', maxWidth: '100%', height: 'auto' }}
        />
      )}

      <AuctionInfo auction={auction} winner={winner} />
      <FavoriteButton isFavorite={isFavorite} onToggle={handleToggleFavorite} />
      {auction.status === 'active' && !isAuctionEnded && (
        <BidControls
          bidAmount={bidAmount}
          onPlaceBid={handlePlaceBid}
          onRaiseBid={handleRaiseBid}
          onBidAmountChange={setBidAmount}
        />
      )}

      {isAuctionEnded && <p>Аукцион завершен!</p>}
      {isOwner && isAuctionEnded && auction.all_bids && (
        <BidsList bids={auction.all_bids} />
      )}

      {isOwner && auction.status === 'planned' && (
        <button onClick={() => navigate(`/auction/${id}/update`)}>Редактировать аукцион</button>
      )}
      {isAuctionEnded && winner && (
  <Chat currentUser={currentUser} winner={winner} seller={auction.seller} />
)}

      <ProductList
        auctionType={auction.auction_type}
        products={auction.products}
        product={auction.product}
        isOwner={isOwner}
        navigate={navigate}
        status={auction.status}
      />
    </div>
  );
};

export default AuctionDetail;
