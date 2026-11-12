import { Link } from "react-router-dom";
import { FaMobileAlt } from "react-icons/fa";

function MobileCard({ mobile }) {
  const imageUrl = mobile.images?.[0]?.image_url;

  return (
    <div className="card mobile-card h-100">

      {imageUrl ? (
        <img
          src={imageUrl}
          className="card-img-top mobile-image"
          alt={`${mobile.brand} ${mobile.model}`}
        />
      ) : (
        <div className="mobile-placeholder">
          <FaMobileAlt size={60} />
        </div>
      )}

      <div className="card-body">

        <span className="badge bg-light text-primary mb-2">
          {mobile.condition}
        </span>

        <h5 className="card-title">
          {mobile.brand} {mobile.model}
        </h5>

        <h4 className="mobile-price">
          ₹{Number(mobile.price).toLocaleString("en-IN")}
        </h4>

        <Link
          to={`/mobiles/${mobile.id}`}
          className="btn btn-outline-primary w-100 mt-2"
        >
          View Details
        </Link>

      </div>
    </div>
  );
}

export default MobileCard;