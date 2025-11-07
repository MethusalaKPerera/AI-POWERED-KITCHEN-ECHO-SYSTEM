import React from "react";
import { Link, useLocation } from "react-router-dom";
import "./Header.css";

function Header() {
  const location = useLocation();

  const isActive = (path) => (location.pathname === path ? "active" : "");

  return (
    <header className="header">
      <h1 className="logo">AI Kitchen Ecosystem</h1>
      <nav className="nav">
        <Link to="/" className={isActive("/")}>Home</Link>
        <Link to="/cooking-assistant" className={isActive("/cooking-assistant")}>Cooking Assistant</Link>
        <Link to="/nutritional-guidance" className={isActive("/nutritional-guidance")}>Nutritional Guidance</Link>
        <Link to="/expiry-predictor" className={isActive("/expiry-predictor")}>Expiry Predictor</Link>
        <Link to="/smart-shopping" className={isActive("/smart-shopping")}>Smart Shopping</Link>
      </nav>
    </header>
  );
}

export default Header;
