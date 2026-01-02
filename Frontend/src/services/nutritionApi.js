// src/services/nutritionApi.js

const API_BASE =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") || "http://127.0.0.1:5000";

async function request(path, options = {}) {
  const url = `${API_BASE}${path}`;

  const res = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });

  const text = await res.text();
  let data;
  try {
    data = JSON.parse(text);
  } catch {
    data = { raw: text };
  }

  if (!res.ok) {
    const msg = data?.error || data?.message || `Request failed (${res.status})`;
    throw new Error(msg);
  }

  return data;
}

/* -----------------------------
   Step 2: Food search
------------------------------ */
export async function searchFoods(q, limit = 15) {
  const qs = new URLSearchParams({
    q: q || "",
    limit: String(limit),
  }).toString();

  return request(`/api/nutrition/foods/search?${qs}`, {
    method: "GET",
  });
}

/* -----------------------------
   Step 4: Intake add
------------------------------ */
export async function addIntake({ user_id, food_id, food_name, quantity, date }) {
  return request(`/api/nutrition/intake/add`, {
    method: "POST",
    body: JSON.stringify({
      user_id,
      food_id,
      food_name,
      quantity,
      date,
    }),
  });
}

/* -----------------------------
   Step 3: Profile (optional)
------------------------------ */
export async function getProfile(user_id) {
  const qs = new URLSearchParams({ user_id: user_id || "demo" }).toString();
  return request(`/api/nutrition/profile?${qs}`, { method: "GET" });
}

export async function saveProfile(profile) {
  return request(`/api/nutrition/profile`, {
    method: "POST",
    body: JSON.stringify(profile || {}),
  });
}

/* -----------------------------
   Step 4: Summary (optional)
------------------------------ */
export async function getIntakeSummary(user_id, period = "weekly") {
  const qs = new URLSearchParams({
    user_id: user_id || "demo",
    period: period || "weekly",
  }).toString();

  return request(`/api/nutrition/intake/summary?${qs}`, { method: "GET" });
}

/* -----------------------------
   Step 5: Report (optional)
------------------------------ */
export async function getReport(user_id, period = "monthly") {
  const qs = new URLSearchParams({
    user_id: user_id || "demo",
    period: period || "monthly",
  }).toString();

  return request(`/api/nutrition/report?${qs}`, { method: "GET" });
}

/* -----------------------------
   Step 9: Conditions list
------------------------------ */
export async function getConditions() {
  return request(`/api/nutrition/conditions`, {
    method: "GET",
  });
}

