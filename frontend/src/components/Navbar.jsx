
import { Link } from "react-router-dom";
import { FaMobileAlt } from "react-icons/fa";

import { useAuth } from "../context/AuthContext";

function Navbar() {
  const { user, isAuthenticated, logout } = useAuth();

  const handleLogout = () => {
    logout();
    window.location.href = "/";
  };

  return (
    <nav className="navbar navbar-expand-lg bg-white shadow-sm sticky-top">
      <div className="container py-2">

        <Link className="navbar-brand selfie-logo" to="/">
          <FaMobileAlt className="me-2" />
          Selfie
        </Link>

        <button
          className="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarContent"
        >
          <span className="navbar-toggler-icon"></span>
        </button>

        <div className="collapse navbar-collapse" id="navbarContent">

          <div className="navbar-nav ms-auto align-items-lg-center gap-lg-3">

            <Link className="nav-link" to="/">
              Home
            </Link>

            {isAuthenticated ? (
              <>
                <span className="nav-link">
                  Hi, {user.full_name}
                </span>

                <Link className="nav-link" to="/sell">
                  Sell Mobile
                </Link>

                <Link to="/my-listings" className="nav-link">
                    My Listings
                </Link>
                <Link to="/buyer-requests" className="nav-link">
                    My Purchase Requests
                </Link>
                <Link to="/seller-requests" className="nav-link">
                    Seller Requests
                </Link>
                <Link to="/dashboard" className="nav-link">
                    Dashboard
                </Link>
                <button
                  className="btn btn-outline-danger rounded-pill px-4"
                  onClick={handleLogout}
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link className="nav-link" to="/login">
                  Login
                </Link>

                <Link className="nav-link" to="/register">
                  Register
                </Link>

                <Link
                  className="btn btn-primary rounded-pill px-4"
                  to="/login"
                >
                  Sell Your Mobile
                </Link>
              </>
            )}

          </div>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
