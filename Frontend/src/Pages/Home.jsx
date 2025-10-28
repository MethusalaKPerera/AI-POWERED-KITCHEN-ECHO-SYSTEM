import React from "react";
import "../App.css";
import { FaCamera, FaBrain, FaUtensils, FaHeartbeat } from "react-icons/fa";
import { MdOutlineAccessTime } from "react-icons/md";

function Home() {
  return (
    <div>
      <section className="hero">
        <div className="hero-box">
          <h1>COOK SMARTER. WASTE LESS.<br />LIVE HEALTHIER.</h1>
          <p>
            Your AI-powered kitchen companion that recognizes your ingredients,
            suggests recipes, and reduces food waste.
          </p>
          <div className="buttons">
            <button className="btn primary">Try the Demo</button>
            <button className="btn secondary">Learn More</button>
          </div>
        </div>
      </section>

      <section className="section how">
        <h2>How It Works</h2>
        <div className="cards">
          <Card icon={<FaCamera />} text="1. Snap your ingredients" />
          <Card icon={<FaBrain />} text="2. Let AI detect and understand what you have" />
          <Card icon={<FaUtensils />} text="3. Get personalized recipe ideas instantly" />
        </div>
      </section>

      <section className="section features">
        <h2>Key Features</h2>
        <div className="cards">
          <Feature icon={<FaCamera />} title="AI Ingredient Detection" />
          <Feature icon={<FaHeartbeat />} title="Personalized Nutrition" />
          <Feature icon={<MdOutlineAccessTime />} title="Smart Expiry Prediction" />
          <Feature icon={<FaUtensils />} title="Sustainable Meal Planning" />
        </div>
      </section>
    </div>
  );
}

function Card({ icon, text }) {
  return (
    <div className="card">
      <div className="icon">{icon}</div>
      <p>{text}</p>
    </div>
  );
}

function Feature({ icon, title }) {
  return (
    <div className="feature">
      <div className="icon">{icon}</div>
      <h4>{title}</h4>
    </div>
  );
}

export default Home;
