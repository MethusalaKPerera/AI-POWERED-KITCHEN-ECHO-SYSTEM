// src/Pages/FoodExpiry/Use.jsx
import React, { useMemo, useState } from "react";
import { NavLink } from "react-router-dom";
import Sidebar from "../../Components/Dashboard/Sidebar.jsx";
import Topbar from "../../Components/Dashboard/Topbar.jsx";
import "./foodexpiry.css";

/* -----------------------------
   Small UI Helpers
----------------------------- */
function Pill({ children, tone = "green" }) {
  return <span className={`feuse-pill feuse-pill--${tone}`}>{children}</span>;
}

function AccordionCard({ id, openId, setOpenId, title, subtitle, pill, icon, children }) {
  const open = openId === id;

  return (
    <button
      type="button"
      className={`feuse-card feuse-card--accordion ${open ? "open" : ""}`}
      onClick={() => setOpenId(open ? null : id)}
    >
      <div className="feuse-card-top">
        <div className="feuse-card-icon">{icon}</div>

        <div className="feuse-card-main">
          <div className="feuse-card-titleRow">
            <div className="feuse-card-title">{title}</div>
            {pill ? <Pill tone="blue">{pill}</Pill> : null}
          </div>
          {subtitle ? <div className="feuse-card-subtitle">{subtitle}</div> : null}
        </div>

        <div className={`feuse-card-chevron ${open ? "rot" : ""}`}>⌄</div>
      </div>

      <div className={`feuse-card-body ${open ? "show" : ""}`}>{children}</div>
    </button>
  );
}

function FaqItem({ id, openId, setOpenId, q, a }) {
  const open = openId === id;

  return (
    <button
      type="button"
      className={`feuse-faq-item ${open ? "open" : ""}`}
      onClick={() => setOpenId(open ? null : id)}
    >
      <div className="feuse-faq-q">
        <span>{q}</span>
        <span className={`feuse-faq-chevron ${open ? "rot" : ""}`}>⌄</span>
      </div>

      <div className={`feuse-faq-a ${open ? "show" : ""}`}>{a}</div>
    </button>
  );
}

