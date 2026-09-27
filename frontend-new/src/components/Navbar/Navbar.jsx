import { NavLink } from "react-router-dom";
import "./Navbar.css";

function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar-container">

        <NavLink to="/" className="navbar-logo">
          🛒 DropCart
        </NavLink>

        <div className="navbar-links">
          <NavLink to="/" className="nav-link">
            Home
          </NavLink>

          <NavLink to="/products" className="nav-link">
            Products
          </NavLink>

          <NavLink to="/cart" className="nav-link">
            Cart
          </NavLink>

          <NavLink to="/orders" className="nav-link">
            Orders
          </NavLink>
        </div>

      </div>
    </nav>
  );
}

export default Navbar;