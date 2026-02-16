import { useMemo, useState } from "react";
import "./MedicationAlerts.css";
import {
  FOOD_MED_INTERACTIONS,
  MED_CATEGORIES,
  CONDITION_TAGS,
} from "../../../data/foodMedicineInteractions";

const Pill = ({ text, tone = "neutral" }) => (
  <span className={`ma-pill ma-pill-${tone}`}>{text}</span>
);

function SeverityDot({ level }) {
  return <span className={`ma-sev ma-sev-${level}`} title={level} />;
}

export default function MedicationAlerts() {
  const [query, setQuery] = useState("");
  const [selectedMed, setSelectedMed] = useState("all");
  const [selectedCondition, setSelectedCondition] = useState("all");
  const [severity, setSeverity] = useState("all"); // all | high | medium | low
  const [expandedId, setExpandedId] = useState(null);

  const meds = useMemo(() => ["all", ...MED_CATEGORIES], []);
  const conditions = useMemo(() => ["all", ...CONDITION_TAGS], []);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();

    return FOOD_MED_INTERACTIONS.filter((row) => {
      const matchQuery =
        !q ||
        row.medicine.toLowerCase().includes(q) ||
        row.category.toLowerCase().includes(q) ||
        row.aliases.some((a) => a.toLowerCase().includes(q)) ||
        row.avoidFoods.some((f) => f.toLowerCase().includes(q)) ||
        row.limitFoods.some((f) => f.toLowerCase().includes(q)) ||
        row.preferFoods.some((f) => f.toLowerCase().includes(q)) ||
        row.notes.toLowerCase().includes(q);

      const matchMed = selectedMed === "all" ? true : row.category === selectedMed;

      const matchCondition =
        selectedCondition === "all"
          ? true
          : (row.conditions || []).includes(selectedCondition);

      const matchSeverity = severity === "all" ? true : row.severity === severity;

      return matchQuery && matchMed && matchCondition && matchSeverity;
    });
  }, [query, selectedMed, selectedCondition, severity]);

  const stats = useMemo(() => {
    const total = FOOD_MED_INTERACTIONS.length;
    const shown = filtered.length;
    const high = filtered.filter((x) => x.severity === "high").length;
    const medium = filtered.filter((x) => x.severity === "medium").length;
    const low = filtered.filter((x) => x.severity === "low").length;
    return { total, shown, high, medium, low };
  }, [filtered]);

  function toggleExpand(id) {
    setExpandedId((prev) => (prev === id ? null : id));
  }

  return (
    <div className="ma-wrap">
      {/* HERO SECTION */}
      <div className="ma-hero">
        <div>
          <h2 className="ma-title">Medication Alerts</h2>
          <p className="ma-subtitle">Check medicine & food interactions — avoid, limit, or prefer foods based on your medications.</p>
        </div>
        <span className="ma-badge">Food × Medicine</span>
      </div>

      {/* CONTROLS CARD */}
      <div className="ma-card-controls">
        <div className="ma-controls">
          <div className="ma-field">
            <label>Search</label>
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g., warfarin, metformin, grapefruit, vitamin K..."
            />
          </div>

          <div className="ma-field">
            <label>Medicine category</label>
            <select value={selectedMed} onChange={(e) => setSelectedMed(e.target.value)}>
              {meds.map((m) => (
                <option key={m} value={m}>
                  {m === "all" ? "All categories" : m}
                </option>
              ))}
            </select>
          </div>

          <div className="ma-field">
            <label>Condition</label>
            <select
              value={selectedCondition}
              onChange={(e) => setSelectedCondition(e.target.value)}
            >
              {conditions.map((c) => (
                <option key={c} value={c}>
                  {c === "all" ? "All conditions" : c}
                </option>
              ))}
            </select>
          </div>

          <div className="ma-field">
            <label>Severity</label>
            <select value={severity} onChange={(e) => setSeverity(e.target.value)}>
              <option value="all">All</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>
        </div>

        {/* Summary */}
        <div className="ma-stats">
          <div className="ma-stat">
            <div className="ma-statLabel">Shown</div>
            <div className="ma-statValue">{stats.shown}</div>
            <div className="ma-statHint">out of {stats.total}</div>
          </div>

          <div className="ma-stat">
            <div className="ma-statLabel">High</div>
            <div className="ma-statValue">{stats.high}</div>
            <div className="ma-statHint">avoid priority</div>
          </div>

          <div className="ma-stat">
            <div className="ma-statLabel">Medium</div>
            <div className="ma-statValue">{stats.medium}</div>
            <div className="ma-statHint">limit priority</div>
          </div>

          <div className="ma-stat">
            <div className="ma-statLabel">Low</div>
            <div className="ma-statValue">{stats.low}</div>
            <div className="ma-statHint">general tips</div>
          </div>
        </div>
      </div>

      {/* Results */}
      <div className="ma-grid">
        {filtered.length === 0 ? (
          <div className="ma-empty fe-card">
            <h3>No matches found</h3>
            <p>Try a different keyword (medicine name / food item / vitamin).</p>
          </div>
        ) : (
          filtered.map((row) => {
            const expanded = expandedId === row.id;

            return (
              <div className="ma-card fe-card" key={row.id}>
                <div className="ma-cardTop">
                  <div className="ma-left">
                    <div className="ma-medRow">
                      <SeverityDot level={row.severity} />
                      <h3 className="ma-med">{row.medicine}</h3>
                    </div>

                    <div className="ma-meta">
                      <Pill text={row.category} tone="neutral" />
                      {(row.aliases || []).slice(0, 3).map((a) => (
                        <Pill key={a} text={a} tone="ghost" />
                      ))}
                      {(row.conditions || []).slice(0, 2).map((c) => (
                        <Pill key={c} text={c} tone="info" />
                      ))}
                    </div>
                  </div>

                  <button
                    className="ma-btn"
                    onClick={() => toggleExpand(row.id)}
                    type="button"
                  >
                    {expanded ? "Hide details" : "View details"}
                  </button>
                </div>

                {/* Quick summary blocks */}
                <div className="ma-blocks">
                  <div className="ma-block ma-avoid">
                    <div className="ma-blockTitle">Avoid</div>
                    <div className="ma-chipRow">
                      {(row.avoidFoods || []).map((f) => (
                        <span className="ma-chip" key={f}>{f}</span>
                      ))}
                    </div>
                  </div>

                  <div className="ma-block ma-limit">
                    <div className="ma-blockTitle">Limit</div>
                    <div className="ma-chipRow">
                      {(row.limitFoods || []).map((f) => (
                        <span className="ma-chip" key={f}>{f}</span>
                      ))}
                    </div>
                  </div>

                  <div className="ma-block ma-prefer">
                    <div className="ma-blockTitle">Prefer</div>
                    <div className="ma-chipRow">
                      {(row.preferFoods || []).map((f) => (
                        <span className="ma-chip" key={f}>{f}</span>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Expanded details */}
                {expanded && (
                  <div className="ma-details">
                    <div className="ma-detailGrid">
                      <div className="ma-detailCol">
                        <h4>Why this matters</h4>
                        <p className="ma-notes">{row.notes}</p>
                        <div className="ma-small">
                          <b>Severity:</b> {row.severity.toUpperCase()}
                        </div>
                      </div>

                      <div className="ma-detailCol">
                        <h4>Full list</h4>

                        <div className="ma-fullRow">
                          <span className="ma-tag">Avoid</span>
                          <span className="ma-fullText">
                            {(row.avoidFoods || []).join(", ") || "—"}
                          </span>
                        </div>

                        <div className="ma-fullRow">
                          <span className="ma-tag ma-tag-warn">Limit</span>
                          <span className="ma-fullText">
                            {(row.limitFoods || []).join(", ") || "—"}
                          </span>
                        </div>

                        <div className="ma-fullRow">
                          <span className="ma-tag ma-tag-good">Prefer</span>
                          <span className="ma-fullText">
                            {(row.preferFoods || []).join(", ") || "—"}
                          </span>
                        </div>

                        {(row.timingAdvice || "").trim() && (
                          <div className="ma-fullRow">
                            <span className="ma-tag ma-tag-info">Timing</span>
                            <span className="ma-fullText">{row.timingAdvice}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
