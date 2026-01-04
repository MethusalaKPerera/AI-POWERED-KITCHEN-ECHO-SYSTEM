// src/api/foodApi.js
import axios from "axios";

// For Vite: set in .env -> VITE_API_BASE_URL=http://127.0.0.1:5000
const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:5000";

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 20000,
  headers: { "Content-Type": "application/json" },
});

// Normalized error message
function toMessage(err) {
  const msg =
    err?.response?.data?.error ||
    err?.response?.data?.message ||
    err?.message ||
    "Request failed";
  return new Error(msg);
}

// -----------------------------
// FoodExpiry endpoints (/api/food/*)
// -----------------------------
export async function getAllFoods() {
  try {
    const res = await api.get("/api/food/");
    return res.data;
  } catch (err) {
    throw toMessage(err);
  }
}

export async function predictExpiry(payload) {
  try {
    const res = await api.post("/api/food/predict", payload);
    return res.data;
  } catch (err) {
    throw toMessage(err);
  }
}

export async function addFood(payload) {
  try {
    const res = await api.post("/api/food/add", payload);
    return res.data;
  } catch (err) {
    throw toMessage(err);
  }
}

export async function sendFeedback(payload) {
  try {
    const res = await api.post("/api/food/feedback", payload);
    return res.data;
  } catch (err) {
    throw toMessage(err);
  }
}

export async function updateFood(id, payload) {
  try {
    const res = await api.put(`/api/food/update/${id}`, payload);
    return res.data;
  } catch (err) {
    throw toMessage(err);
  }
}

export async function deleteFood(id) {
  try {
    const res = await api.delete(`/api/food/delete/${id}`);
    return res.data;
  } catch (err) {
    throw toMessage(err);
  }
}
