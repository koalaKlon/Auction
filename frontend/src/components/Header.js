import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from './AuthContext'; // Импортируем хук для аутентификации
import '../styles/Header.css';
import AuctionTimer from './AuctionTimer';

const Header = () => {
  const navigate = useNavigate();
  const { isAuthenticated, user, logout, changeRole } = useAuth(); // Получаем пользователя и его роль

  return (
    <header className="header">
      <div className="header-content">
        <h1 className="header-title">Аукционы</h1>
        <AuctionTimer />
      </div>
      <nav className="nav-links">
        <Link to="/" className="nav-link">Главная</Link>
        <Link to="/profile" className="nav-link">Профиль</Link>
      </nav>
      <div className={`header-buttons ${isAuthenticated ? 'is-authenticated' : 'is-guest'}`}>
        {isAuthenticated ? (
          <div className="auth-buttons">
            <button onClick={logout}>Выход</button>
            {/* Условие для кнопки "Создать аукцион", доступна только для роли "user" */}
            {user && user.role === 'seller' && (
              <button onClick={() => navigate('/create-auction')}>Создать аукцион</button>
            )}
            {/* Условные кнопки в зависимости от роли */}
            {user && user.role === 'user' && (
              <button onClick={changeRole}>Стать продавцом</button>
            )}
            {user && user.role === 'seller' && (
              <button onClick={changeRole}>Стать покупателем</button>
            )}
            {user && user.username === 'admin' && (
              <button onClick={async () => { navigate('/stats');
              }}>Статистика</button>
            )}

          </div>
        ) : (
          <div className="guest-buttons">
            <button onClick={() => navigate('/login')}>Авторизация</button>
            <button onClick={() => navigate('/register')}>Регистрация</button>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;
