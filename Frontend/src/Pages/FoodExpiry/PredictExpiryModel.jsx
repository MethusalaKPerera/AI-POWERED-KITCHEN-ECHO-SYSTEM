import React, { useEffect, useMemo, useState } from "react";
import "./PredictExpiryModal.css";

/*
  Props:
  - open: boolean
  - onClose: function
  - selectedFood: object
  - onPredict: async function(payload) => response
    Expected payload:
      {
        foodId,
        region,
        storage_temperature_c,
        storage_humidity_pct,
        printedExpiryDate
      }

    Expected response fields (any of these are supported):
      {
        baseline_expiry_date,
        baselineExpiryDate,
        personalized_expiry_date,
        personalizedExpiryDate,
        final_expiry_date,
        finalExpiryDate,
        scp,
        scp_score,
        days_left,
        daysLeft,
        days_left_from_personalized,
        printed_cap_applied
      }
*/

const REGION_HUMIDITY = {
  western: 78,
  central: 82,
  southern: 80,
  northern: 70,
  eastern: 75,
  north_western: 74,
  north_central: 73,
  uva: 76,
  sabaragamuwa: 84,
};

function formatDate(value) {
  if (!value) return "—";
  return value;
}

function getFoodName(food) {
  return (
    food?.name ||
    food?.foodName ||
    food?.itemName ||
    food?.item ||
    "Food Item"
  );
}

function getFoodUserId(food) {
  return food?.userId || food?.user_id || "U001";
}

function getFoodItem(food) {
  return food?.item || food?.normalizedName || food?.food_name || "—";
}

function getFoodCategory(food) {
  return food?.category || food?.foodCategory || "—";
}

function getFoodPurchaseDate(food) {
  return food?.purchaseDate || food?.purchase_date || "—";
}

function getFoodStorage(food) {
  return food?.storage || food?.storageLocation || food?.storage_type || "—";
}

function getFoodQty(food) {
  return food?.qty || food?.quantity || 1;
}

