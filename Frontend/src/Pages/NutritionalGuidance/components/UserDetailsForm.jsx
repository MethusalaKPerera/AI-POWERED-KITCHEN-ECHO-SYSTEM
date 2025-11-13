import React, { useState } from "react";
import "../styles/UserDetailsForm.css";

function UserDetailsForm() {
  const [formData, setFormData] = useState({
    name: "",
    age: "",
    weight: "",
    height: "",
    gender: "",
    allergies: "",
    sleep: "",
    goal: "",
    medication: "",
    medicalConditions: [],
    customCondition: "",
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  // ✅ Handle checkbox selections
  const handleCheckboxChange = (e) => {
    const { value, checked } = e.target;
    setFormData((prev) => {
      const updated = checked
        ? [...prev.medicalConditions, value]
        : prev.medicalConditions.filter((cond) => cond !== value);
      return { ...prev, medicalConditions: updated };
    });
  };

  // ✅ Handle submit
  const handleSubmit = (e) => {
    e.preventDefault();
    console.log("Form Submitted:", formData);
    alert("✅ User details submitted successfully!");
  };

  // 🩺 All medical condition options
  const medicalOptions = [
    "Diabetes",
    "High Blood Pressure",
    "High Cholesterol",
    "Hypertension",
    "Heart Disease",
    "Kidney Disease",
    "Thyroid Issues",
    "Asthma",
  ];

  return (
    <section className="section form-section">
      <h2>Enter Your Details for Personalized Nutrition</h2>

      <form className="user-form" onSubmit={handleSubmit}>
        {/* 🧍 Personal Information */}
        <h3 className="form-subtitle">👤 Personal Information</h3>
        <div className="form-grid">
          <input
            name="name"
            value={formData.name}
            onChange={handleChange}
            placeholder="Full Name"
            required
          />
          <input
            name="age"
            type="number"
            value={formData.age}
            onChange={handleChange}
            placeholder="Age"
            required
          />
          <select
            name="gender"
            value={formData.gender}
            onChange={handleChange}
            required
          >
            <option value="">Gender</option>
            <option value="male">Male</option>
            <option value="female">Female</option>
            <option value="other">Other</option>
          </select>
        </div>

        {/* ⚖️ Health Information */}
        <h3 className="form-subtitle">🩺 Health Information</h3>
        <div className="form-grid">
          <input
            name="weight"
            type="number"
            value={formData.weight}
            onChange={handleChange}
            placeholder="Weight (kg)"
            required
          />
          <input
            name="height"
            type="number"
            value={formData.height}
            onChange={handleChange}
            placeholder="Height (cm)"
            required
          />
          <input
            name="allergies"
            value={formData.allergies}
            onChange={handleChange}
            placeholder="Allergies (if any)"
          />
          <input
            name="medication"
            value={formData.medication}
            onChange={handleChange}
            placeholder="Medications (optional)"
          />
        </div>

        {/* 💊 Medical Conditions */}
        <h3 className="form-subtitle">💊 Medical Conditions</h3>
        <div className="checkbox-grid">
          {medicalOptions.map((condition) => (
            <label key={condition} className="checkbox-label">
              <input
                type="checkbox"
                value={condition}
                checked={formData.medicalConditions.includes(condition)}
                onChange={handleCheckboxChange}
              />
              {condition}
            </label>
          ))}
        </div>

        <input
          name="customCondition"
          value={formData.customCondition}
          onChange={handleChange}
          placeholder="Other (please specify)"
        />

        {/* 🌙 Lifestyle */}
        <h3 className="form-subtitle">🌙 Lifestyle</h3>
        <div className="form-grid">
          <input
            name="sleep"
            value={formData.sleep}
            onChange={handleChange}
            placeholder="Sleep Schedule (e.g. 11 PM - 6 AM)"
          />
          <input
            name="goal"
            value={formData.goal}
            onChange={handleChange}
            placeholder="Fitness Goal (e.g. weight loss)"
          />
        </div>

        <button className="btn primary" type="submit">
          Submit Details
        </button>
      </form>
    </section>
  );
}

export default UserDetailsForm;
