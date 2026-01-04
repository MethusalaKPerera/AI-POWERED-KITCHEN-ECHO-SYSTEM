import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

import Header from "../Components/Header.jsx";

// Main site pages
import Home from "../Pages/Home.jsx";
import CookingAssistant from "../Pages/CookingAssistant/CookingAssistant.jsx";
import MealPlanner from "../Pages/CookingAssistant/MealPlanner.jsx";
import SmartShopping from "../Pages/SmartShopping.jsx";
import NutritionalGuidance from "../Pages/NutritionalGuidance";

// Auth
import Login from "../Pages/Auth/Login.jsx";
import Register from "../Pages/Auth/Register.jsx";

// Food Expiry Dashboard Pages
import DashboardHome from "../Pages/FoodExpiry/DashboardHome.jsx";
import Predict from "../Pages/FoodExpiry/Predict.jsx";
import AddFood from "../Pages/FoodExpiry/AddFood.jsx";
import Inventory from "../Pages/FoodExpiry/Inventory.jsx";
import FeedbackTrainer from "../Pages/FoodExpiry/FeedbackTrainer.jsx";
import Analytics from "../Pages/FoodExpiry/Analytics.jsx";
import UserProfile from "../Pages/FoodExpiry/UserProfile.jsx";
import SystemLogs from "../Pages/FoodExpiry/SystemLogs.jsx";

function AppRouter() {
  return (
    <Router>
      <Header />

      <Routes>
        {/* Main site */}
        <Route path="/" element={<Home />} />
        <Route path="/cooking-assistant" element={<CookingAssistant />} />
        <Route path="/meal-planner" element={<MealPlanner />} />
        <Route path="/smart-shopping/*" element={<SmartShopping />} />
        <Route path="/nutritional-guidance" element={<NutritionalGuidance />} />

        {/* Auth */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* ----------------------------
            Food Expiry Dashboard
           ---------------------------- */}

        {/* Dashboard landing */}
        <Route path="/food-expiry" element={<DashboardHome />} />

        <Route path="/food-expiry/predict" element={<Predict />} />
        <Route path="/food-expiry/add" element={<AddFood />} />
        <Route path="/food-expiry/inventory" element={<Inventory />} />
        <Route path="/food-expiry/feedback" element={<FeedbackTrainer />} />
        <Route path="/food-expiry/analytics" element={<Analytics />} />
        <Route path="/food-expiry/profile" element={<UserProfile />} />
        <Route path="/food-expiry/logs" element={<SystemLogs />} />
      </Routes>
    </Router>
  );
}

export default AppRouter;
