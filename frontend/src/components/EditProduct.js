import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useParams, useNavigate } from 'react-router-dom';
import '../styles/EditProduct.css';

const EditProduct = () => {
  const { id } = useParams(); // Получаем ID продукта из URL
  const navigate = useNavigate();
  const [product, setProduct] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    axios.get(`http://localhost:8000/api/product/${id}/`)
      .then(response => {
        setProduct(response.data);
      })
      .catch(() => {
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
        formData.append(key, product[key][0]); // Файл изображения
      } else if (product[key] !== null && product[key] !== undefined) {
        formData.append(key, product[key]); // Остальные поля
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

  const handleDelete = () => {
    if (window.confirm("Вы уверены, что хотите удалить этот продукт? Если на аукционе больше нет товаров, аукцион также будет удален.")) {
      axios.delete(`http://localhost:8000/api/product/${id}/delete/`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
      .then(response => {
        const remainingProducts = response.data.remaining_products; // Получаем количество оставшихся товаров
        console.log(remainingProducts);
        console.log(remainingProducts);
        console.log(remainingProducts);
        console.log(remainingProducts);
        console.log(remainingProducts);
        
        if (remainingProducts === 0) {
          // Если товаров больше нет, удаляем аукцион
          axios.delete(`http://localhost:8000/api/auction/${product.auctions}/delete/`, {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          })
          .then(() => {
            // Перенаправляем на главную страницу
            navigate(`/`);
          })
          .catch(() => {
            setError('Ошибка при удалении аукциона');
          });
        } else {
          // Если товары остались, просто перенаправляем на страницу аукциона
          navigate(`/auctions/${product.auctions}`);
        }
      })
      .catch(() => {
        setError('Ошибка при удалении продукта');
      });
    }
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
      <button type="button" onClick={handleDelete} className="delete-btn">Удалить продукт</button>
    </form>
  );
};

export default EditProduct;
