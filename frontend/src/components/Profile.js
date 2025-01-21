import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import StarRatingInput from './StarRatingInput';
import axios from 'axios';
import '../styles/Profile.css';

const tabs = ['Избранное', 'Мои аукционы', 'Участвовал', 'История ставок'];

const Profile = () => {
    const [profileData, setProfileData] = useState(null);
    const [error, setError] = useState(null);
    const [activeTab, setActiveTab] = useState(tabs[0]);
    const [filter, setFilter] = useState('all'); 
    const [filteredAuctions, setFilteredAuctions] = useState([]);
    
    const handleRemoveFromFavorites = (auctionId) => {
        const accessToken = localStorage.getItem('access_token');
        if (accessToken) {
            axios
                .delete(`http://localhost:8000/api/auction/${auctionId}/favorite/remove/`, {
                    headers: { Authorization: `Bearer ${accessToken}` },
                })
                .then(() => {
                    setProfileData((prevData) => ({
                        ...prevData,
                        favorites: prevData.favorites.filter((auction) => auction.id !== auctionId),
                    }));
                    alert('Аукцион удален из избранного!');
                })
                .catch(() => alert('Ошибка при удалении из избранного'));
        }
    };
    const handleTabChange = (tab) => {
        setActiveTab(tab);
        if (tab !== 'Участвовал') {
            setFilter('all'); // Сброс фильтра
            setFilteredAuctions([]); // Сброс отфильтрованных данных
        }
    };
    
    
    useEffect(() => {
        if (activeTab === 'Участвовал') {
            const uniqueAuctions = Array.from(
                new Set((profileData?.participated_auctions || []).map(a => a.id))
            ).map(id => (profileData?.participated_auctions || []).find(a => a.id === id));
    
            const filtered = uniqueAuctions.filter((auction) => {
                if (filter === 'won') return auction.is_winner === true;
                if (filter === 'lost') return auction.is_winner === false;
                return true; // "all"
            });
    
            setFilteredAuctions(filtered);
        } else {
            setFilteredAuctions([]);
        }
    }, [filter, activeTab, profileData]);
    
    
    
    

    useEffect(() => {
        const accessToken = localStorage.getItem('access_token');
        if (accessToken) {
            fetch('http://localhost:8000/api/profile/', {
                method: 'GET',
                headers: {
                    Authorization: `Bearer ${accessToken}`,
                },
            })
                .then((response) => {
                    if (!response.ok) {
                        console.log(response);
                        throw new Error('Ошибка при загрузке профиля');
                    }
                    return response.json();
                })
                .then((data) => setProfileData(data))
                .catch((error) => setError(error.message));
        } else {
            setError('Пользователь не авторизован');
        }
    }, []);

    if (error) {
        return <div>Ошибка: {error}</div>;
    }

    if (!profileData) {
        return <div>Загрузка...</div>;
    }

    const renderContent = () => {
        switch (activeTab) {
            case 'Избранное':
            return (
                <div className="auctions-list">
                    {profileData.favorites?.length > 0 ? (
                        profileData.favorites.map((auction) => (
                            <div key={auction.id} className="auction-card">
                                <h4>{auction.auction_type}</h4>
                                <p><strong>Статус:</strong> {auction.status}</p>
                                <Link to={`/auctions/${auction.id}`}>
                                    <button>Перейти к аукциону</button>
                                </Link>
                                <button onClick={() => handleRemoveFromFavorites(auction.id)}>
                                    Удалить из избранного
                                </button>
                            </div>
                        ))
                    ) : (
                        <p>Нет избранных аукционов</p>
                    )}
                </div>
            );
        case 'Мои аукционы':
            return (
                <div className="auctions-list">
                    {profileData.auctions?.map((auction) => (
                        <div key={auction.id} className="auction-card">
                            <h4>{auction.auction_type}</h4>
                            <p><strong>Статус:</strong> {auction.status}</p>
                            <p><strong>Начало:</strong> {new Date(auction.start_time).toLocaleString()}</p>
                            <p><strong>Окончание:</strong> {new Date(auction.end_time).toLocaleString()}</p>
                            <Link to={`/auctions/${auction.id}`}>
                                <button>Перейти к аукциону</button>
                            </Link>
                        </div>
                    ))}
                </div>
            );
                case 'Участвовал':
            return (
                <div>
                    {/* Фильтрация */}
                    <div className="filter-section">
                        <label htmlFor="filter">Фильтровать по результату:</label>
                        <select
                            id="filter"
                            value={filter}
                            onChange={(e) => setFilter(e.target.value)}
                        >
                            <option value="all">Все</option>
                            <option value="won">Выиграл</option>
                            <option value="lost">Проиграл</option>
                        </select>
                    </div>

                    {/* Список аукционов */}
                    <div className="auctions-list">
                        {filteredAuctions?.length > 0 ? (
                            filteredAuctions.map((auction) => (
                                <div key={auction.id} className="auction-item">
                                    <p><strong>Тип:</strong> {auction.auction_type}</p>
                                    <p><strong>Статус:</strong> {auction.status}</p>
                                    <p><strong>Результат:</strong> {auction.is_winner ? 'Выиграл' : 'Проиграл'}</p>
                                    <Link to={`/auctions/${auction.id}`}>
                                        <button>Перейти к аукциону</button>
                                    </Link>
                                </div>
                            ))
                        ) : (
                            <p>Нет аукционов, соответствующих фильтру "{filter === 'won' ? 'Выиграл' : 'Проиграл'}".</p>
                        )}
                    </div>
                </div>
            );
        case 'История ставок':
            return (
                <div>
                    {profileData.bids_history?.map((bid) => (
                        <div key={bid.id} className="bid-card">
                            <p><strong>Аукцион:</strong> {bid.auction__auction_type}</p>
                            <p><strong>Ставка:</strong> {bid.amount}</p>
                            <p><strong>Дата:</strong> {new Date(bid.timestamp).toLocaleString()}</p>
                        </div>
                    ))}
                </div>
            );
                
            default:
                return <p>Выберите вкладку</p>;
        }
    };

    return (
        <div className="profile-container">
            <h2>Профиль пользователя</h2>
            <div className="profile-header">
            {profileData.profile_picture ? (
    <img
        src={profileData.profile_picture}
        alt="Фото профиля"
        className="profile-picture"
    />
) : (
    <div className="profile-placeholder">Нет фото</div>
)}

                <div>
                    <p><strong>Псевдоним:</strong> {profileData.username}</p>
                    <p><strong>Электронная почта:</strong> {profileData.email}</p>
                    <p><strong>Имя:</strong> {profileData.first_name}</p>
                    <p><strong>Фамилия:</strong> {profileData.last_name}</p>
                    <p><strong>Телефон:</strong> {profileData.phone_number || 'Нет данных'}</p>
                </div>
            </div>
    
            <div>
                <strong>Рейтинг:</strong> {profileData.rating || 0}
                <StarRatingInput initialRating={profileData.rating || 0} readOnly={true} />
            </div>
    
            <Link to="/profile/edit">
                <button>Редактировать профиль</button>
            </Link>
    
            <div className="tabs">
    {tabs.map((tab) => (
        <button
            key={tab}
            className={activeTab === tab ? 'active-tab' : ''}
            onClick={() => handleTabChange(tab)} // Используем новый обработчик
        >
            {tab}
        </button>
    ))}
</div>

            {renderContent()}
        </div>
    );    
};

export default Profile;
