
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { FaEdit, FaTrash, FaEye, FaPlus } from "react-icons/fa";

import {
  getMyListings,
  deleteMobile,
} from "../services/mobileService";

function MyListings() {
  const [mobiles, setMobiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [deletingId, setDeletingId] = useState(null);

  const fetchListings = async () => {
    try {
      setLoading(true);
      setError("");

      const data = await getMyListings();
      setMobiles(data.items);

    } catch (err) {
      console.error("Failed to fetch listings:", err);
      setError("Unable to load your listings.");

    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchListings();
  }, []);

  const handleDelete = async (mobileId) => {
    const confirmed = window.confirm(
      "Are you sure you want to delete this mobile listing?"
    );

    if (!confirmed) return;

    try {
      setDeletingId(mobileId);

      await deleteMobile(mobileId);

      setMobiles((previous) =>
        previous.filter((mobile) => mobile.id !== mobileId)
      );

    } catch (err) {
      console.error("Delete failed:", err);

      alert(
        err.response?.data?.detail ||
        "Unable to delete this listing."
      );

    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="container py-5">

      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2>My Listings</h2>
          <p className="text-muted">
            Manage the mobile phones you have listed.
          </p>
        </div>

        <Link to="/sell" className="btn btn-primary">
          <FaPlus className="me-2" />
          Sell Mobile
        </Link>
      </div>

      {loading && (
        <div className="text-center py-5">
          <div className="spinner-border text-primary"></div>
          <p className="mt-3">Loading your listings...</p>
        </div>
      )}

      {error && (
        <div className="alert alert-danger">
          {error}
          <button
            className="btn btn-sm btn-outline-danger ms-3"
            onClick={fetchListings}
          >
            Retry
          </button>
        </div>
      )}

      {!loading && !error && mobiles.length === 0 && (
        <div className="text-center py-5">
          <h4>You haven't listed any mobiles yet.</h4>
          <p className="text-muted">
            Start selling your old smartphone on Selfie.
          </p>

          <Link to="/sell" className="btn btn-primary">
            Sell Your First Mobile
          </Link>
        </div>
      )}

      {!loading && !error && mobiles.length > 0 && (
        <div className="row g-4">

          {mobiles.map((mobile) => (
            <div
              className="col-12 col-md-6 col-lg-4"
              key={mobile.id}
            >
              <div className="card h-100 shadow-sm">

                {mobile.images?.length > 0 ? (
                  <img
                    src={mobile.images[0].image_url}
                    className="card-img-top"
                    alt={`${mobile.brand} ${mobile.model}`}
                    style={{
                      height: "220px",
                      objectFit: "contain",
                      padding: "15px",
                    }}
                  />
                ) : (
                  <div
                    className="d-flex justify-content-center align-items-center bg-light"
                    style={{ height: "220px" }}
                  >
                    No Image
                  </div>
                )}

                <div className="card-body">

                  <span
                    className={`badge ${
                      mobile.status === "available"
                        ? "bg-success"
                        : "bg-secondary"
                    }`}
                  >
                    {mobile.status}
                  </span>

                  <h5 className="mt-3">
                    {mobile.brand} {mobile.model}
                  </h5>

                  <h4 className="text-primary">
                    ₹{Number(mobile.price).toLocaleString("en-IN")}
                  </h4>

                  <p className="text-muted mb-3">
                    Condition: {mobile.condition}
                  </p>

                  <div className="d-flex gap-2 flex-wrap">

                    <Link
                      to={`/mobiles/${mobile.id}`}
                      className="btn btn-outline-primary btn-sm"
                    >
                      <FaEye className="me-1" />
                      View
                    </Link>

                    {mobile.status === "available" && (
                      <>
                        <Link
                          to={`/edit-mobile/${mobile.id}`}
                          className="btn btn-outline-warning btn-sm"
                        >
                          <FaEdit className="me-1" />
                          Edit
                        </Link>

                        <button
                          className="btn btn-outline-danger btn-sm"
                          onClick={() => handleDelete(mobile.id)}
                          disabled={deletingId === mobile.id}
                        >
                          <FaTrash className="me-1" />
                          {deletingId === mobile.id
                            ? "Deleting..."
                            : "Delete"}
                        </button>
                      </>
                    )}

                  </div>

                </div>
              </div>
            </div>
          ))}

        </div>
      )}

    </div>
  );
}

export default MyListings;
