
import { Routes, Route } from "react-router-dom";

import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import MobileDetails from "./pages/MobileDetails";
import SellMobile from "./pages/SellMobile";

import ProtectedRoute from "./components/ProtectedRoute";
import { AuthProvider } from "./context/AuthContext";
import MyListings from "./pages/MyListings";
import EditMobile from "./pages/EditMobile";
import BuyerRequests from "./pages/BuyerRequests";
import SellerRequests from "./pages/SellerRequests";
import Dashboard from "./pages/Dashboard";

function App() {
  return (
    <AuthProvider>
      <Navbar />

      <Routes>
        {/* Home */}
        <Route path="/" element={<Home />} />

        {/* Authentication */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* Mobile Details */}
        <Route
          path="/mobiles/:mobile_id"
          element={<MobileDetails />}
        />

        {/* Sell Mobile - Login Required */}
        <Route
          path="/sell"
          element={
            <ProtectedRoute>
              <SellMobile />
            </ProtectedRoute>
          }
        />

        {/* Page Not Found */}
        <Route
          path="*"
          element={
            <div className="container text-center py-5">
              <h2>Page not found</h2>
            </div>
          }
        />
        <Route
          path="/my-listings"
          element={
            <ProtectedRoute>
              <MyListings />
            </ProtectedRoute>
          }
        />
        <Route
          path="/edit-mobile/:mobile_id"
          element={
            <ProtectedRoute>
              <EditMobile />
            </ProtectedRoute>
          }
        />
        <Route
          path="/buyer-requests"
          element={
            <ProtectedRoute>
              <BuyerRequests />
            </ProtectedRoute>
          }
        />
        <Route
          path="/seller-requests"
          element={
            <ProtectedRoute>
              <SellerRequests />
            </ProtectedRoute>
          }
        />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
      </Routes>
    </AuthProvider>
  );
}

export default App;
