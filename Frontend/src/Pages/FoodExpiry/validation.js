// src/Pages/FoodExpiry/validation.js
export function validateRequired(value, fieldName) {
  if (!value || String(value).trim() === "") {
    return `${fieldName} is required`;
  }
  return null;
}

export function validatePositiveNumber(value, fieldName) {
  if (value === "" || value === null || value === undefined) {
    return `${fieldName} is required`;
  }
  const num = Number(value);
  if (Number.isNaN(num) || num <= 0) {
    return `${fieldName} must be a positive number`;
  }
  return null;
}

export function validateDate(value, fieldName) {
  if (!value) return `${fieldName} is required`;
  const isValid = /^\d{4}-\d{2}-\d{2}$/.test(value);
  if (!isValid) return `${fieldName} must be YYYY-MM-DD`;
  return null;
}
