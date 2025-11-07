import React, { useState } from "react";
import "./GuidanceForm.css";

function GuidanceForm() {
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
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log("Form Submitted:", formData);
    alert("✅ Nutritional details submitted successfully!");
  };

  return (
    <section className="section form-section">
      <h2>Enter Your Details for Personalized Nutrition</h2>
      <form className="user-form" onSubmit={handleSubmit}>
        <div className="form-grid">
          <input name="name" value={formData.name} onChange={handleChange} placeholder="Full Name" required />
          <input name="age" type="number" value={formData.age} onChange={handleChange} placeholder="Age" required />
          <input name="weight" type="number" value={formData.weight} onChange={handleChange} placeholder="Weight (kg)" required />
          <input name="height" type="number" value={formData.height} onChange={handleChange} placeholder="Height (cm)" required />

          <select name="gender" value={formData.gender} onChange={handleChange} required>
            <option value="">Gender</option>
            <option value="male">Male</option>
            <option value="female">Female</option>
            <option value="other">Other</option>
          </select>

          <input name="allergies" value={formData.allergies} onChange={handleChange} placeholder="Allergies (if any)" />
          <input name="sleep" value={formData.sleep} onChange={handleChange} placeholder="Sleep Schedule (e.g. 11 PM - 6 AM)" />
          <input name="goal" value={formData.goal} onChange={handleChange} placeholder="Fitness Goal (e.g. weight loss)" />
          <input name="medication" value={formData.medication} onChange={handleChange} placeholder="Medications (optional)" />
        </div>

        <button className="btn primary" type="submit">Submit Details</button>
      </form>
    </section>
  );
}

export default GuidanceForm;
