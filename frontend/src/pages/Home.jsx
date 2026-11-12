import { useEffect, useState } from "react";
import { FaSearch } from "react-icons/fa";

import api from "../services/api";
import MobileCard from "../components/MobileCard";

function Home() {
  const [mobiles, setMobiles] = useState([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchMobiles = async (searchValue = "") => {
    try {
      setLoading(true);
      setError("");

      const response = await api.get("/api/mobiles", {
        params: {
          search: searchValue || undefined,
          page: 1,
          page_size: 20,
        },
      });

      setMobiles(response.data.items);

    } catch (err) {
      console.error("Failed to load mobiles:", err);
      setError("Unable to load mobile listings. Please try again.");

    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMobiles();
  }, []);

  const handleSearch = (event) => {
    event.preventDefault();
    fetchMobiles(search);
  };

  return (
    <div>

      {/* Hero Section */}
      <section className="hero-section">
        <div className="container text-center">

          <h1>
            Find Your Perfect <span>Smartphone</span>
          </h1>

          <p>
            Buy and sell pre-owned smartphones at great prices.
          </p>

          <form
            className="search-box mx-auto"
            onSubmit={handleSearch}
          >
            <input
              type="text"
              className="form-control"
              placeholder="Search iPhone, Samsung, OnePlus..."
              value={search}
              onChange={(event) => setSearch(event.target.value)}
            />

            <button className="btn btn-primary" type="submit">
              <FaSearch className="me-2" />
              Search
            </button>
          </form>

        </div>
      </section>

      {/* Mobile Listings */}
      <section className="container py-5">

        <div className="d-flex justify-content-between align-items-center mb-4">
          <div>
            <h2 className="section-title">Latest Mobiles</h2>
            <p className="text-muted">
              Explore available smartphones.
            </p>
          </div>
        </div>

        {loading && (
          <div className="text-center py-5">
            <div className="spinner-border text-primary"></div>
            <p className="mt-3">Loading mobiles...</p>
          </div>
        )}

        {error && (
          <div className="alert alert-danger">
            {error}
            <button
              className="btn btn-sm btn-outline-danger ms-3"
              onClick={() => fetchMobiles(search)}
            >
              Retry
            </button>
          </div>
        )}

        {!loading && !error && mobiles.length === 0 && (
          <div className="text-center py-5">
            <h4>No mobiles found</h4>
            <p className="text-muted">
              Try another search.
            </p>
          </div>
        )}

        <div className="row g-4">

          {mobiles.map((mobile) => (
            <div
              className="col-12 col-sm-6 col-lg-3"
              key={mobile.id}
            >
              <MobileCard mobile={mobile} />
            </div>
          ))}

        </div>

      </section>
    </div>
  );
}

export default Home;