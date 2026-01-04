// src/services/nutritionApi.js

const BASE = "http://127.0.0.1:5000";

async function request(path, options = {}) {
  const url = path.startsWith("http") ? path : `${BASE}${path}`;

  const res = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    credentials: "include",
  });

  // Try to parse JSON always
  let data = null;
  const text = await res.text();
  try {
    data = text ? JSON.parse(text) : null;
  } catch (e) {
    data = { raw: text };
  }

  if (!res.ok) {
    const msg =
      data?.message ||
      data?.error ||
      `Request failed (${res.status})`;
    throw new Error(msg);
  }

  return data;
}

/* -----------------------------
   Step 2: Food Search
------------------------------ */
export async function searchFoods(q, limit = 15) {
  const qs = encodeURIComponent(q || "");
  return request(`/api/nutrition/foods/search?q=${qs}&limit=${limit}`, {
    method: "GET",
  });
}

/* -----------------------------
   Step 3: Add Intake
------------------------------ */
export async function addIntake(payload) {
  return request(`/api/nutrition/intake/add`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

/* -----------------------------
   Step 4: Get Summary
------------------------------ */
export async function getIntakeSummary(userId = "demo", period = "weekly") {
  const uid = encodeURIComponent(userId || "demo");
  const p = encodeURIComponent(period || "weekly");
  return request(`/api/nutrition/intake/summary?user_id=${uid}&period=${p}`, {
    method: "GET",
  });
}

/* -----------------------------
   Step 5/7: Predictive Report
------------------------------ */
export async function getReport(userId = "demo", period = "monthly") {
  const uid = encodeURIComponent(userId || "demo");
  const p = encodeURIComponent(period || "monthly");
  return request(`/api/nutrition/report?user_id=${uid}&period=${p}`, {
    method: "GET",
  });
}

/* -----------------------------
   Step 9: User Profile
------------------------------ */
export async function getProfile(userId = "demo") {
  const uid = encodeURIComponent(userId || "demo");
  return request(`/api/nutrition/profile?user_id=${uid}`, {
    method: "GET",
  });
}

export async function saveProfile(payload) {
  return request(`/api/nutrition/profile`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

/* -----------------------------
   Step 9: Conditions list
------------------------------ */
export async function getConditions() {
  return request(`/api/nutrition/conditions`, { method: "GET" });
}

/* -----------------------------
   ✅ NEW: ML Deficiency Risk
------------------------------ */
export async function getMLRisk(userId = "demo", period = "monthly") {
  const uid = encodeURIComponent(userId || "demo");
  const p = encodeURIComponent(period || "monthly");
  return request(`/api/nutrition/ml-risk?user_id=${uid}&period=${p}`, {
    method: "GET",
  });
}
