import React from 'react';

const ProductItem = ({ product, isOwner, navigate, status }) => (
  <li>
    <img src={product.image} style={{ width: '100%', maxWidth: '100%', height: 'auto' }}/>
    <h3>{product.name}</h3>
    <p><strong>Описание:</strong> {product.description}</p>
    <p><strong>Начальная цена:</strong> {product.starting_price}</p>
    {isOwner && status !== "active" && status !== "finished" && (
      <button onClick={() => navigate(`/product/${product.id}/update`)}>
        Редактировать товар
      </button>
    )}
  </li>
);

export default ProductItem;
