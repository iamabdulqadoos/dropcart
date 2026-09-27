import { useEffect, useState } from "react";

import api from "../../services/api";
import OrderCard from "../../components/OrderCard/OrderCard";

import "./Orders.css";

function Orders() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const userId = 1;

  useEffect(() => {
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    try {
      const response = await api.get(
        `/orders/user/${userId}`
      );

      setOrders(response.data);
    } catch (error) {
      console.error(error);
      setError("Unable to load your orders.");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="orders-message">
        Loading orders...
      </div>
    );
  }

  if (error) {
    return (
      <div className="orders-message error">
        {error}
      </div>
    );
  }

  return (
    <main className="orders-page">

      <section className="orders-header">
        <p className="orders-label">
          ORDER HISTORY
        </p>

        <h1>Your Orders</h1>

        <p>
          Track your recent DropCart orders and their
          processing status.
        </p>
      </section>

      {orders.length === 0 ? (
        <div className="orders-empty">
          <div>📦</div>

          <h2>No Orders Yet</h2>

          <p>
            Your completed checkouts will appear here.
          </p>
        </div>
      ) : (
        <section className="orders-list">

          {orders.map((order) => (
            <OrderCard
              key={order.id}
              order={order}
            />
          ))}

        </section>
      )}

    </main>
  );
}

export default Orders;