export default function PredictExpiryModal({
  open,
  onClose,
  selectedFood,
  onPredict,
}) {
  const defaultRegion = "western";
  const defaultStorage = String(getFoodStorage(selectedFood)).toLowerCase();

  const [region, setRegion] = useState(defaultRegion);
  const [humidity, setHumidity] = useState(REGION_HUMIDITY[defaultRegion]);
  const [temperature, setTemperature] = useState(4);
  const [printedExpiryDate, setPrintedExpiryDate] = useState("");
  const [noPrintedExpiry, setNoPrintedExpiry] = useState(false);

  const [predictionLoading, setPredictionLoading] = useState(false);
  const [predictionError, setPredictionError] = useState("");
  const [predictionResult, setPredictionResult] = useState(null);
  const [showResultPopup, setShowResultPopup] = useState(false);

  useEffect(() => {
    if (!open) return;

    const regionDefault = "western";
    setRegion(regionDefault);
    setHumidity(REGION_HUMIDITY[regionDefault]);

    if (defaultStorage.includes("freezer")) {
      setTemperature(-18);
    } else if (defaultStorage.includes("fridge")) {
      setTemperature(4);
    } else {
      setTemperature(28);
    }

    setPrintedExpiryDate("");
    setNoPrintedExpiry(false);
    setPredictionLoading(false);
    setPredictionError("");
    setPredictionResult(null);
    setShowResultPopup(false);
  }, [open, defaultStorage]);

  useEffect(() => {
    setHumidity(REGION_HUMIDITY[region] ?? 78);
  }, [region]);

  useEffect(() => {
    if (!showResultPopup) return;
    const timer = setTimeout(() => {
      setShowResultPopup(false);
    }, 5000);
    return () => clearTimeout(timer);
  }, [showResultPopup]);

  const regionLabel = useMemo(() => {
    switch (region) {
      case "western":
        return "Western";
      case "central":
        return "Central";
      case "southern":
        return "Southern";
      case "northern":
        return "Northern";
      case "eastern":
        return "Eastern";
      case "north_western":
        return "North Western";
      case "north_central":
        return "North Central";
      case "uva":
        return "Uva";
      case "sabaragamuwa":
        return "Sabaragamuwa";
      default:
        return "Western";
    }
  }, [region]);

  const baselineExpiry =
    predictionResult?.baseline_expiry_date ||
    predictionResult?.baselineExpiryDate ||
    "—";

  const personalizedExpiry =
    predictionResult?.personalized_expiry_date ||
    predictionResult?.personalizedExpiryDate ||
    "—";

  const finalExpiry =
    predictionResult?.final_expiry_date ||
    predictionResult?.finalExpiryDate ||
    "—";

  const scpScore =
    predictionResult?.scp_score ?? predictionResult?.scp ?? "—";

  const daysLeft =
    predictionResult?.days_left ??
    predictionResult?.daysLeft ??
    predictionResult?.days_left_from_personalized ??
    "—";

  const handleRunPrediction = async () => {
    try {
      setPredictionLoading(true);
      setPredictionError("");
      setPredictionResult(null);
      setShowResultPopup(false);

      if (!selectedFood?._id && !selectedFood?.id) {
        throw new Error("Food item ID is missing.");
      }

      const payload = {
        foodId: selectedFood?._id || selectedFood?.id,
        region,
        storage_temperature_c: Number(temperature),
        storage_humidity_pct: Number(humidity),
        printedExpiryDate: noPrintedExpiry ? "" : printedExpiryDate,
      };

      const response = await onPredict(payload);

      setPredictionResult(response);
      setShowResultPopup(true);
    } catch (error) {
      setPredictionError(
        error?.response?.data?.message ||
          error?.message ||
          "Prediction failed. Please try again."
      );
    } finally {
      setPredictionLoading(false);
    }
  };

  if (!open) return null;

  return (
    <>
      <div className="pem-overlay" onClick={onClose} />
      <div className="pem-modal" role="dialog" aria-modal="true">
        <div className="pem-header">
          <h2>Predict Expiry</h2>
          <button className="pem-close" onClick={onClose} type="button">
            ×
          </button>
        </div>

        <div className="pem-body">
          <div className="pem-card pem-food-readonly">
            <p className="pem-muted">Stored item details (read-only)</p>
            <h3>{getFoodName(selectedFood)}</h3>
            <p>User ID: {getFoodUserId(selectedFood)}</p>
            <p>
              Item: {getFoodItem(selectedFood)} • Category:{" "}
              {getFoodCategory(selectedFood)}
            </p>
            <p>
              Purchase: {getFoodPurchaseDate(selectedFood)} • Storage:{" "}
              {getFoodStorage(selectedFood)} • Qty: {getFoodQty(selectedFood)}
            </p>
          </div>

          <div className="pem-card">
            <h3>Storage Environment (for prediction)</h3>
            <p className="pem-help">
              Select your region to apply a typical humidity value for Sri
              Lanka, and enter the storage temperature.
            </p>

            <div className="pem-grid">
              <div className="pem-field">
                <label>Region (Sri Lanka)</label>
                <select
                  value={region}
                  onChange={(e) => setRegion(e.target.value)}
                >
                  <option value="western">Western (≈ 78% humidity)</option>
                  <option value="central">Central (≈ 82% humidity)</option>
                  <option value="southern">Southern (≈ 80% humidity)</option>
                  <option value="northern">Northern (≈ 70% humidity)</option>
                  <option value="eastern">Eastern (≈ 75% humidity)</option>
                  <option value="north_western">
                    North Western (≈ 74% humidity)
                  </option>
                  <option value="north_central">
                    North Central (≈ 73% humidity)
                  </option>
                  <option value="uva">Uva (≈ 76% humidity)</option>
                  <option value="sabaragamuwa">
                    Sabaragamuwa (≈ 84% humidity)
                  </option>
                </select>
              </div>

              <div className="pem-field">
                <label>Humidity (%)</label>
                <input
                  type="number"
                  value={humidity}
                  onChange={(e) => setHumidity(e.target.value)}
                />
                <small>Auto-filled from region, but you can adjust.</small>
              </div>
            </div>

            <div className="pem-field">
              <label>Temperature (°C)</label>
              <input
                type="number"
                value={temperature}
                onChange={(e) => setTemperature(e.target.value)}
              />
              <small>
                Defaults: Pantry ≈ 28°C • Fridge ≈ 4°C • Freezer ≈ -18°C
              </small>
            </div>
          </div>

          <div className="pem-card">
            <h3>Printed Expiry Date (optional)</h3>

            <div className="pem-field">
              <input
                type="date"
                value={printedExpiryDate}
                onChange={(e) => setPrintedExpiryDate(e.target.value)}
                disabled={noPrintedExpiry}
              />
            </div>

            <label className="pem-checkbox">
              <input
                type="checkbox"
                checked={noPrintedExpiry}
                onChange={(e) => setNoPrintedExpiry(e.target.checked)}
              />
              <span>No printed expiry available</span>
            </label>
          </div>

          {predictionError && (
            <div className="pem-error-box">{predictionError}</div>
          )}
        </div>

        <div className="pem-footer">
          <button
            type="button"
            className="pem-btn pem-btn-secondary"
            onClick={onClose}
          >
            Close
          </button>
          <button
            type="button"
            className="pem-btn pem-btn-primary"
            onClick={handleRunPrediction}
            disabled={predictionLoading}
          >
            {predictionLoading ? "Running..." : "Run Prediction"}
          </button>
        </div>
      </div>

      {showResultPopup && predictionResult && (
        <div className="pem-result-overlay">
          <div className="pem-result-popup">
            <button
              className="pem-result-close"
              onClick={() => setShowResultPopup(false)}
              type="button"
            >
              ×
            </button>

            <div className="pem-result-header">
              <div className="pem-result-icon">✓</div>
              <div>
                <h3>Prediction Completed</h3>
                <p>Your expiry result is ready</p>
              </div>
            </div>

            <div className="pem-result-content">
              <div className="pem-result-env">
                <span>Environment used</span>
                <strong>
                  {regionLabel} • {temperature}°C • {humidity}%
                </strong>
              </div>

              <div className="pem-result-row">
                <span>Final Expiry</span>
                <strong className="pem-highlight">
                  {formatDate(finalExpiry)}
                </strong>
              </div>

              <div className="pem-result-row">
                <span>Baseline Expiry</span>
                <strong>{formatDate(baselineExpiry)}</strong>
              </div>

              <div className="pem-result-row">
                <span>Personalized Expiry</span>
                <strong>{formatDate(personalizedExpiry)}</strong>
              </div>

              <div className="pem-result-row">
                <span>Days Left</span>
                <strong>{daysLeft}</strong>
              </div>

              <div className="pem-result-row">
                <span>SCP Score</span>
                <strong>{scpScore}</strong>
              </div>

              <div className="pem-result-row">
                <span>Printed Cap Applied</span>
                <strong>
                  {predictionResult?.printed_cap_applied ? "Yes" : "No"}
                </strong>
              </div>
            </div>

            <div className="pem-result-actions">
              <button
                type="button"
                className="pem-btn pem-btn-secondary"
                onClick={() => setShowResultPopup(false)}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}