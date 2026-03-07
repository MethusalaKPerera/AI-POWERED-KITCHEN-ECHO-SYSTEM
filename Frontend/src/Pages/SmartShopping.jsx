import React from "react";
import { App } from "./SmartShoppingApp/App";

// Wrapper so Smart Shopping layout and sidebar align with reference UI
export default function SmartShoppingPage() {
  return (
    <div className="min-h-screen bg-[#E8F8F3]">
      <App />
    </div>
  );
}
