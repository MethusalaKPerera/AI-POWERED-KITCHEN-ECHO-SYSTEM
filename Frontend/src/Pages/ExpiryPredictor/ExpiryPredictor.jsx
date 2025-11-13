// src/components/FoodExpiryPersonalization.jsx
import React, { useState } from "react";
import { motion } from "framer-motion";

const FoodExpiryPredictor = () => {
  const [showForm, setShowForm] = useState(false);
  const [section, setSection] = useState("");

  const handleStart = () => {
    setShowForm(true);
    setSection("");
  };

  return (
    <div className="min-h-screen bg-[#F9FAFB] py-12 px-6 flex flex-col items-center">
      {/* HERO Section */}
      <motion.div
        className="hero-box"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-3xl font-bold text-[#1E293B] mb-4">
          Personalized Food Expiry Prediction 
        </h1>
        <p className="text-gray-600 leading-relaxed mb-6">
          We use AI to predict food expiry based on your habits. <br/>
          With personalization, you can extend freshness and reduce waste! <br />
          <span className="font-semibold text-[#16A34A]">
            What’s new? Personalization.
          </span>{" "}
          Your system adapts to <strong>your habits</strong> using Adaptive Expiry Drift (AED) and Smart Consumption Prioritization (SCP).
        </p>

        {/* Info Buttons Section */}
        <div className="flex justify-center gap-6 mb-8">
          <button
            onClick={() => setSection("scp")}
            className="btn primary"
          >
            Learn About SCP
          </button>
          <button
            onClick={() => setSection("personalization")}
            className="btn primary"
          >
            How Personalization Works
          </button>
          <button
            onClick={() => setSection("benefits")}
            className="btn secondary"
          >
            Benefits for You
          </button>
          <button
            onClick={handleStart}
            className="btn primary"
          >
            Start Personalizing
          </button>
        </div>

        {/* Dynamic Sections for Features */}
        <motion.div
          className="text-left text-gray-700 mt-4"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
        >
          {section === "scp" && (
            <div>
              <h2 className="text-xl font-semibold text-[#16A34A] mb-2">
                🧮 Smart Consumption Prioritization (SCP)
              </h2>
              <p>
                SCP ranks food based on freshness, storage, and predicted
                expiry. It helps you prioritize food that will expire sooner.
              </p>
            </div>
          )}

          {section === "personalization" && (
            <div>
              <h2 className="text-xl font-semibold text-[#16A34A] mb-2">
                🧠 Adaptive Personalization
              </h2>
              <p>
                Our system adjusts expiry predictions based on your habits and
                feedback. The more you use it, the more accurate it becomes.
              </p>
            </div>
          )}

          {section === "benefits" && (
            <div>
              <h2 className="text-xl font-semibold text-[#16A34A] mb-2">
                🌱 Benefits for You
              </h2>
              <ul className="list-disc ml-6 space-y-2">
                <li>Reduce food waste and save money</li>
                <li>Track and plan meals smarter</li>
                <li>Personalized AI predictions based on your consumption</li>
              </ul>
            </div>
          )}
        </motion.div>
      </motion.div>

      {/* Personalization Form (Hidden by default) */}
      {showForm && (
        <motion.div
          className="max-w-2xl bg-white rounded-2xl shadow-xl p-8 mt-10"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
        >
          <h2 className="text-2xl font-semibold text-[#1E293B] mb-4">
            Start Personalizing
          </h2>
          <form className="grid gap-4 text-left">
            <label className="font-semibold">Food Name</label>
            <input
              type="text"
              placeholder="Enter food name"
              className="border p-3 rounded-md focus:ring-2 focus:ring-[#16A34A]"
              required
            />

            <label className="font-semibold">Category</label>
            <select className="border p-3 rounded-md" required>
              <option value="">Select Category</option>
              <option>Dairy</option>
              <option>Fruit</option>
              <option>Vegetable</option>
              <option>Grain</option>
              <option>Meat</option>
              <option>Snack</option>
            </select>

            <label className="font-semibold">Storage Type</label>
            <select className="border p-3 rounded-md" required>
              <option value="">Select Storage</option>
              <option>Freezer</option>
              <option>Fridge</option>
              <option>Pantry</option>
            </select>

            <label className="font-semibold">Quantity</label>
            <input
              type="number"
              min="1"
              placeholder="Enter quantity"
              className="border p-3 rounded-md"
              required
            />

            <label className="font-semibold">
              How often do you use food before expiry?
            </label>
            <select className="border p-3 rounded-md" required>
              <option value="">Select</option>
              <option>Always before expiry</option>
              <option>Sometimes before expiry</option>
              <option>After expiry (occasionally)</option>
            </select>

            <button
              type="submit"
              className="mt-4 bg-[#16A34A] text-white py-3 rounded-md hover:bg-[#15803D] font-semibold transition-all"
            >
              Submit Personalization
            </button>
          </form>
        </motion.div>
      )}
    </div>
  );
};

export default FoodExpiryPredictor;
