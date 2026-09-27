import "./ProductCard.css";

function ProductCard({ product, onAddToCart }) {
  return (
    <div className="product-card">

      <div className="product-card-image">
        🛍️
      </div>

      <div className="product-card-content">

        <h3>{product.name}</h3>

        <p className="product-description">
          {product.description || "No description available."}
        </p>

        <div className="product-info">
          <span className="product-price">
            Rs. {Number(product.price).toLocaleString()}
          </span>

          <span className="product-stock">
            Stock: {product.stock}
          </span>
        </div>

        <button
          className="add-cart-button"
          onClick={() => onAddToCart(product)}
          disabled={product.stock <= 0}
        >
          {product.stock > 0 ? "Add to Cart" : "Out of Stock"}
        </button>

      </div>

    </div>
  );
}

export default ProductCard;