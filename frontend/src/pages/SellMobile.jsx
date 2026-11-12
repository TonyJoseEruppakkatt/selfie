
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { FaCloudUploadAlt, FaTimes, FaMobileAlt } from "react-icons/fa";

import api from "../services/api";

function SellMobile() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    brand: "",
    model: "",
    price: "",
    condition: "",
    description: "",
  });

  const [images, setImages] = useState([]);
  const [previews, setPreviews] = useState([]);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const allowedTypes = [
    "image/jpeg",
    "image/png",
    "image/webp",
  ];

  const maxImageSize = 5 * 1024 * 1024;
  const maxImages = 5;

  // Handle text fields
  const handleChange = (event) => {
    setFormData({
      ...formData,
      [event.target.name]: event.target.value,
    });
  };

  // Handle image selection
  const handleImageChange = (event) => {
    const selectedFiles = Array.from(event.target.files);

    setError("");
    setSuccess("");

    if (images.length + selectedFiles.length > maxImages) {
      setError("You can upload a maximum of 5 images.");
      event.target.value = "";
      return;
    }

    for (const file of selectedFiles) {
      if (!allowedTypes.includes(file.type)) {
        setError("Only JPEG, PNG and WEBP images are allowed.");
        event.target.value = "";
        return;
      }

      if (file.size > maxImageSize) {
        setError("Each image must be smaller than 5 MB.");
        event.target.value = "";
        return;
      }
    }

    const newImages = [...images, ...selectedFiles];

    setImages(newImages);

    const newPreviews = selectedFiles.map((file) =>
      URL.createObjectURL(file)
    );

    setPreviews((previous) => [
      ...previous,
      ...newPreviews,
    ]);

    event.target.value = "";
  };

  // Remove selected image
  const removeImage = (index) => {
    URL.revokeObjectURL(previews[index]);

    setImages((previous) =>
      previous.filter((_, i) => i !== index)
    );

    setPreviews((previous) =>
      previous.filter((_, i) => i !== index)
    );
  };

  // Submit mobile listing
  const handleSubmit = async (event) => {
    event.preventDefault();

    setError("");
    setSuccess("");

    if (images.length === 0) {
      setError("Please upload at least one mobile image.");
      return;
    }

    if (images.length > maxImages) {
      setError("You can upload a maximum of 5 images.");
      return;
    }

    try {
      setLoading(true);

      const data = new FormData();

      data.append("brand", formData.brand);
      data.append("model", formData.model);
      data.append("price", formData.price);
      data.append("condition", formData.condition);
      data.append("description", formData.description);

      images.forEach((image) => {
        data.append("images", image);
      });

      const response = await api.post(
        "/api/mobiles",
        data
      );

      setSuccess("Your mobile listing was created successfully!");

      // Release temporary preview URLs
      previews.forEach((url) => URL.revokeObjectURL(url));

      // Open the newly created mobile details page
      navigate(`/mobiles/${response.data.id}`);

    } catch (err) {
      console.error("Mobile listing failed:", err);

      setError(
        err.response?.data?.detail ||
        "Unable to create mobile listing. Please try again."
      );

    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container py-5">

      <div className="sell-page-header text-center mb-5">
        <FaMobileAlt className="sell-icon" />

        <h1>Sell Your Mobile</h1>

        <p className="text-muted">
          List your smartphone and connect with interested buyers.
        </p>
      </div>

      <div className="sell-form-card mx-auto">

        {error && (
          <div className="alert alert-danger">
            {error}
          </div>
        )}

        {success && (
          <div className="alert alert-success">
            {success}
          </div>
        )}

        <form onSubmit={handleSubmit}>

          {/* Brand */}
          <div className="mb-3">
            <label className="form-label">
              Mobile Brand *
            </label>

            <select
              className="form-select"
              name="brand"
              value={formData.brand}
              onChange={handleChange}
              required
            >
              <option value="">Select brand</option>
              <option value="Apple">Apple</option>
              <option value="Samsung">Samsung</option>
              <option value="OnePlus">OnePlus</option>
              <option value="Xiaomi">Xiaomi</option>
              <option value="Redmi">Redmi</option>
              <option value="Realme">Realme</option>
              <option value="Vivo">Vivo</option>
              <option value="Oppo">Oppo</option>
              <option value="Motorola">Motorola</option>
              <option value="Google">Google</option>
              <option value="Other">Other</option>
            </select>
          </div>

          {/* Model */}
          <div className="mb-3">
            <label className="form-label">
              Mobile Model *
            </label>

            <input
              type="text"
              className="form-control"
              name="model"
              placeholder="Example: iPhone 15 Pro"
              value={formData.model}
              onChange={handleChange}
              maxLength={100}
              required
            />
          </div>

          {/* Price */}
          <div className="mb-3">
            <label className="form-label">
              Expected Selling Price (₹) *
            </label>

            <input
              type="number"
              className="form-control"
              name="price"
              placeholder="Example: 35000"
              value={formData.price}
              onChange={handleChange}
              min="0.01"
              step="0.01"
              required
            />
          </div>

          {/* Condition */}
          <div className="mb-3">
            <label className="form-label">
              Mobile Condition *
            </label>

            <select
              className="form-select"
              name="condition"
              value={formData.condition}
              onChange={handleChange}
              required
            >
              <option value="">Select condition</option>
              <option value="Like New">Like New</option>
              <option value="Excellent">Excellent</option>
              <option value="Good">Good</option>
              <option value="Fair">Fair</option>
            </select>

            <small className="text-muted">
              Choose the condition that best describes your mobile.
            </small>
          </div>

          {/* Description */}
          <div className="mb-4">
            <label className="form-label">
              Description
            </label>

            <textarea
              className="form-control"
              name="description"
              rows="4"
              placeholder="Describe your mobile, its age, accessories, battery condition, etc."
              value={formData.description}
              onChange={handleChange}
              maxLength={2000}
            />
          </div>

          {/* Image Upload */}
          <div className="mb-4">

            <label className="form-label">
              Upload Mobile Images *
            </label>

            <div className="image-upload-area">

              <FaCloudUploadAlt size={40} />

              <p className="mt-2 mb-1">
                Click below to select mobile images
              </p>

              <small className="text-muted">
                JPEG, PNG or WEBP. Maximum 5 images, 5 MB each.
              </small>

              <input
                type="file"
                className="form-control mt-3"
                accept="image/jpeg,image/png,image/webp"
                multiple
                onChange={handleImageChange}
                disabled={images.length >= maxImages}
              />

            </div>

            {/* Image previews */}
            {previews.length > 0 && (
              <div className="row g-3 mt-2">

                {previews.map((preview, index) => (
                  <div
                    className="col-6 col-md-4 col-lg-3"
                    key={preview}
                  >
                    <div className="preview-card">

                      <img
                        src={preview}
                        alt={`Preview ${index + 1}`}
                      />

                      <button
                        type="button"
                        className="remove-image-btn"
                        onClick={() => removeImage(index)}
                        aria-label={`Remove image ${index + 1}`}
                      >
                        <FaTimes />
                      </button>

                    </div>
                  </div>
                ))}

              </div>
            )}

            <small className="text-muted d-block mt-2">
              {images.length} of 5 images selected
            </small>

          </div>

          {/* Submit */}
          <button
            type="submit"
            className="btn btn-primary w-100 sell-submit-btn"
            disabled={loading}
          >
            {loading
              ? "Publishing Your Listing..."
              : "Publish Mobile Listing"}
          </button>

        </form>

      </div>

    </div>
  );
}

export default SellMobile;