export default function Use() {
  const [mode, setMode] = useState("first"); // "first" | "regular"
  const [openStep, setOpenStep] = useState("s1"); // opened step
  const [openFaq, setOpenFaq] = useState(null);

  const steps = useMemo(
    () => [
      {
        id: "s1",
        no: 1,
        icon: "➕",
        title: "Add the item to the Inventory first",
        subtitle: "Create your inventory list with correct storage type.",
        details: (
          <div className="feuse-text">
            <p>
              Add your food item with <b>storage type</b> (fridge/freezer/pantry) and{" "}
              <b>purchase date</b>. The item is saved and visible in Inventory.
            </p>
            <ul className="feuse-ul">
              <li>More accurate storage type will give a better baseline expiry</li>
              <li>Add printed expiry (if available) for safer final results</li>
            </ul>
          </div>
        ),
      },
      {
        id: "s2",
        no: 2,
        icon: "🧩",
        title: "The initial expiry of the food is predicted using AEIF baseline",
        subtitle: "Domain base expiry + storage context = baseline prediction.",
        details: (
          <div className="feuse-text">
            <p>
              When you click <b>Predict</b> in Inventory, the system computes the baseline expiry
              using <b>AEIF</b> (base expiry intelligence + storage-aware rules).
            </p>
            <div className="feuse-mini">
              <span className="feuse-mini-label">Why baseline matters:</span>
              <span className="feuse-mini-value">It’s the safe starting point for all users.</span>
            </div>
          </div>
        ),
      },
      {
        id: "s3",
        no: 3,
        icon: "🎯",
        title: "If the particular food has feedback greater than or equal to 5, AED personalization applies",
        subtitle: "Your behavior adjusts expiry (bounded, not extreme).",
        details: (
          <div className="feuse-text">
            <p>
              After you provide enough feedback (used-before-expiry / spoiled), <b>AED</b> adjusts
              expiry to match your real-world behavior.
            </p>
            <ul className="feuse-ul">
              <li>Personalization starts after <b>greater than or equal to 5 feedbacks</b></li>
              <li>Adjustment is bounded to avoid unsafe extreme shifts</li>
              <li>Results improve as you keep using the system</li>
            </ul>
          </div>
        ),
      },
      {
        id: "s4",
        no: 4,
        icon: "🛡️",
        title: "Printed expiry cap exists to make sure the final date stays safe",
        subtitle: "If printed expiry exists, we never recommend beyond it.",
        details: (
          <div className="feuse-text">
            <p>
              If a printed expiry date exists, the system caps the final predicted date to avoid
              unsafe recommendations.
            </p>
            <div className="feuse-alert feuse-alert--warn">
              Safety rule: printed expiry overrides any longer prediction.
            </div>
          </div>
        ),
      },
      {
        id: "s5",
        no: 5,
        icon: "⏳",
        title: "SCP ranks urgency order of the food to be used -> “use-first which expires earlier” ",
        subtitle: "Clear priority list based on days remaining.",
        details: (
          <div className="feuse-text">
            <p>
              After final expiry is computed, <b>SCP</b> ranks items by urgency using days left.
            </p>
            <ul className="feuse-ul">
              <li>Shows what to use first (prevents waste)</li>
              <li>Highlights expiring and expired items clearly</li>
            </ul>
          </div>
        ),
      },
      {
        id: "s6",
        no: 6,
        icon: "📌",
        title: "Prediction History stores results over time",
        subtitle: "Shows personalization progress and supports evaluation proof.",
        details: (
          <div className="feuse-text">
            <p>
              Every prediction is stored in <b>predictionHistory</b>. This helps prove
              personalization (AED) and shows improvements over time.
            </p>
            <div className="feuse-mini">
              <span className="feuse-mini-label">Proof point:</span>
              <span className="feuse-mini-value">
                Panel can see the same item’s predictions evolve as feedback grows.
              </span>
            </div>
          </div>
        ),
      },
    ],
    []
  );

  return (
    <div className="fe-layout">
      <Sidebar />

      <div className="fe-main">
        <Topbar title="How to Use the Expiry Predictor" badge="Interactive Guide" />

        <div className="fe-main__content">
          <div className="feuse2">
            {/* HERO */}
            <section className="feuse2-hero">
              <div className="feuse2-hero-left">
                <div className="feuse2-badge">
                  <span className="feuse2-badgeDot" />
                  This is the Food Expiry Predictor with AEIF + AED + SCP
                </div>

                <h2 className="feuse2-title">
                  Learn it fast. <span>Use it smarter.</span>
                </h2>

                <p className="feuse2-sub">
                  Click each step to expand details. This guide helps both first-time and regular users
                  understand how predictions and personalization work.
                </p>

                
                {/* Mode Switch */}
                <div className="feuse2-switch">
                  <button
                    type="button"
                    className={`feuse2-chip ${mode === "first" ? "active" : ""}`}
                    onClick={() => setMode("first")}
                  >
                    First-time user
                  </button>
                  <button
                    type="button"
                    className={`feuse2-chip ${mode === "regular" ? "active" : ""}`}
                    onClick={() => setMode("regular")}
                  >
                    Regular user
                  </button>
                </div>

                {mode === "first" ? (
                  <div className="feuse2-callout">
                    <b>New here?</b> Start by adding items and giving feedback. AED personalization begins after{" "}
                    <b>≥ 5 feedbacks</b>.
                  </div>
                ) : (
                  <div className="feuse2-callout">
                    <b>Welcome back!</b> Your AED adjustments strengthen over time. predictionHistory helps prove your
                    personalization progress.
                  </div>
                )}
              </div>

              <div className="feuse2-hero-right" aria-hidden="true">
                <div className="feuse2-orb feuse2-orb--a" />
                <div className="feuse2-orb feuse2-orb--b" />
                <div className="feuse2-orb feuse2-orb--c" />
              </div>
            </section>

            {/* QUICK CARDS */}
            <section className="feuse2-cards">
              <div className="feuse2-kpi">
                <div className="feuse2-kpiIcon">🧩</div>
                <div className="feuse2-kpiTitle">AEIF baseline</div>
                <div className="feuse2-kpiText">Base expiry knowledge + storage rules.</div>
              </div>

              <div className="feuse2-kpi">
                <div className="feuse2-kpiIcon">🎯</div>
                <div className="feuse2-kpiTitle">AED personalization</div>
                <div className="feuse2-kpiText">Activates after ≥ 5 feedbacks.</div>
              </div>

              <div className="feuse2-kpi">
                <div className="feuse2-kpiIcon">⏳</div>
                <div className="feuse2-kpiTitle">SCP priority</div>
                <div className="feuse2-kpiText">Use-first ranking by days left.</div>
              </div>

              <div className="feuse2-kpi">
                <div className="feuse2-kpiIcon">📌</div>
                <div className="feuse2-kpiTitle">predictionHistory</div>
                <div className="feuse2-kpiText">Stores proof over time.</div>
              </div>
            </section>

            {/* STEPS (Interactive) */}
            <section className="feuse2-grid">
              <div className="feuse2-panel">
                <div className="feuse2-panelHead">
                  <h3 className="feuse2-h3">Interactive Steps</h3>
                  <span className="feuse2-pill">Click to expand</span>
                </div>

                <div className="feuse2-stepList">
                  {steps.map((s) => (
                    <AccordionCard
                      key={s.id}
                      id={s.id}
                      openId={openStep}
                      setOpenId={setOpenStep}
                      title={`${s.no}. ${s.title}`}
                      subtitle={s.subtitle}
                      pill={s.pill}
                      icon={s.icon}
                    >
                      {s.details}
                    </AccordionCard>
                  ))}
                </div>
              </div>

              {/* RIGHT SIDE: PERSONALIZATION QUICK */}
              <div className="feuse2-panel">
                <div className="feuse2-panelHead">
                  <h3 className="feuse2-h3">Personalization Snapshot</h3>
                  <span className="feuse2-pill">Simple view</span>
                </div>

                <div className="feuse2-box feuse2-box--good">
                  <div className="feuse2-boxTitle">Before feedback (New user)</div>
                  <div className="feuse2-boxText">
                    Predictions rely on <b>AEIF baseline</b> only.
                  </div>
                </div>

                <div className="feuse2-box feuse2-box--info">
                  <div className="feuse2-boxTitle">After ≥ 5 feedbacks</div>
                  <div className="feuse2-boxText">
                    <b>AED personalization</b> adjusts expiry using your outcomes.
                  </div>
                </div>

                <div className="feuse2-box feuse2-box--warn">
                  <div className="feuse2-boxTitle">Always enforced</div>
                  <div className="feuse2-boxText">
                    Printed expiry cap keeps results <b>safe</b>.
                  </div>
                </div>

                <div className="feuse2-box feuse2-box--neutral">
                  <div className="feuse2-boxTitle">Why history matters</div>
                  <div className="feuse2-boxText">
                    predictionHistory shows proof that predictions change as you give feedback.
                  </div>
                </div>
              </div>
            </section>

            {/* FAQ */}
            <section className="feuse2-faq">
              <div className="feuse2-panel">
                <div className="feuse2-panelHead">
                  <h3 className="feuse2-h3">FAQ</h3>
                  <span className="feuse2-pill">Interactive</span>
                </div>

                <FaqItem
                  id="f1"
                  openId={openFaq}
                  setOpenId={setOpenFaq}
                  q="Do I need to give feedback?"
                  a="Yes. Without feedback the system can only use baseline expiry (AEIF). Feedback activates personalization (AED)."
                />
                <FaqItem
                  id="f2"
                  openId={openFaq}
                  setOpenId={setOpenFaq}
                  q="Why do I see a “use-first” list?"
                  a="SCP ranks urgency so you immediately know which items are most critical to use first."
                />
                <FaqItem
                  id="f3"
                  openId={openFaq}
                  setOpenId={setOpenFaq}
                  q="How can you prove personalization?"
                  a="Every prediction is stored in predictionHistory, which shows how your final dates change as you provide feedback over time."
                />
              </div>
            </section>

            <div className="feuse2-footer">
              <NavLink to="/food-expiry" className="feuse2-link">
                ← Back to Dashboard
              </NavLink>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
