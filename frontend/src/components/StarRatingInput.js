import React, { useEffect, useState } from 'react';
import '../styles/StarRatingInput.css';

const StarRatingInput = ({ onSubmit, onDelete, initialRating, readOnly = false }) => {
    const [hoveredRating, setHoveredRating] = useState(null);
    const [selectedRating, setSelectedRating] = useState(initialRating || null);

    useEffect(() => {
        setSelectedRating(initialRating || null);
    }, [initialRating]);

    const handleMouseEnter = (value) => {
        if (!readOnly) setHoveredRating(value);
    };

    const handleMouseLeave = () => {
        if (!readOnly) setHoveredRating(null);
    };

    const handleClick = (value) => {
        if (!readOnly) {
            setSelectedRating(value);
            onSubmit(value);
        }
    };

    const renderStars = () => {
        const stars = [];
        for (let i = 1; i <= 10; i++) {
            stars.push(
                <div
                    key={i}
                    className={`star ${
                        hoveredRating !== null
                            ? i <= hoveredRating
                                ? 'filled'
                                : ''
                            : i <= (selectedRating || 0)
                            ? 'filled'
                            : ''
                    }`}
                    onMouseEnter={() => handleMouseEnter(i)}
                    onMouseLeave={handleMouseLeave}
                    onClick={() => handleClick(i)}
                    style={{ cursor: readOnly ? 'default' : 'pointer' }} // Убираем курсор для режима readOnly
                >
                    ★
                </div>
            );
        }
        return stars;
    };

    return (
        <div>
            <div className="starRating">{renderStars()}</div>
            {!readOnly && selectedRating !== null}
        </div>
    );
};

export default StarRatingInput;
