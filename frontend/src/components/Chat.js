import React, { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import '../styles/Chat.css'
const Chat = ({ currentUser, winner, seller }) => {
    const { id } = useParams(); // Auction ID из URL
    const [messages, setMessages] = useState([]);
    const [message, setMessage] = useState('');
    const socketRef = useRef(null); // Хранение WebSocket
    const accessToken = localStorage.getItem('access_token');

    // Проверка прав доступа
    const isAuthorized = currentUser?.id === seller?.id || currentUser?.username === winner || currentUser?.username === 'admin';
    console.log(winner);
    console.log(winner)
    useEffect(() => {
        if (!isAuthorized) return;

        // Загрузка старых сообщений из базы данных
        const fetchMessages = async () => {
            try {
                const response = await fetch(`http://localhost:8000/api/chats/${id}/`, {
                    headers: { Authorization: `Bearer ${accessToken}` },
                });
                if (response.ok) {
                    const data = await response.json();
                    setMessages(data); // Предполагается, что данные возвращаются в виде массива
                } else {
                    console.error('Failed to fetch messages');
                }
            } catch (error) {
                console.error('Error fetching messages:', error);
            }
        };

        fetchMessages();
    }, [id, isAuthorized]);

    useEffect(() => {
        if (!isAuthorized) return;

        // Создание WebSocket-соединения
        socketRef.current = new WebSocket(`ws://localhost:8000/ws/auction/${id}/chat/`);

        socketRef.current.onmessage = (event) => {
            const data = JSON.parse(event.data);
            setMessages((prevMessages) => [
                ...prevMessages,
                { sender_name: data.sender_name, message: data.message },
            ]);
        };

        socketRef.current.onopen = () => {
            console.log("WebSocket connection established");
        };

        socketRef.current.onerror = (error) => {
            console.error("WebSocket Error: ", error);
        };

        return () => {
            // Закрытие соединения при размонтировании
            if (socketRef.current) socketRef.current.close();
        };
    }, [id, isAuthorized]);

    const sendMessage = () => {
        if (!message.trim() || !socketRef.current) return;

        socketRef.current.send(JSON.stringify({
            message,
            sender: currentUser.username, // Используйте текущего пользователя
        }));

        setMessage(''); // Очистка поля сообщения
    };

    if (!isAuthorized) {
        return <div>У вас нет доступа к этому чату.</div>;
    }

    return (
        <div className="chat-container">
            <div className="messages">
                {messages.map((msg, index) => (
                    <div key={index} className="message">
                        <strong>{msg.sender_name}: </strong>{msg.message}
                    </div>
                ))}
            </div>

            <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Введите сообщение"
            />
            <button onClick={sendMessage}>Отправить</button>
        </div>
    );
};

export default Chat;
