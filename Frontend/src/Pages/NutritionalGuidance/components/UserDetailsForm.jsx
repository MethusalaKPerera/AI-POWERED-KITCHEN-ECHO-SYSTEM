import React, { useEffect, useMemo, useState } from "react";
import {
  getProfile,
  saveProfile,
  getConditions,
  DEFAULT_USER_ID,
} from "../../../services/nutritionApi";
import "./UserDetailsForm.css";

export default function UserDetailsForm({ userId = DEFAULT_USER_ID }) {
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [err, setErr] = useState("");
  const [ok, setOk] = useState("");

  const [age, setAge] = useState(22);
  const [group, setGroup] = useState("male");
  const [selectedConditions, setSelectedConditions] = useState([]);
  const [conditions, setConditions] = useState([]);

  const loadAll = async () => {
    setLoading(true);
    setErr("");
    setOk("");
    try {
      const [p, c] = await Promise.all([getProfile(userId), getConditions()]);
      const profile = p?.profile || {};

      setAge(profile.age ?? 22);
      setGroup(profile.group ?? "male");
      setSelectedConditions(profile.conditions ?? []);
      setConditions(c?.items || []);
    } catch (e) {
      setErr(e.message || "Failed to load profile/conditions");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAll();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userId]);

  const toggleCondition = (name) => {
    setOk("");
    setErr("");
    setSelectedConditions((prev) => {
      const key = String(name || "").trim();
      if (!key) return prev;

      const has = prev.includes(key);
      return has ? prev.filter((x) => x !== key) : [...prev, key];
    });
  };

  const onSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setErr("");
    setOk("");

    const a = Number(age);
    if (!Number.isFinite(a) || a < 1 || a > 120) {
      setSaving(false);
      setErr("Age must be between 1 and 120.");
      return;
    }

    try {
      const payload = {
        user_id: userId || DEFAULT_USER_ID,
        age: a,
        group: group,
        conditions: selectedConditions,
      };

      const res = await saveProfile(payload);
      setOk(res?.message || "Profile saved successfully!");
    } catch (e2) {
      setErr(e2.message || "Failed to save profile");
    } finally {
      setSaving(false);
    }
  };

  const conditionTitle = useMemo(() => {
    if (!conditions.length) return "Health Conditions";
    return `Health Conditions (${selectedConditions.length} selected)`;
  }, [conditions.length, selectedConditions.length]);

  return (
    <div className="ud-wrap">
      {/* ✅ Hero header (same style as MealLogger / NutritionTracker) */}
      <div className="ud-hero">
        <div>
          <h2 className="ud-title">User Profile</h2>
          <p className="ud-subtitle">
            Update your age, gender and health conditions to generate accurate requirements and deficiency reports.
          </p>
        </div>

        <div className="ud-meta">
          <div className="ud-pill">
            User: <b>{userId || DEFAULT_USER_ID}</b>
          </div>
        </div>
      </div>

      {err && <div className="ud-alert ud-error">{err}</div>}
      {ok && <div className="ud-alert ud-ok">{ok}</div>}

      <form onSubmit={onSave} className="ud-card">
        <div className="ud-grid">
          <div className="ud-field">
            <label className="ud-label">User Name</label>
            <input className="ud-input" value={userId || DEFAULT_USER_ID} disabled />
          </div>

          <div className="ud-field">
            <label className="ud-label">Age</label>
            <input
              className="ud-input"
              type="number"
              min="1"
              max="120"
              value={age}
              onChange={(e) => setAge(e.target.value)}
            />
          </div>

          <div className="ud-field">
            <label className="ud-label">Gender</label>
            <select className="ud-input" value={group} onChange={(e) => setGroup(e.target.value)}>
              <option value="male">male</option>
              <option value="female">female</option>
            </select>
          </div>
        </div>

        <div className="ud-section">
          <div className="ud-section-title">{conditionTitle}</div>

          {loading ? (
            <div className="ud-muted">Loading conditions...</div>
          ) : conditions.length ? (
            <div className="ud-chips">
              {conditions.map((c) => {
                const name = c.condition || c.name || "";
                const checked = selectedConditions.includes(name);
                return (
                  <button
                    type="button"
                    key={name}
                    className={checked ? "ud-chip active" : "ud-chip"}
                    onClick={() => toggleCondition(name)}
                  >
                    {checked ? "✅ " : ""}
                    {name}
                  </button>
                );
              })}
            </div>
          ) : (
            <div className="ud-muted">
              No conditions list found. Make sure backend endpoint <b>/api/nutrition/conditions</b> works.
            </div>
          )}
        </div>

        <div className="ud-actions">
          <button className="ud-save" type="submit" disabled={saving}>
            {saving ? "Saving..." : "Save Profile"}
          </button>

          <div className="ud-tip">
            Tip: Keep your profile updated for better nutrient targets and more accurate reports.
          </div>
        </div>
      </form>
    </div>
  );
}
