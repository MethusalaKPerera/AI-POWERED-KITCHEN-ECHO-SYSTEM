import React from "react";
import "./App.css";
import { FaCamera, FaBrain, FaUtensils, FaHeartbeat } from "react-icons/fa";
import { MdOutlineAccessTime } from "react-icons/md";

function App() {
  return (
    <div className="app">
      {/* HERO SECTION */}
      <section className="hero">
        <div className="hero-box">
        <h1>
          COOK SMARTER. WASTE LESS.
          <br /> LIVE HEALTHIER.
        </h1>
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

      {/* HOW IT WORKS */}
      <section className="section how">
        <h2>How It Works</h2>
        <div className="cards">
          <Card icon={<FaCamera />} text="1. Snap your ingredients" />
          <Card icon={<FaBrain />} text="2. Let AI detect and understand what you have" />
          <Card icon={<FaUtensils />} text="3. Get personalized recipe ideas instantly" />
        </div>
      </section>

      {/* KEY FEATURES */}
      <section className="section features">
        <h2>Key Features</h2>
        <div className="cards">
          <Feature icon={<FaCamera />} title="AI Ingredient Detection" />
          <Feature icon={<FaHeartbeat />} title="Personalized Nutrition" />
          <Feature icon={<MdOutlineAccessTime />} title="Smart Expiry Prediction" />
          <Feature icon={<FaUtensils />} title="Sustainable Meal Planning" />
        </div>
      </section>

      {/* RESEARCH + STATISTICS */}
      <section className="section research">
        <div className="research-col">
          <h3>Research Origin Section</h3>
          <p>
            Developed by <b>25-26J-351</b> — as part of the{" "}
            <b>IT4010 Research Project</b> (SLIIT)
          </p>
          <div className="team">
            <TeamCard name="Perera U.M.K." role="Lead AI" quote="Inventing kitchen tech" />
            <TeamCard name="Muraleswaran D" role="AI Designer" quote="Crafting taste-driven AI" />
            <TeamCard name="Shahmi M.T.M" role="UX Designer" quote="Uncovering food insight" />
            <TeamCard name="D.H Jayasundara" role="Developer" quote="Uncovering food insight" />
          </div>
        </div>

        <div className="stats-col">
          <h3>Statistics Strip</h3>
          <div className="stats-box">
            <Stat emoji="🤖" text="10K+ AI-generated recipes" />
            <Stat emoji="💚" text="30% less food waste" />
            <Stat emoji="🏡" text="Built for smarter kitchens" />
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer>
        <p>© 2025 Sea Pony Studios. All rights reserved.</p>
        <div className="footer-links">
          <a href="#">About</a> • <a href="#">Features</a> • <a href="#">Demo</a> • <a href="#">Contact</a>
        </div>
      </footer>
    </div>
  );
}

// ---- Reusable Components ----
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

function TeamCard({ name, role, quote }) {
  return (
    <div className="team-card">
      <div className="avatar"></div>
      <h5>{name}</h5>
      <p className="role">{role}</p>
      <p className="quote">“{quote}”</p>
    </div>
  );
}

function Stat({ emoji, text }) {
  return (
    <div className="stat">
      <span>{emoji}</span>
      <p>{text}</p>
    </div>
  );
}

export default App;
