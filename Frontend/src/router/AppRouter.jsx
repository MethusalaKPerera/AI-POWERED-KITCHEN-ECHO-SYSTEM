import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "../Pages/Home.jsx";
import CookingAssistant from "../Pages/CookingAssistant/CookingAssistant.jsx";import ExpiryPredictor from "../Pages/ExpiryPredictor.jsx";
import SmartShopping from "../Pages/SmartShopping.jsx";
import NutritionalGuidance from "../Pages/NutritionalGuidance";
import Header from "../Components/Header.jsx";

function AppRouter() {
  return (
    <Router>
      <Header />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/cooking-assistant" element={<CookingAssistant />} />
        <Route path="/expiry-predictor" element={<ExpiryPredictor />} />
        <Route path="/smart-shopping" element={<SmartShopping />} />
        <Route path="/nutritional-guidance" element={<NutritionalGuidance />} />
      </Routes>
    </Router>
  );
}

export default AppRouter;
