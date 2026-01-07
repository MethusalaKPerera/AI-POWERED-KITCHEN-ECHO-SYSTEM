
import React, { useEffect, useState } from 'react';
import { Sun, Coffee, Moon, Utensils, Loader2 } from 'lucide-react';

export function MealForecast() {
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [nextMeal, setNextMeal] = useState('');

  useEffect(() => {
    const fetchPrediction = async () => {
      const token = localStorage.getItem('token');
      if (!token) {
        setLoading(false);
        return;
      }

      try {
        const res = await fetch('http://localhost:5000/api/shopping/predict-needs', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        const data = await res.json();
        if (data.success && data.prediction) {
          setPrediction(data.prediction);
        } else {
             // Handle empty/new user case
             setError("Start searching to get AI predictions!");
        }
      } catch (err) {
        console.error(err);
        setError("AI Service unavailable.");
      } finally {
        setLoading(false);
      }
    };

    fetchPrediction();

    // Determine next meal based on time
    const hour = new Date().getHours();
    if (hour < 11) setNextMeal('breakfast');
    else if (hour < 16) setNextMeal('lunch');
    else setNextMeal('dinner');

  }, []);

  if (loading) return (
    <div className="flex items-center justify-center p-8 bg-white/50 rounded-xl mt-8">
      <Loader2 className="animate-spin text-[#2D9B81]" />
      <span className="ml-2 text-[#2D5F4F]">AI is analyzing your taste...</span>
    </div>
  );

  if (!prediction) return null; // Don't show if not logged in

  const plan = prediction.meal_plan || { breakfast: "N/A", lunch: "N/A", dinner: "N/A" };

  return (
    <div className="w-full max-w-5xl mx-auto mt-12 mb-12">
      <div className="bg-gradient-to-r from-[#1E5245] to-[#2D9B81] rounded-2xl p-1 shadow-xl overflow-hidden">
        <div className="bg-white rounded-xl p-8">
            
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6">
            <div>
              <div className="flex items-center space-x-2 text-[#2D9B81] font-semibold mb-1">
                 <Utensils size={20} />
                 <span className="uppercase tracking-wider text-sm">AI Daily Forecast</span>
              </div>
              <h2 className="text-2xl font-bold text-gray-800">Tomorrow's Dynamic Meal Plan</h2>
              <p className="text-gray-500 text-sm mt-1">{prediction.reasoning}</p>
            </div>
            
            <div className="mt-4 md:mt-0 flex items-center space-x-2 bg-green-50 px-4 py-2 rounded-lg border border-green-100">
               <span className="text-green-700 font-medium text-sm">Top Preference:</span>
               <span className="text-green-800 font-bold">{prediction.preferences ? prediction.preferences[0] : 'Food'}</span>
            </div>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            <MealCard 
                icon={Coffee} 
                title="Breakfast" 
                meal={plan.breakfast} 
                active={nextMeal === 'breakfast' || true} // Always show all, maybe highlight?
                highlight={nextMeal === 'breakfast'}
            />
             <MealCard 
                icon={Sun} 
                title="Lunch" 
                meal={plan.lunch} 
                active={true}
                highlight={nextMeal === 'lunch'}
            />
             <MealCard 
                icon={Moon} 
                title="Dinner" 
                meal={plan.dinner} 
                active={true}
                highlight={nextMeal === 'dinner'}
            />
          </div>
          
        </div>
      </div>
    </div>
  );
}

function MealCard({ icon: Icon, title, meal, highlight }) {
  return (
    <div className={`relative p-6 rounded-xl border transition-all duration-300 ${highlight ? 'bg-[#F0FDFA] border-[#2D9B81] shadow-md scale-105 ring-2 ring-[#2D9B81]/20' : 'bg-gray-50 border-gray-100 hover:border-[#2D9B81]/50'}`}>
       {highlight && (
           <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-[#2D9B81] text-white text-[10px] uppercase font-bold px-3 py-1 rounded-full">
               Next Up
           </div>
       )}
       <div className={`w-12 h-12 rounded-full flex items-center justify-center mb-4 ${highlight ? 'bg-[#2D9B81] text-white' : 'bg-white text-gray-400'}`}>
          <Icon size={24} />
       </div>
       <h3 className={`text-lg font-semibold mb-2 ${highlight ? 'text-[#1E5245]' : 'text-gray-600'}`}>{title}</h3>
       <p className={`text-sm leading-relaxed ${highlight ? 'text-gray-800 font-medium' : 'text-gray-500'}`}>{meal}</p>
    </div>
  );
}
