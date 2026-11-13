
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import api from "../services/api";

function EditMobile() {
  const { mobile_id } = useParams();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const [form, setForm] = useState({
    brand: "",
    model: "",
    price: "",
    condition: "Good",
    description: "",
  });

  useEffect(() => {
    const fetchMobile = async () => {
      try {
        const response = await api.get(
          `/api/mobiles/${mobile_id}`
        );

        const mobile = response.data;

        setForm({
          brand: mobile.brand,
          model: mobile.model,
          price: mobile.price,
          condition: mobile.condition,
          description: mobile.description || "",
        });

      } catch (err) {
        console.error(err);
        setError(
          err.response?.data?.detail ||
          "Unable to load mobile details."
        );

      } finally {
        setLoading(false);
      }
    };

    fetchMobile();
  }, [mobile_id]);

  const handleChange = (event) => {
    setForm({
      ...form,
      [event.target.name]: event.target.value,
    });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    try {
      setSaving(true);
      setError("");

      const formData = new FormData();

      formData.append("brand", form.brand);
      formData.append("model", form.model);
      formData.append("price", form.price);
      formData.append("condition", form.condition);
      formData.append("description", form.description);

      await api.put(
        `/api/mobiles/${mobile_id}`,
        formData
      );

      alert("Mobile listing updated successfully!");

      navigate("/my-listings");

    } catch (err) {
      console.error("Update failed:", err);

      setError(
        err.response?.data?.detail ||
        "Unable to update mobile listing."
      );

    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="text-center py-5">
        <div className="spinner-border text-primary"></div>
        <p className="mt-3">Loading mobile details...</p>
      </div>
    );
  }

  if (error && !form.brand) {
    return (
      <div className="container py-5">
        <div className="alert alert-danger">{error}</div>
      </div>
    );
  }

  return (
    <div className="container py-5">
      <div className="row justify-content-center">
        <div className="col-md-8 col-lg-7">

          <div className="card shadow-sm">
            <div className="card-body p-4">

              <h2 className="mb-4">Edit Mobile Listing</h2>

              {error && (
                <div className="alert alert-danger">
                  {error}
                </div>
              )}

              <form onSubmit={handleSubmit}>

                <div className="mb-3">
                  <label className="form-label">Brand</label>
                  <input
                    type="text"
                    name="brand"
                    className="form-control"
                    value={form.brand}
                    onChange={handleChange}
                    required
                  />
                </div>

                <div className="mb-3">
                  <label className="form-label">Model</label>
                  <input
                    type="text"
                    name="model"
                    className="form-control"
                    value={form.model}
                    onChange={handleChange}
                    required
                  />
                </div>

                <div className="mb-3">
                  <label className="form-label">Price (₹)</label>
                  <input
                    type="number"
                    name="price"
                    className="form-control"
                    min="1"
                    step="0.01"
                    value={form.price}
                    onChange={handleChange}
                    required
                  />
                </div>

                <div className="mb-3">
                  <label className="form-label">Condition</label>
                  <select
                    name="condition"
                    className="form-select"
                    value={form.condition}
                    onChange={handleChange}
                    required
                  >
                    <option value="Like New">Like New</option>
                    <option value="Excellent">Excellent</option>
                    <option value="Good">Good</option>
                    <option value="Fair">Fair</option>
                  </select>
                </div>

                <div className="mb-3">
                  <label className="form-label">Description</label>
                  <textarea
                    name="description"
                    className="form-control"
                    rows="4"
                    value={form.description}
                    onChange={handleChange}
                  />
                </div>

                <div className="d-flex gap-2">

                  <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={saving}
                  >
                    {saving ? "Saving..." : "Update Listing"}
                  </button>

                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={() => navigate("/my-listings")}
                  >
                    Cancel
                  </button>

                </div>

              </form>

            </div>
          </div>

        </div>
      </div>
    </div>
  );
}

export default EditMobile;
