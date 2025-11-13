import React from "react";
import {
  LayoutDashboard,
  User,
  BarChart3,
  Brain,
  AlertCircle,
  Settings,
  UtensilsCrossed,
} from "lucide-react";

function Sidebar({ activeTab, setActiveTab }) {
  const navItems = [
    { id: "dashboard", icon: LayoutDashboard, label: "Dashboard" },
    { id: "profile", icon: User, label: "User Profile" },
    { id: "meal-logger", icon: UtensilsCrossed, label: "Meal Logger" },
    { id: "nutrition-tracker", icon: BarChart3, label: "Nutrition Tracker" },
    { id: "medication-alerts", icon: AlertCircle, label: "Medication Alerts" },
    { id: "predictive-analytics", icon: Brain, label: "Predictive Analytics" },
    { id: "settings", icon: Settings, label: "Settings" },
  ];

  return (
    <div className="w-64 h-screen sticky top-0 bg-gradient-to-b from-[#164e3b] via-[#1fa37e] to-[#1fa37e] text-white flex flex-col shadow-2xl">
      <div className="p-8 border-b border-white border-opacity-10 text-center">
        <h2 className="text-2xl font-bold mb-1">Nutrition</h2>
        <p className="text-xs opacity-80">AI Health Guide</p>
      </div>
      <nav className="flex-1 py-6 px-4 space-y-2 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center gap-4 px-6 py-3 rounded-lg transition-all text-left text-sm ${
                isActive
                  ? "bg-white bg-opacity-20 border-l-4 border-white shadow-lg font-semibold"
                  : "hover:bg-white hover:bg-opacity-10"
              }`}
            >
              <Icon size={20} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>
      <div className="p-6 border-t border-white border-opacity-10 text-xs text-center opacity-90">
        <p>© 2025 Nutrition AI</p>
      </div>
    </div>
  );
}

export default Sidebar;
