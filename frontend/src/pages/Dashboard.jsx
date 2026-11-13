
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import {
  FaMobileAlt,
  FaCheckCircle,
  FaShoppingBag,
  FaInbox,
  FaClock,
  FaPlus,
  FaList,
} from "react-icons/fa";

import { getDashboardSummary } from "../services/dashboardService";

function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchSummary = async () => {
    try {
      setLoading(true);
      setError("");

      const data = await getDashboardSummary();
      setSummary(data);

    } catch (err) {
      console.error("Dashboard loading failed:", err);

      setError(
        err.response?.data?.detail ||
        "Unable to load dashboard statistics."
      );

    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSummary();
  }, []);

  const statistics = [
    {
      title: "Total Listings",
      value: summary?.total_listings ?? 0,
      icon: <FaMobileAlt />,
      color: "primary",
    },
    {
      title: "Available Mobiles",
      value: summary?.available_listings ?? 0,
      icon: <FaCheckCircle />,
      color: "success",
    },
    {
      title: "Sold Mobiles",
      value: summary?.sold_listings ?? 0,
      icon: <FaShoppingBag />,
      color: "secondary",
    },
    {
      title: "Incoming Requests",
      value: summary?.incoming_requests ?? 0,
      icon: <FaInbox />,
      color: "info",
    },
    {
      title: "Pending Requests",
      value: summary?.pending_requests ?? 0,
      icon: <FaClock />,
      color: "warning",
    },
    {
      title: "My Purchase Requests",
      value: summary?.my_purchase_requests ?? 0,
      icon: <FaList />,
      color: "dark",
    },
  ];

  return (
    <div className="container py-5">

      <div className="d-flex justify-content-between align-items-center flex-wrap gap-3 mb-4">
        <div>
          <h2>My Dashboard</h2>
          <p className="text-muted mb-0">
            Welcome to your Selfie marketplace dashboard.
          </p>
        </div>

        <button
          className="btn btn-outline-primary"
          onClick={fetchSummary}
          disabled={loading}
        >
          {loading ? "Loading..." : "Refresh"}
        </button>
      </div>

      {error && (
        <div className="alert alert-danger">
          {error}
          <button
            className="btn btn-sm btn-outline-danger ms-3"
            onClick={fetchSummary}
          >
            Retry
          </button>
        </div>
      )}

      {loading && !summary && (
        <div className="text-center py-5">
          <div className="spinner-border text-primary"></div>
          <p className="mt-3">Loading dashboard...</p>
        </div>
      )}

      {summary && !error && (
        <>
          <div className="row g-4 mb-5">

            {statistics.map((item) => (
              <div
                className="col-12 col-sm-6 col-lg-4"
                key={item.title}
              >
                <div className="card shadow-sm h-100">
                  <div className="card-body d-flex justify-content-between align-items-center">

                    <div>
                      <p className="text-muted mb-2">
                        {item.title}
                      </p>

                      <h2 className="mb-0">
                        {item.value}
                      </h2>
                    </div>

                    <div
                      className={`text-${item.color}`}
                      style={{ fontSize: "35px" }}
                    >
                      {item.icon}
                    </div>

                  </div>
                </div>
              </div>
            ))}

          </div>

          <h4 className="mb-3">Quick Actions</h4>

          <div className="row g-3">

            <div className="col-12 col-md-4">
              <Link
                to="/sell"
                className="btn btn-primary w-100 py-3"
              >
                <FaPlus className="me-2" />
                Sell a Mobile
              </Link>
            </div>

            <div className="col-12 col-md-4">
              <Link
                to="/my-listings"
                className="btn btn-outline-primary w-100 py-3"
              >
                <FaMobileAlt className="me-2" />
                My Listings
              </Link>
            </div>

            <div className="col-12 col-md-4">
              <Link
                to="/seller-requests"
                className="btn btn-outline-primary w-100 py-3"
              >
                <FaInbox className="me-2" />
                Seller Requests
              </Link>
            </div>

            <div className="col-12 col-md-4">
              <Link
                to="/buyer-requests"
                className="btn btn-outline-primary w-100 py-3"
              >
                <FaShoppingBag className="me-2" />
                My Purchase Requests
              </Link>
            </div>

          </div>
        </>
      )}

    </div>
  );
}

export default Dashboard;
