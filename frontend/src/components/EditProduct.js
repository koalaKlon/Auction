import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useParams, useNavigate } from 'react-router-dom';
import '../styles/EditProduct.css';

const EditProduct = () => {
  const { id } = useParams(); // Get product ID from URL
  const navigate = useNavigate();
  const [product, setProduct] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    axios.get(`http://localhost:8000/api/product/${id}/`)
      .then(response => {
        setProduct(response.data);
      })
      .catch(err => {
        setError('Ошибка загрузки данных');
      });
  }, [id]);

  const handleChange = (e) => {
    const { name, value, files } = e.target;
    if (files) {
      setProduct({ ...product, [name]: files });
    } else {
      setProduct({ ...product, [name]: value });
    }
  };
  
  const token = localStorage.getItem("access_token");
  const handleSubmit = (e) => {
    e.preventDefault();
  
    const formData = new FormData();
    for (const key in product) {
      if (key === 'image' && product[key]) {
        formData.append(key, product[key][0]); // Attach file
      } else if (product[key] !== null && product[key] !== undefined) {
        formData.append(key, product[key]); // Attach other fields
      }
    }
  
    axios.put(`http://localhost:8000/api/product/${id}/update/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        Authorization: `Bearer ${token}`,
      },
    })
      .then(() => {
        navigate(`/auctions/${product.auctions}`);
      })
      .catch(err => {
        const serverError = err.response?.data?.error || 'Ошибка при сохранении данных';
        setError(serverError);
      });
  };
  

  if (!product) return <div className="loading">Загрузка...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <form onSubmit={handleSubmit} className="edit-product-form">
      <div className="form-group">
        <label htmlFor="image" className="label">Текущее изображение</label>
        <input
          type="file"
          name="image"
          accept="image/*"
          onChange={handleChange}
          className="file-input"
        />
      </div>

      <div className="form-group">
        <label htmlFor="name" className="label">Название продукта</label>
        <input
          type="text"
          name="name"
          value={product.name}
          onChange={handleChange}
          className="text-input"
        />
      </div>

      <div className="form-group">
        <label htmlFor="description" className="label">Описание</label>
        <textarea
          name="description"
          value={product.description}
          onChange={handleChange}
          className="textarea-input"
        />
      </div>

      <div className="form-group">
        <label htmlFor="starting_price" className="label">Цена</label>
        <input
          type="number"
          name="starting_price"
          value={product.starting_price || ''}
          onChange={handleChange}
          className="number-input"
        />
      </div>

      <button type="submit" className="submit-btn">Сохранить изменения</button>
    </form>
  );
};

export default EditProduct;
