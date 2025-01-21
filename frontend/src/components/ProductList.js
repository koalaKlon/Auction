import React from 'react';
import ProductItem from './ProductItem';

const ProductList = ({ auctionType, products, product, isOwner, navigate, status }) => (
  <div>
    <h2>Товары на аукционе:</h2>
    {auctionType === "multiple" && products ? (
      <ul>
        {products.map((prod, index) => (
          <ProductItem key={index} product={prod} isOwner={isOwner} navigate={navigate} status={status} />
        ))}
      </ul>
    ) : auctionType === "single" && product ? (
      <ProductItem product={product} isOwner={isOwner} navigate={navigate} status={status} />
    ) : (
      <p>Нет товаров для аукциона</p>
    )}
  </div>
);

export default ProductList;
