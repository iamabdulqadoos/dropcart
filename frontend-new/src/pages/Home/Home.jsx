import { Link } from "react-router-dom";

import "./Home.css";

function Home() {
  return (
    <main className="home-page">

      {/* Hero Section */}
      <section className="hero-section">

        <div className="hero-content">

          <p className="hero-label">
            SIMPLE • FAST • RELIABLE
          </p>

          <h1>
            Welcome to <span>DropCart</span>
          </h1>

          <p className="hero-description">
            A simple e-commerce platform for browsing products,
            managing your cart, and placing orders with ease.
          </p>

          <div className="hero-buttons">

            <Link
              to="/products"
              className="primary-button"
            >
              Browse Products
            </Link>

            <Link
              to="/orders"
              className="secondary-button"
            >
              View Orders
            </Link>

          </div>

        </div>

        <div className="hero-card">

          <div className="hero-icon">
            🛒
          </div>

          <h3>
            Your Shopping Cart
          </h3>

          <p>
            Add products, manage quantities,
            and checkout securely.
          </p>

          <div className="hero-card-line">
            <span>Products</span>
            <span>✓</span>
          </div>

          <div className="hero-card-line">
            <span>Cart Management</span>
            <span>✓</span>
          </div>

          <div className="hero-card-line">
            <span>Order Processing</span>
            <span>✓</span>
          </div>

        </div>

      </section>


      {/* Features Section */}
      <section className="features-section">

        <div className="section-heading">

          <p className="section-label">
            WHY DROPCART
          </p>

          <h2>
            Everything you need
          </h2>

          <p>
            Manage your shopping experience from one simple
            interface.
          </p>

        </div>


        <div className="features-grid">

          <div className="feature-card">

            <div className="feature-icon">
              📦
            </div>

            <h3>
              Browse Products
            </h3>

            <p>
              Explore available products and check their
              prices and stock.
            </p>

          </div>


          <div className="feature-card">

            <div className="feature-icon">
              🛒
            </div>

            <h3>
              Manage Your Cart
            </h3>

            <p>
              Add products, update quantities, and remove
              items whenever you need.
            </p>

          </div>


          <div className="feature-card">

            <div className="feature-icon">
              🚚
            </div>

            <h3>
              Track Orders
            </h3>

            <p>
              Place orders and monitor their processing
              status from your order history.
            </p>

          </div>

        </div>

      </section>


      {/* CTA Section */}
      <section className="cta-section">

        <div>

          <p className="section-label">
            READY TO SHOP?
          </p>

          <h2>
            Start exploring DropCart
          </h2>

          <p>
            Find products and add them to your cart.
          </p>

        </div>

        <Link
          to="/products"
          className="cta-button"
        >
          Explore Products →
        </Link>

      </section>

    </main>
  );
}

export default Home;