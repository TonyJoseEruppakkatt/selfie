
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { FaEye, FaShoppingBag } from "react-icons/fa";

import { getBuyerRequests } from "../services/mobileService";

function BuyerRequests() {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchRequests = async () => {
    try {
      setLoading(true);
      setError("");

      const data = await getBuyerRequests();
      setRequests(data);

    } catch (err) {
      console.error("Failed to load buyer requests:", err);

      setError(
        err.response?.data?.detail ||
        "Unable to load your purchase requests."
      );

    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRequests();
  }, []);

  const getStatusClass = (status) => {
    switch (status?.toLowerCase()) {
      case "pending":
        return "bg-warning text-dark";

      case "accepted":
        return "bg-success";

      case "rejected":
        return "bg-danger";

      default:
        return "bg-secondary";
    }
  };

  return (
    <div className="container py-5">

      <div className="mb-4">
        <h2>
          <FaShoppingBag className="me-2" />
          My Purchase Requests
        </h2>

        <p className="text-muted">
          Track the purchase requests you have submitted.
        </p>
      </div>

      {loading && (
        <div className="text-center py-5">
          <div className="spinner-border text-primary"></div>
          <p className="mt-3">Loading purchase requests...</p>
        </div>
      )}

      {error && (
        <div className="alert alert-danger">
          {error}

          <button
            className="btn btn-sm btn-outline-danger ms-3"
            onClick={fetchRequests}
          >
            Retry
          </button>
        </div>
      )}

      {!loading && !error && requests.length === 0 && (
        <div className="text-center py-5">
          <h4>No purchase requests yet</h4>

          <p className="text-muted">
            Explore available smartphones and contact sellers.
          </p>

          <Link to="/" className="btn btn-primary">
            Explore Mobiles
          </Link>
        </div>
      )}

      {!loading && !error && requests.length > 0 && (
        <div className="table-responsive">

          <table className="table table-bordered table-hover align-middle">

            <thead className="table-light">
              <tr>
                <th>Request ID</th>
                <th>Mobile ID</th>
                <th>Message</th>
                <th>Date</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>

            <tbody>
              {requests.map((request) => (
                <tr key={request.id}>

                  <td>#{request.id}</td>

                  <td>#{request.mobile_id}</td>

                  <td>
                    {request.message || "No message"}
                  </td>

                  <td>
                    {new Date(request.created_at).toLocaleDateString("en-IN")}
                  </td>

                  <td>
                    <span
                      className={`badge ${getStatusClass(request.status)}`}
                    >
                      {request.status}
                    </span>
                  </td>

                  <td>
                    <Link
                      to={`/mobiles/${request.mobile_id}`}
                      className="btn btn-sm btn-outline-primary"
                    >
                      <FaEye className="me-1" />
                      View Mobile
                    </Link>
                  </td>

                </tr>
              ))}
            </tbody>

          </table>

        </div>
      )}

    </div>
  );
}

export default BuyerRequests;
