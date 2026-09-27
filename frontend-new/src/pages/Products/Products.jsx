import { useEffect, useState } from "react";

import api from "../../services/api";
import ProductCard from "../../components/ProductCard/ProductCard";

import "./Products.css";

function Products() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      const response = await api.get("/products/");
      setProducts(response.data);
    } catch (error) {
      console.error(error);
      setError("Unable to load products.");
    } finally {
      setLoading(false);
    }
  };

  const handleAddToCart = async (product) => {
    try {
      setMessage("");

      await api.post("/carts/1/items", {
        product_id: product.id,
        quantity: 1,
      });

      setMessage(`${product.name} added to cart.`);
    } catch (error) {
      console.error(error);

      const detail = error.response?.data?.detail;

      setMessage(detail || "Unable to add product to cart.");
    }
  };

  if (loading) {
    return (
      <div className="products-message">
        Loading products...
      </div>
    );
  }

  if (error) {
    return (
      <div className="products-message error">
        {error}
      </div>
    );
  }

  return (
    <main className="products-page">

      <section className="products-header">
        <div>
          <p className="products-label">DROP CART STORE</p>

          <h1>Our Products</h1>

          <p>
            Browse our available products and add your favorites
            to your shopping cart.
          </p>
        </div>
      </section>

      {message && (
        <div className="cart-message">
          {message}
        </div>
      )}

      {products.length === 0 ? (
        <div className="products-message">
          No products available.
        </div>
      ) : (
        <section className="products-grid">
          {products.map((product) => (
            <ProductCard
              key={product.id}
              product={product}
              onAddToCart={handleAddToCart}
            />
          ))}
        </section>
      )}

    </main>
  );
}

export default Products;