import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import {
  getDrop,
  getDropStock,
  reserveDrop,
} from "../../services/dropService";

import "./Drop.css";

function Drop() {
  const { dropId } = useParams();

  const [drop, setDrop] = useState(null);
  const [stock, setStock] = useState(null);

  const [loading, setLoading] = useState(true);
  const [stockLoading, setStockLoading] = useState(true);

  const [reserving, setReserving] = useState(false);

  const [reservation, setReservation] = useState(null);

  const [countdown, setCountdown] = useState(null);
  const [reservationTime, setReservationTime] = useState(null);

  const [error, setError] = useState("");

  // Temporary user ID.
  // We will replace this with proper authentication later.
  const userId = 1;

  // --------------------------------------------------
  // Fetch Drop
  // --------------------------------------------------

  useEffect(() => {
    const loadDrop = async () => {
      try {
        setLoading(true);
        setError("");

        const data = await getDrop(dropId);

        setDrop(data);
      } catch (error) {
        console.error("Drop error:", error);

        setError(
          error.response?.data?.detail ||
            "Unable to load this drop."
        );
      } finally {
        setLoading(false);
      }
    };

    loadDrop();
  }, [dropId]);

  // --------------------------------------------------
  // Fetch Stock
  // --------------------------------------------------

  const loadStock = async () => {
    try {
      setStockLoading(true);

      const data = await getDropStock(dropId);

      setStock(data);
    } catch (error) {
      console.error("Stock error:", error);
    } finally {
      setStockLoading(false);
    }
  };

  // --------------------------------------------------
  // Poll Stock Every 2 Seconds
  // --------------------------------------------------

  useEffect(() => {
    if (!drop) {
      return;
    }

    loadStock();

    const interval = setInterval(() => {
      loadStock();
    }, 2000);

    return () => {
      clearInterval(interval);
    };
  }, [dropId, drop]);

  // --------------------------------------------------
  // Drop Countdown
  // --------------------------------------------------

  useEffect(() => {
    if (!drop) {
      return;
    }

    const updateCountdown = () => {
      const now = Date.now();

      const startTime = new Date(
        drop.starts_at
      ).getTime();

      const endTime = new Date(
        drop.ends_at
      ).getTime();

      if (now < startTime) {
        setCountdown(startTime - now);
      } else if (now >= endTime) {
        setCountdown(0);
      } else {
        setCountdown(null);
      }
    };

    updateCountdown();

    const interval = setInterval(
      updateCountdown,
      1000
    );

    return () => {
      clearInterval(interval);
    };
  }, [drop]);

  // --------------------------------------------------
  // Reservation Countdown
  // --------------------------------------------------

  useEffect(() => {
    if (!reservation) {
      return;
    }

    const updateReservationTimer = () => {
      const now = Date.now();

      const expiresAt = new Date(
        reservation.expires_at
      ).getTime();

      const remaining = expiresAt - now;

      if (remaining <= 0) {
        setReservationTime(0);
      } else {
        setReservationTime(remaining);
      }
    };

    updateReservationTimer();

    const interval = setInterval(
      updateReservationTimer,
      1000
    );

    return () => {
      clearInterval(interval);
    };
  }, [reservation]);

  // --------------------------------------------------
  // Reserve Drop
  // --------------------------------------------------

  const handleReserve = async () => {
    try {
      setReserving(true);
      setError("");

      const data = await reserveDrop(
        dropId,
        userId
      );

      setReservation(data);

      await loadStock();
    } catch (error) {
      console.error("Reservation error:", error);

      setError(
        error.response?.data?.detail ||
          "Unable to reserve this item."
      );

      await loadStock();
    } finally {
      setReserving(false);
    }
  };

  // --------------------------------------------------
  // Format Time
  // --------------------------------------------------

  const formatTime = (milliseconds) => {
    if (
      milliseconds === null ||
      milliseconds === undefined
    ) {
      return "00:00:00";
    }

    const totalSeconds = Math.max(
      0,
      Math.floor(milliseconds / 1000)
    );

    const hours = Math.floor(
      totalSeconds / 3600
    );

    const minutes = Math.floor(
      (totalSeconds % 3600) / 60
    );

    const seconds = totalSeconds % 60;

    return [
      hours,
      minutes,
      seconds,
    ]
      .map((value) =>
        String(value).padStart(2, "0")
      )
      .join(":");
  };

  // --------------------------------------------------
  // Loading State
  // --------------------------------------------------

  if (loading) {
    return (
      <div className="drop-page">
        <div className="drop-state">
          <div className="drop-spinner"></div>

          <p>Loading drop...</p>
        </div>
      </div>
    );
  }

  // --------------------------------------------------
  // Error State
  // --------------------------------------------------

  if (error && !drop) {
    return (
      <div className="drop-page">
        <div className="drop-state drop-error-state">
          <div className="state-icon">!</div>

          <h2>Something went wrong</h2>

          <p>{error}</p>
        </div>
      </div>
    );
  }

  // --------------------------------------------------
  // Drop Not Found
  // --------------------------------------------------

  if (!drop) {
    return (
      <div className="drop-page">
        <div className="drop-state">
          <h2>Drop Not Found</h2>

          <p>
            The drop you're looking for does not
            exist.
          </p>
        </div>
      </div>
    );
  }

  // --------------------------------------------------
  // Drop Status
  // --------------------------------------------------

  const now = Date.now();

  const startTime = new Date(
    drop.starts_at
  ).getTime();

  const endTime = new Date(
    drop.ends_at
  ).getTime();

  const dropNotStarted = now < startTime;

  const dropEnded = now >= endTime;

  const availableStock =
    stock?.available ?? drop.quantity;

  const totalStock =
    stock?.total_stock ?? drop.quantity;

  const reservedStock =
    stock?.reserved ?? 0;

  const soldOut = availableStock <= 0;

  const reservationExpired =
    reservation &&
    reservationTime !== null &&
    reservationTime <= 0;

  const stockPercentage =
    totalStock > 0
      ? Math.max(
          0,
          Math.min(
            100,
            (availableStock / totalStock) * 100
          )
        )
      : 0;

  return (
    <div className="drop-page">

      <div className="drop-container">

        {/* Header */}

        <div className="drop-header">

          <span className="drop-badge">
            LIMITED DROP
          </span>

          <h1>Exclusive Drop</h1>

          <p>
            Limited quantity. Once it's gone,
            it's gone.
          </p>

        </div>

        {/* Main Card */}

        <div className="drop-card">

          {/* Product */}

          <div className="product-section">

            <span className="section-label">
              DROP PRODUCT
            </span>

            <h2>
              Product #{drop.product_id}
            </h2>

            <p className="product-description">
              Secure your item before the
              limited inventory runs out.
            </p>

            <div className="product-price">
              PKR 25,000
            </div>

          </div>

          <div className="drop-divider"></div>

          {/* Before Drop */}

          {dropNotStarted && (

            <div className="countdown-section">

              <span className="section-label">
                DROP STARTS IN
              </span>

              <div className="countdown">

                {formatTime(countdown)}

              </div>

              <p>
                Be ready when the drop goes live.
              </p>

            </div>

          )}

          {/* Live Drop */}

          {!dropNotStarted &&
            !dropEnded && (

              <div className="live-section">

                <div className="live-header">

                  <div className="live-indicator">

                    <span></span>

                    LIVE NOW

                  </div>

                  {soldOut && (
                    <span className="sold-out-badge">
                      SOLD OUT
                    </span>
                  )}

                </div>

                {/* Stock */}

                <div className="stock-section">

                  <div>

                    <span className="section-label">
                      AVAILABLE STOCK
                    </span>

                    {stockLoading ? (

                      <div className="stock-loading">
                        Updating...
                      </div>

                    ) : (

                      <div className="stock-number">

                        {availableStock}

                        <span>
                          {" "}
                          / {totalStock}
                        </span>

                      </div>

                    )}

                  </div>

                  <div className="reserved-info">

                    {reservedStock} reserved

                  </div>

                </div>

                {/* Stock Bar */}

                <div className="stock-bar">

                  <div
                    className="stock-progress"
                    style={{
                      width: `${stockPercentage}%`,
                    }}
                  ></div>

                </div>

              </div>

            )}

          {/* Ended */}

          {dropEnded && (

            <div className="ended-section">

              <div className="state-icon">
                —
              </div>

              <h3>
                Drop Ended
              </h3>

              <p>
                This drop is no longer accepting
                reservations.
              </p>

            </div>

          )}

          {/* Reservation Success */}

          {reservation &&
            !reservationExpired && (

              <div className="reservation-success">

                <div className="success-top">

                  <div className="success-icon">
                    ✓
                  </div>

                  <div>

                    <h3>
                      Reservation Successful
                    </h3>

                    <p>
                      Your item is reserved.
                    </p>

                  </div>

                </div>

                <div className="reservation-timer">

                  <span>
                    RESERVATION EXPIRES IN
                  </span>

                  <strong>
                    {formatTime(
                      reservationTime
                    )}
                  </strong>

                </div>

                <button
                  className="checkout-button"
                  type="button"
                  onClick={() => {
                    // Checkout will be connected
                    // in the next stage.
                  }}
                >
                  Proceed to Checkout
                </button>

              </div>

            )}

          {/* Reserve Button */}

          {!reservation &&
            !dropNotStarted &&
            !dropEnded && (

              <button
                className="reserve-button"
                type="button"
                disabled={
                  reserving || soldOut
                }
                onClick={handleReserve}
              >

                {reserving
                  ? "RESERVING..."
                  : soldOut
                  ? "SOLD OUT"
                  : "RESERVE NOW"}

              </button>

            )}

          {/* Reservation Expired */}

          {reservationExpired && (

            <div className="expired-section">

              <h3>
                Reservation Expired
              </h3>

              <p>
                Your 5-minute reservation hold
                has expired.
              </p>

              <button
                className="reserve-again-button"
                type="button"
                onClick={() => {
                  setReservation(null);
                  setReservationTime(null);
                }}
              >
                Reserve Again
              </button>

            </div>

          )}

          {/* Error */}

          {error && (

            <div className="inline-error">

              <span>!</span>

              {error}

            </div>

          )}

        </div>

        {/* Information */}

        <div className="drop-info">

          <div>
            <strong>5 min</strong>
            <span>Reservation hold</span>
          </div>

          <div>
            <strong>1 item</strong>
            <span>Per user</span>
          </div>

          <div>
            <strong>Live</strong>
            <span>Stock updates</span>
          </div>

        </div>

      </div>

    </div>
  );
}

export default Drop;