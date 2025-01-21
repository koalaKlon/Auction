import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import styles from '../styles/CreateAuction.module.css';

const CreateAuction = () => {
  const navigate = useNavigate();
  const [auctionType, setAuctionType] = useState('single');
  const [categories, setCategories] = useState([]);
  const [newProducts, setNewProducts] = useState([ 
    { name: '', description: '', starting_price: '', category: '', image: null }
  ]);
  const [formData, setFormData] = useState({ start_time: '', end_time: '', banner_image: null });

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/categories/');
        setCategories(response.data);
      } catch (err) {
        console.error('Error fetching categories:', err);
      }
    };

    fetchCategories();
  }, []);

  const handleAuctionTypeChange = (e) => {
    setAuctionType(e.target.value);
    if (e.target.value === 'single') {
      setNewProducts([{ name: '', description: '', starting_price: '', category: '', image: null }]);
    } else {
      setNewProducts([{ name: '', description: '', starting_price: '', category: '', image: null }]); // Keep at least one product form for "multiple"
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    setFormData((prevData) => ({
      ...prevData, banner_image: file,
    }));
  };

  const handleNewProductChange = (index, e) => {
    const { name, value, files } = e.target;
    const updatedProducts = [...newProducts];
    updatedProducts[index][name] = name === 'image' ? files[0] : value;
    setNewProducts(updatedProducts);
  };

  const handleAddProduct = () => {
    setNewProducts([...newProducts, { name: '', description: '', starting_price: '', category: '', image: null }]);
  };

  const handleCreateAuction = async (e) => {
    e.preventDefault();

    try {
        const auctionData = new FormData();
        Object.keys(formData).forEach((key) => {
            if (formData[key]) auctionData.append(key, formData[key]);
        });
        auctionData.append('auction_type', auctionType);

        if (formData.banner_image) {
            auctionData.append('banner_image', formData.banner_image);
        }

        if (auctionType === 'single') {
            const productData = new FormData();
            Object.keys(newProducts[0]).forEach((key) => {
                if (newProducts[0][key]) productData.append(key, newProducts[0][key]);
            });
            if (newProducts[0].image) {
                productData.append('image', newProducts[0].image);
            }

            const productResponse = await axios.post('http://localhost:8000/api/create-product/', productData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                    Authorization: `Bearer ${localStorage.getItem('access_token')}`,
                },
            });

            auctionData.append('product', productResponse.data.id);
        } else {
            newProducts.forEach((product, index) => {
                Object.keys(product).forEach((key) => {
                    if (product[key]) auctionData.append(`new_products[${index}][${key}]`, product[key]);
                });
                if (product.image) {
                    auctionData.append(`new_products[${index}][image]`, product.image);
                }
            });
        }

        const response = await axios.post('http://localhost:8000/api/create-auction/', auctionData, {
            headers: {
                'Content-Type': 'multipart/form-data',
                Authorization: `Bearer ${localStorage.getItem('access_token')}`,
            },
        });

        alert('Auction created successfully!');
        navigate(`/auctions/${response.data.auction_id}`);
    } catch (err) {
        console.error('Error creating auction:', err);
        alert('Failed to create auction.');
    }
};

  return (
    <form onSubmit={handleCreateAuction} encType="multipart/form-data" className={styles.form}>
      <div className={styles.field}>
        <label>Тип аукциона:</label>
        <select value={auctionType} onChange={handleAuctionTypeChange} className={styles.select}>
          <option value="single">Одиночный</option>
          <option value="multiple">Множественный</option>
        </select>
      </div>

      <div className={styles.field}>
        <label>Дата начала:</label>
        <input
          type="datetime-local"
          name="start_time"
          value={formData.start_time}
          onChange={handleInputChange}
          required
          className={styles.input}
        />
      </div>

      <div className={styles.field}>
        <label>Дата окончания:</label>
        <input
          type="datetime-local"
          name="end_time"
          value={formData.end_time}
          onChange={handleInputChange}
          required
          className={styles.input}
        />
      </div>

      <div className={styles.field}>
        <label>Баннер для аукциона:</label>
        <input type="file" name="banner_image" onChange={handleImageChange} className={styles.input} />
      </div>

      <div className={styles.products}>
        <h3>Товары для аукциона</h3>
        {newProducts.map((product, index) => (
          <div key={index} className={styles.product}>
            <input
              type="text"
              name="name"
              placeholder="Название"
              value={product.name}
              onChange={(e) => handleNewProductChange(index, e)}
              required
              className={styles.input}
            />
            <textarea
              name="description"
              placeholder="Описание"
              value={product.description}
              onChange={(e) => handleNewProductChange(index, e)}
              className={styles.textarea}
            />
            <input
              type="number"
              name="starting_price"
              placeholder="Начальная цена"
              value={product.starting_price}
              onChange={(e) => handleNewProductChange(index, e)}
              required
              className={styles.input}
            />
            <select
              name="category"
              value={product.category}
              onChange={(e) => handleNewProductChange(index, e)}
              required
              className={styles.select}
            >
              <option value="">Выберите категорию</option>
              {categories.map((cat) => (
                <option key={cat.id} value={cat.id}>
                  {cat.name}
                </option>
              ))}
            </select>
            <div className={styles.imageField}>
              <label>Изображение:</label>
              <input
                type="file"
                name="image"
                onChange={(e) => handleNewProductChange(index, e)}
                className={styles.input}
              />
            </div>
          </div>
        ))}
        {auctionType === 'multiple' && (
          <button type="button" onClick={handleAddProduct} className={styles.addProductButton}>
            Добавить товар
          </button>
        )}
      </div>
        
      <button type="submit" className={styles.button}>Создать аукцион</button>
    </form>
  );
};

export default CreateAuction;
