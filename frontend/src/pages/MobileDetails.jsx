
import { useEffect, useState } from "react";
import { useNavigate, useParams, Link } from "react-router-dom";
import {
  FaPhone,
  FaWhatsapp,
  FaPaperPlane,
  FaArrowLeft,
} from "react-icons/fa";

import api from "../services/api";
import { useAuth } from "../context/AuthContext";

function MobileDetails() {
  const { mobile_id } = useParams();
  const navigate = useNavigate();

  const { user, isAuthenticated, loading: authLoading } = useAuth();

  const [mobile, setMobile] = useState(null);
  const [selectedImage, setSelectedImage] = useState(0);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [message, setMessage] = useState("");
  const [requestLoading, setRequestLoading] = useState(false);
  const [requestSuccess, setRequestSuccess] = useState("");
  const [requestError, setRequestError] = useState("");

  // Load mobile details
  useEffect(() => {
    const fetchMobileDetails = async () => {
      try {
        setLoading(true);
        setError("");

        const response = await api.get(
          `/api/mobiles/${mobile_id}`
        );

        setMobile(response.data);

      } catch (err) {
        console.error("Failed to load mobile:", err);

        setError(
          err.response?.data?.detail ||
          "Unable to load mobile details."
        );
      } finally {
        setLoading(false);
      }
    };

    fetchMobileDetails();
  }, [mobile_id]);

  // Send purchase request
  const handlePurchaseRequest = async (event) => {
    event.preventDefault();

    if (!isAuthenticated) {
      navigate("/login");
      return;
    }

    try {
      setRequestLoading(true);
      setRequestError("");
      setRequestSuccess("");

      await api.post(
        `/api/purchase-requests/${mobile_id}`,
        {
          message: message.trim() || null,
        }
      );

      setRequestSuccess(
        "Your purchase request has been sent successfully!"
      );

      setMessage("");

    } catch (err) {
      console.error("Purchase request failed:", err);

      setRequestError(
        err.response?.data?.detail ||
        "Unable to send purchase request."
      );

    } finally {
      setRequestLoading(false);
    }
  };

  if (loading || authLoading) {
    return (
      <div className="container text-center py-5">
        <div className="spinner-border text-primary"></div>
        <p className="mt-3">Loading mobile details...</p>
      </div>
    );
  }

  if (error || !mobile) {
    return (
      <div className="container text-center py-5">
        <h3>Mobile not found</h3>

        <p className="text-danger">
          {error || "This mobile listing is unavailable."}
        </p>

        <Link to="/" className="btn btn-primary">
          Back to Home
        </Link>
      </div>
    );
  }

  const isSeller =
    isAuthenticated && user?.id === mobile.seller_id;

  const imageUrl = mobile.images?.[selectedImage]?.image_url;

  const phoneNumber = mobile.seller?.phone_number || "";
  const whatsappNumber = phoneNumber.replace(/\D/g, "");

  const canContactSeller =
    mobile.status === "available" && !isSeller;

  return (
    <div className="container py-4">

      {/* Back button */}
      <Link to="/" className="btn btn-outline-secondary mb-4">
        <FaArrowLeft className="me-2" />
        Back to Mobiles
      </Link>

      <div className="row g-4">

        {/* Product images */}
        <div className="col-lg-6">

          <div className="details-image-container">
            {imageUrl ? (
              <img
                src={imageUrl}
                alt={`${mobile.brand} ${mobile.model}`}
                className="details-main-image"
              />
            ) : (
              <div className="mobile-placeholder details-placeholder">
                No Image Available
              </div>
            )}
          </div>

          {/* Image thumbnails */}
          {mobile.images?.length > 1 && (
            <div className="d-flex gap-3 mt-3 flex-wrap">

              {mobile.images.map((image, index) => (
                <button
                  key={image.id}
                  type="button"
                  className={`thumbnail-button ${
                    selectedImage === index ? "active" : ""
                  }`}
                  onClick={() => setSelectedImage(index)}
                >
                  <img
                    src={image.image_url}
                    alt={`Mobile image ${index + 1}`}
                  />
                </button>
              ))}

            </div>
          )}

        </div>

        {/* Product information */}
        <div className="col-lg-6">

          <span className="badge bg-primary mb-3">
            {mobile.condition}
          </span>

          <h1 className="details-title">
            {mobile.brand} {mobile.model}
          </h1>

          <h2 className="details-price mt-3">
            ₹{Number(mobile.price).toLocaleString("en-IN")}
          </h2>

          <p className="mt-3">
            <strong>Availability:</strong>{" "}
            <span
              className={
                mobile.status === "available"
                  ? "text-success"
                  : "text-danger"
              }
            >
              {mobile.status}
            </span>
          </p>

          <hr />

          <h5>Product Description</h5>

          <p className="text-muted">
            {mobile.description || "No description provided."}
          </p>

          <hr />

          {/* Seller information */}
          <h5>Seller Information</h5>

          <div className="seller-information mt-3">

            <p>
              <strong>Name:</strong>{" "}
              {mobile.seller?.full_name}
            </p>

            <p>
              <strong>Phone:</strong>{" "}
              {phoneNumber || "Not available"}
            </p>

            {canContactSeller && phoneNumber && (
              <div className="d-flex gap-2 flex-wrap">

                <a
                  href={`tel:${phoneNumber}`}
                  className="btn btn-outline-primary"
                >
                  <FaPhone className="me-2" />
                  Call Seller
                </a>

                <a
                  href={`https://wa.me/${whatsappNumber}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn btn-success"
                >
                  <FaWhatsapp className="me-2" />
                  WhatsApp
                </a>

              </div>
            )}

          </div>

          <hr />

          {/* Purchase request form */}
          {isSeller ? (
            <div className="alert alert-info">
              This is your own mobile listing.
            </div>
          ) : mobile.status !== "available" ? (
            <div className="alert alert-secondary">
              This mobile is no longer available.
            </div>
          ) : (
            <div className="purchase-request-box">

              <h5>Interested in buying this mobile?</h5>

              <p className="text-muted">
                Send a purchase enquiry to the seller.
              </p>

              {requestSuccess && (
                <div className="alert alert-success">
                  {requestSuccess}
                </div>
              )}

              {requestError && (
                <div className="alert alert-danger">
                  {requestError}
                </div>
              )}

              <form onSubmit={handlePurchaseRequest}>

                <textarea
                  className="form-control mb-3"
                  rows="4"
                  placeholder="Hi, I am interested in buying this mobile..."
                  value={message}
                  onChange={(event) => setMessage(event.target.value)}
                  maxLength={1000}
                />

                <button
                  type="submit"
                  className="btn btn-primary w-100"
                  disabled={requestLoading}
                >
                  <FaPaperPlane className="me-2" />

                  {requestLoading
                    ? "Sending Request..."
                    : isAuthenticated
                      ? "Send Purchase Request"
                      : "Login to Send Request"}
                </button>

              </form>

            </div>
          )}

        </div>

      </div>

    </div>
  );
}

export default MobileDetails;
