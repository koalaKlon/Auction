import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Header from './components/Header'; // Подключаем Header
import AuctionList from './components/AuctionList';
import Register from './components/Register';
import Login from './components/Login';
import Profile from './components/Profile';
import Stats from './components/Stats';
import EditProfile from './components/EditProfile';
import CreateAuction from './components/CreateAuction';
import AuctionDetail from './components/AuctionDetail';
import UserProfile from './components/UserProfile';
import EditAuction from './components/EditAuction';
import EditProduct from './components/EditProduct';
import { AuthProvider } from './components/AuthContext'; // Импорт AuthProvider
import './styles/global.css'; // Общие стили

const App = () => {
  return (
    <AuthProvider> {/* Оборачиваем приложение в AuthProvider */}
      <Router>
        <Header />
        <main className="app-content">
          <Routes>
            <Route path="/" element={<AuctionList />} />
            <Route path="/register" element={<Register />} />
            <Route path="/login" element={<Login />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/profile/edit" element={<EditProfile />} />
            <Route path="/create-auction" element={<CreateAuction />} />
            <Route path="/auctions/:id" element={<AuctionDetail />} />
            <Route path="/profile/:userId" element={<UserProfile />} />
            <Route path="/auction/:id/update" element={<EditAuction />} />
            <Route path="/product/:id/update" element={<EditProduct />} />
            <Route path="/stats" element={<Stats />} />
          </Routes>
        </main>
      </Router>
    </AuthProvider>
  );
};

export default App;
