// src/api/foodApi.js
import axios from "axios";

// Change this to your actual backend URL
const API = axios.create({
  baseURL: "/api/food",
});

// Extract readable error
function getErr(err) {
  return (
    err?.response?.data?.error ||
    err?.response?.data?.message ||
    err.message ||
    "Unknown server error"
  );
}

// -----------------------
// GET ALL FOODS
// -----------------------
export async function getAllFoods() {
  try {
    const res = await API.get("/");
    return res.data;
  } catch (err) {
    throw new Error(getErr(err));
  }
}

// -----------------------
// PREDICT ONLY
// -----------------------
export async function predictExpiry(payload) {
  try {
    const res = await API.post("/predict", payload);
    return res.data;
  } catch (err) {
    throw new Error(getErr(err));
  }
}

// -----------------------
// ADD FOOD
// -----------------------
export async function addFood(payload) {
  try {
    const res = await API.post("/add", payload);
    return res.data;
  } catch (err) {
    throw new Error(getErr(err));
  }
}

// -----------------------
// FEEDBACK (AED training)
// -----------------------
export async function sendFeedback(payload) {
  try {
    const res = await API.post("/feedback", payload);
    return res.data;
  } catch (err) {
    throw new Error(getErr(err));
  }
}

// -----------------------
// UPDATE FOOD
// -----------------------
export async function updateFood(id, payload) {
  try {
    const res = await API.put(`/update/${id}`, payload);
    return res.data;
  } catch (err) {
    throw new Error(getErr(err));
  }
}

// -----------------------
// DELETE FOOD
// -----------------------
export async function deleteFood(id) {
  try {
    const res = await API.delete(`/delete/${id}`);
    return res.data;
  } catch (err) {
    throw new Error(getErr(err));
  }
}
