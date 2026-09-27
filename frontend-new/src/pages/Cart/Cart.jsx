import { useEffect, useState } from "react";

import api from "../../services/api";

import "./Cart.css";

function Cart() {
  const [cart, setCart] = useState(null);
  const [products, setProducts] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const userId = 1;

  useEffect(() => {
    fetchCart();
  }, []);

  const fetchCart = async () => {
    try {
      setLoading(true);
      setError("");

      const [cartResponse, productsResponse] = await Promise.all([
        api.get(`/carts/${userId}`),
        api.get("/products/"),
      ]);

      setCart(cartResponse.data);
      setProducts(productsResponse.data);

    } catch (error) {
      console.error(error);
      setError("Unable to load your cart.");
    } finally {
      setLoading(false);
    }
  };

  const getProduct = (productId) => {
    return products.find(
      (product) => product.id === productId
    );
  };

  const updateQuantity = async (itemId, quantity) => {
    if (quantity < 1) {
      return;
    }

    try {
      await api.patch(
        `/carts/${userId}/items/${itemId}`,
        {
          quantity,
        }
      );

      fetchCart();

    } catch (error) {
      console.error(error);

      alert(
        error.response?.data?.detail ||
        "Unable to update cart."
      );
    }
  };

  const removeItem = async (itemId) => {
    try {
      await api.delete(
        `/carts/${userId}/items/${itemId}`
      );

      fetchCart();

    } catch (error) {
      console.error(error);

      alert(
        error.response?.data?.detail ||
        "Unable to remove item."
      );
    }
  };

  const checkout = async () => {
    try {
      const response = await api.post(
        `/orders/checkout/${userId}`
      );

      alert(
        `Order #${response.data.id} created successfully.`
      );

      fetchCart();

    } catch (error) {
      console.error(error);

      alert(
        error.response?.data?.detail ||
        "Checkout failed."
      );
    }
  };

  const calculateTotal = () => {
    if (!cart) {
      return 0;
    }

    return cart.items.reduce((total, item) => {
      const product = getProduct(item.product_id);

      if (!product) {
        return total;
      }

      return total + Number(product.price) * item.quantity;
    }, 0);
  };

  if (loading) {
    return (
      <div className="cart-message">
        Loading cart...
      </div>
    );
  }

  if (error) {
    return (
      <div className="cart-message error">
        {error}
      </div>
    );
  }

  if (!cart || cart.items.length === 0) {
    return (
      <main className="cart-page">

        <div className="empty-cart">

          <div className="empty-cart-icon">
            🛒
          </div>

          <h1>Your Cart is Empty</h1>

          <p>
            Add some products to your cart and they will
            appear here.
          </p>

        </div>

      </main>
    );
  }

  const total = calculateTotal();

  return (
    <main className="cart-page">

      {/* Header */}

      <div className="cart-header">

        <p className="cart-label">
          SHOPPING CART
        </p>

        <h1>
          Your Cart
        </h1>

        <p>
          Review your items before placing your order.
        </p>

      </div>


      {/* Cart Content */}

      <div className="cart-content">

        <section className="cart-items">

          {cart.items.map((item) => {

            const product = getProduct(item.product_id);

            if (!product) {
              return null;
            }

            const itemTotal =
              Number(product.price) * item.quantity;

            return (
              <div
                className="cart-item"
                key={item.id}
              >

                {/* Product */}

                <div className="cart-product">

                  <div className="cart-product-icon">
                    🛍️
                  </div>

                  <div>

                    <h3>
                      {product.name}
                    </h3>

                    <p>
                      {product.description ||
                        "No description available."}
                    </p>

                    <span>
                      Rs.{" "}
                      {Number(
                        product.price
                      ).toLocaleString()}
                    </span>

                  </div>

                </div>


                {/* Quantity */}

                <div className="quantity-controls">

                  <button
                    onClick={() =>
                      updateQuantity(
                        item.id,
                        item.quantity - 1
                      )
                    }
                    disabled={item.quantity <= 1}
                  >
                    −
                  </button>

                  <span>
                    {item.quantity}
                  </span>

                  <button
                    onClick={() =>
                      updateQuantity(
                        item.id,
                        item.quantity + 1
                      )
                    }
                    disabled={
                      item.quantity >= product.stock
                    }
                  >
                    +
                  </button>

                </div>


                {/* Item Total */}

                <div className="cart-item-total">

                  <strong>
                    Rs.{" "}
                    {itemTotal.toLocaleString()}
                  </strong>

                  <button
                    className="remove-button"
                    onClick={() =>
                      removeItem(item.id)
                    }
                  >
                    Remove
                  </button>

                </div>

              </div>
            );
          })}

        </section>


        {/* Summary */}

        <aside className="cart-summary">

          <p className="summary-label">
            ORDER SUMMARY
          </p>

          <h2>
            Your Order
          </h2>

          <div className="summary-row">

            <span>
              Items
            </span>

            <span>
              {cart.items.reduce(
                (total, item) =>
                  total + item.quantity,
                0
              )}
            </span>

          </div>

          <div className="summary-row">

            <span>
              Products
            </span>

            <span>
              {cart.items.length}
            </span>

          </div>

          <div className="summary-divider" />

          <div className="summary-total">

            <span>
              Total
            </span>

            <strong>
              Rs. {total.toLocaleString()}
            </strong>

          </div>

          <button
            className="checkout-button"
            onClick={checkout}
          >
            Proceed to Checkout
          </button>

        </aside>

      </div>

    </main>
  );
}

export default Cart;