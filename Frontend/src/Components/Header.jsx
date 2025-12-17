import React from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import "./Header.css";

function Header() {
  const location = useLocation();
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem('user'));
  const isActive = (path) => (location.pathname === path ? "active" : "");

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/login');
    window.location.reload();
  };

  return (
    <header className="header">
      <h1 className="logo">AI Kitchen Ecosystem</h1>
      <nav className="nav items-center">
        <Link to="/" className={isActive("/")}>Home</Link>
        <Link to="/cooking-assistant" className={isActive("/cooking-assistant")}>Cooking Assistant</Link>
        <Link to="/nutritional-guidance" className={isActive("/nutritional-guidance")}>Nutritional Guidance</Link>
        <Link to="/expiry-predictor" className={isActive("/expiry-predictor")}>Expiry Predictor</Link>
        <Link to="/smart-shopping" className={isActive("/smart-shopping")}>Smart Shopping</Link>

        {user ? (
          <div className="flex items-center gap-4 ml-4">
            <span className="text-sm font-medium">Hello, {user.name}</span>
            <button
              onClick={handleLogout}
              className="bg-white text-emerald-700 px-4 py-1 rounded-md text-sm font-bold hover:bg-emerald-50 transition-colors"
            >
              Logout
            </button>
          </div>
        ) : (
          <div className="ml-4">
            <Link
              to="/login"
              className={`bg-white text-emerald-700 px-4 py-1.5 rounded-md text-sm font-bold hover:bg-emerald-50 transition-colors ${isActive("/login")}`}
            >
              Login
            </Link>
          </div>
        )}
      </nav>
    </header>
  );
}

export default Header;
