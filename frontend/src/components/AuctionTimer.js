import React, { useState, useEffect } from 'react';

const AuctionTimer = () => {
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    // Interval to update time every second
    const timeInterval = setInterval(() => {
      setTime(new Date());
    }, 1000);

    // Interval for making requests every 5 seconds
    const requestInterval = setInterval(() => {
      fetch('http://localhost:8000/api/auction/status/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
    }, 10000);

    // Clean up intervals on component unmount
    return () => {
      clearInterval(timeInterval);
      clearInterval(requestInterval);
    };
  }, []);

  return (
    <div className="auction-timer">
      <div>
        Текущее время: {time.toLocaleTimeString()} {/* Display current time */}
      </div>
    </div>
  );
};

export default AuctionTimer;
