import "./OrderCard.css";

function OrderCard({ order }) {
  return (
    <div className="order-card">

      <div className="order-card-header">
        <div>
          <p className="order-label">ORDER</p>
          <h3>#{order.id}</h3>
        </div>

        <span className={`order-status ${order.status}`}>
          {order.status}
        </span>
      </div>

      <div className="order-card-body">
        <div>
          <span>Customer</span>
          <strong>User #{order.user_id}</strong>
        </div>

        <div>
          <span>Total</span>
          <strong>
            Rs. {Number(order.total_amount).toLocaleString()}
          </strong>
        </div>

        <div>
          <span>Items</span>
          <strong>{order.items.length}</strong>
        </div>
      </div>

    </div>
  );
}

export default OrderCard;