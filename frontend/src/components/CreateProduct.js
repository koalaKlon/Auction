import React, { useState } from 'react';
import { createProduct } from '../api/api';
import '../styles/CreateProduct.css';

const CreateProduct = () => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    category: '',
    starting_price: '',
  });
  const [image, setImage] = useState(null);

  const handleInputChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleImageChange = (e) => {
    setImage(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const productData = new FormData();
    Object.keys(formData).forEach((key) => {
      productData.append(key, formData[key]);
    });
    if (image) {
      productData.append('image', image);
    }

    try {
      const response = await createProduct(productData);
      alert('Product created successfully: ' + JSON.stringify(response.data));
    } catch (error) {
      
      console.error('Error creating product:', error);
      alert('Failed to create product: ' + error.message);
    }
  };

  return (
    <form onSubmit={handleSubmit} encType="multipart/form-data">
      <div>
        <label>
          Name:
          <input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleInputChange}
            required
          />
        </label>
      </div>
      <div>
        <label>
          Description:
          <textarea
            name="description"
            value={formData.description}
            onChange={handleInputChange}
          />
        </label>
      </div>
      <div>
        <label>
          Category:
          <input
            type="text"
            name="category"
            value={formData.category}
            onChange={handleInputChange}
            required
          />
        </label>
      </div>
      <div>
        <label>
          Starting Price:
          <input
            type="number"
            name="starting_price"
            value={formData.starting_price}
            onChange={handleInputChange}
            step="0.01"
          />
        </label>
      </div>
      <div>
        <label>
          Image:
          <input type="file" onChange={handleImageChange} />
        </label>
      </div>
      <button type="submit">Create Product</button>
    </form>
  );
};

export default CreateProduct;
