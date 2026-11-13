
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  FaCheck,
  FaTimes,
  FaEye,
  FaInbox,
} from "react-icons/fa";

import {
  getSellerRequests,
  updatePurchaseRequestStatus,
} from "../services/mobileService";

function SellerRequests() {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [updatingId, setUpdatingId] = useState(null);

  const fetchRequests = async () => {
    try {
      setLoading(true);
      setError("");

      const data = await getSellerRequests();
      setRequests(data);

    } catch (err) {
      console.error("Failed to load seller requests:", err);

      setError(
        err.response?.data?.detail ||
        "Unable to load purchase requests."
      );

    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRequests();
  }, []);

  const handleStatusUpdate = async (requestId, newStatus) => {
    const action = newStatus === "accepted" ? "accept" : "reject";

    const confirmed = window.confirm(
      `Are you sure you want to ${action} this purchase request?`
    );

    if (!confirmed) return;

    try {
      setUpdatingId(requestId);
      setError("");

      await updatePurchaseRequestStatus(requestId, newStatus);

      setRequests((previous) =>
        previous.map((request) =>
          request.id === requestId
            ? { ...request, status: newStatus }
            : request
        )
      );

    } catch (err) {
      console.error("Status update failed:", err);

      setError(
        err.response?.data?.detail ||
        "Unable to update purchase request."
      );

    } finally {
      setUpdatingId(null);
    }
  };

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
          <FaInbox className="me-2" />
          Seller Requests
        </h2>

        <p className="text-muted">
          Review and manage purchase requests from buyers.
        </p>
      </div>

      {error && (
        <div className="alert alert-danger">
          {error}
        </div>
      )}

      {loading && (
        <div className="text-center py-5">
          <div className="spinner-border text-primary"></div>
          <p className="mt-3">Loading incoming requests...</p>
        </div>
      )}

      {!loading && !error && requests.length === 0 && (
        <div className="text-center py-5">
          <h4>No purchase requests yet</h4>

          <p className="text-muted">
            Buyer requests for your mobile listings will appear here.
          </p>

          <Link to="/my-listings" className="btn btn-primary">
            View My Listings
          </Link>
        </div>
      )}

      {!loading && requests.length > 0 && (
        <div className="table-responsive">

          <table className="table table-bordered table-hover align-middle">

            <thead className="table-light">
              <tr>
                <th>Request ID</th>
                <th>Mobile ID</th>
                <th>Buyer ID</th>
                <th>Message</th>
                <th>Request Date</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>

            <tbody>
              {requests.map((request) => (
                <tr key={request.id}>

                  <td>#{request.id}</td>

                  <td>#{request.mobile_id}</td>

                  <td>#{request.buyer_id}</td>

                  <td>
                    {request.message || "No message"}
                  </td>

                  <td>
                    {new Date(
                      request.created_at
                    ).toLocaleDateString("en-IN")}
                  </td>

                  <td>
                    <span
                      className={`badge ${getStatusClass(request.status)}`}
                    >
                      {request.status}
                    </span>
                  </td>

                  <td>
                    <div className="d-flex gap-2 flex-wrap">

                      <Link
                        to={`/mobiles/${request.mobile_id}`}
                        className="btn btn-sm btn-outline-primary"
                      >
                        <FaEye />
                      </Link>

                      {request.status === "pending" && (
                        <>
                          <button
                            className="btn btn-sm btn-success"
                            onClick={() =>
                              handleStatusUpdate(
                                request.id,
                                "accepted"
                              )
                            }
                            disabled={updatingId === request.id}
                            title="Accept request"
                          >
                            <FaCheck />
                          </button>

                          <button
                            className="btn btn-sm btn-danger"
                            onClick={() =>
                              handleStatusUpdate(
                                request.id,
                                "rejected"
                              )
                            }
                            disabled={updatingId === request.id}
                            title="Reject request"
                          >
                            <FaTimes />
                          </button>
                        </>
                      )}

                      {updatingId === request.id && (
                        <span className="text-muted small">
                          Updating...
                        </span>
                      )}

                    </div>
                  </td>

                </tr>
              ))}
            </tbody>

          </table>

        </div>
      )}

      {!loading && (
        <div className="text-end mt-3">
          <button
            className="btn btn-outline-secondary"
            onClick={fetchRequests}
          >
            Refresh Requests
          </button>
        </div>
      )}

    </div>
  );
}

export default SellerRequests;
