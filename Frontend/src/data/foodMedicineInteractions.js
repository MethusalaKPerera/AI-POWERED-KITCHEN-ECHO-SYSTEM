export const MED_CATEGORIES = [
  "Anticoagulant (Blood thinner)",
  "Antibiotic",
  "Antidiabetic",
  "Antihypertensive",
  "Statin (Cholesterol)",
  "Thyroid",
  "NSAID (Pain relief)",
  "Diuretic",

  // ✅ New categories
  "Antidepressant (MAOI/SSRI)",
  "Cardiac (Digoxin)",
  "Mood stabilizer (Lithium)",
  "TB Medication",
];

export const CONDITION_TAGS = [
  "diabetes",
  "hypertension",
  "heart_disease",
  "kidney_disease",
  "thyroid_disorder",
  "high_cholesterol",
  "gastritis_ulcer",

  // ✅ new common tags
  "depression_anxiety",
  "tb",
];

export const FOOD_MED_INTERACTIONS = [
  // EXISTING (8)
  {
    id: "MED001",
    medicine: "Warfarin",
    category: "Anticoagulant (Blood thinner)",
    aliases: ["blood thinner", "vitamin K interaction"],
    severity: "high",
    conditions: ["heart_disease"],
    avoidFoods: ["Sudden large changes of leafy greens (very high Vitamin K)"],
    limitFoods: ["Kale", "Spinach", "Gotukola", "Mukunuwenna", "Broccoli"],
    preferFoods: ["Keep Vitamin K intake consistent", "Balanced meals"],
    timingAdvice:
      "Keep daily Vitamin K intake stable; do not suddenly increase/decrease greens.",
    notes:
      "Vitamin K affects warfarin activity. The key is consistency, not fully avoiding greens.",
  },

  {
    id: "MED002",
    medicine: "Metformin",
    category: "Antidiabetic",
    aliases: ["type 2 diabetes medication"],
    severity: "medium",
    conditions: ["diabetes"],
    avoidFoods: ["Excess alcohol"],
    limitFoods: ["Sugary drinks", "Refined carbs (white bread, sweets)"],
    preferFoods: [
      "High-fiber foods",
      "Vegetables",
      "Whole grains",
      "Lean protein",
    ],
    timingAdvice: "Take with meals to reduce stomach upset.",
    notes:
      "Alcohol increases risk of lactic acidosis and can worsen blood sugar control.",
  },

  {
    id: "MED003",
    medicine: "Statins (e.g., Atorvastatin, Simvastatin)",
    category: "Statin (Cholesterol)",
    aliases: ["atorvastatin", "simvastatin", "cholesterol tablet"],
    severity: "high",
    conditions: ["high_cholesterol", "heart_disease"],
    avoidFoods: ["Grapefruit / grapefruit juice"],
    limitFoods: ["Very high-fat fried foods"],
    preferFoods: [
      "Oats",
      "Fruits (non-grapefruit)",
      "Vegetables",
      "Omega-3 sources",
    ],
    timingAdvice:
      "Avoid grapefruit; it can increase statin levels and side effects.",
    notes:
      "Grapefruit can inhibit metabolism (CYP3A4) causing higher statin concentration.",
  },

  {
    id: "MED004",
    medicine: "ACE inhibitors (e.g., Enalapril, Lisinopril)",
    category: "Antihypertensive",
    aliases: ["enalapril", "lisinopril", "blood pressure tablet"],
    severity: "medium",
    conditions: ["hypertension", "heart_disease"],
    avoidFoods: ["Salt substitutes high in potassium (if advised by doctor)"],
    limitFoods: ["Very high potassium foods in excess (if potassium tends to be high)"],
    preferFoods: [
      "Low-salt meals",
      "Fruits/veg (balanced potassium)",
      "Adequate water",
    ],
    timingAdvice: "Monitor potassium if your doctor requested it.",
    notes:
      "ACE inhibitors may increase potassium in some people; avoid unnecessary potassium overload.",
  },

  {
    id: "MED005",
    medicine: "Levothyroxine",
    category: "Thyroid",
    aliases: ["thyroid tablet", "thyroxine"],
    severity: "high",
    conditions: ["thyroid_disorder"],
    avoidFoods: ["Taking with soy, calcium/iron supplements at the same time"],
    limitFoods: ["Soy-based meals close to dose", "High-fiber immediately after dose"],
    preferFoods: ["Take on empty stomach with water"],
    timingAdvice:
      "Take 30–60 min before breakfast; separate calcium/iron by 4 hours.",
    notes:
      "Food and minerals reduce absorption. Timing is the main issue, not banning foods entirely.",
  },

  {
    id: "MED006",
    medicine: "Tetracycline antibiotics (e.g., Doxycycline)",
    category: "Antibiotic",
    aliases: ["doxycycline", "tetracycline"],
    severity: "high",
    conditions: [],
    avoidFoods: ["Milk, yogurt, cheese close to dose"],
    limitFoods: ["Calcium-fortified drinks near dose"],
    preferFoods: ["Take with water; light meal if stomach upset (no dairy)"],
    timingAdvice: "Separate dairy/calcium by 2–3 hours from the dose.",
    notes: "Calcium binds the antibiotic and reduces absorption.",
  },

  {
    id: "MED007",
    medicine: "NSAIDs (e.g., Ibuprofen, Diclofenac)",
    category: "NSAID (Pain relief)",
    aliases: ["ibuprofen", "diclofenac", "painkiller"],
    severity: "medium",
    conditions: ["gastritis_ulcer"],
    avoidFoods: ["Alcohol"],
    limitFoods: ["Very spicy foods (if gastritis)", "Excess coffee"],
    preferFoods: ["Take with food", "Bland meals if stomach sensitive"],
    timingAdvice: "Take after meals to reduce gastric irritation (as advised).",
    notes:
      "NSAIDs can irritate the stomach lining; food reduces discomfort for many people.",
  },

  {
    id: "MED008",
    medicine: "Diuretics (e.g., Furosemide)",
    category: "Diuretic",
    aliases: ["water pill", "furosemide"],
    severity: "low",
    conditions: ["heart_disease", "hypertension", "kidney_disease"],
    avoidFoods: ["Excess licorice"],
    limitFoods: ["Very salty foods", "Processed foods with high sodium", "Canned soups"],
    preferFoods: ["Adequate hydration", "Doctor-advised electrolyte balance"],
    timingAdvice:
      "Take earlier in the day to reduce night urination (if doctor agrees).",
    notes:
      "Salt increases fluid retention; hydration/electrolytes depend on your clinical advice.",
  },

  // NEW (8)
  {
    id: "MED009",
    medicine: "MAOI antidepressants (e.g., Phenelzine, Tranylcypromine)",
    category: "Antidepressant (MAOI/SSRI)",
    aliases: ["MAOI", "phenelzine", "tranylcypromine"],
    severity: "high",
    conditions: ["depression_anxiety"],
    avoidFoods: ["Aged cheese", "Fermented foods", "Cured meats", "Soy sauce"],
    limitFoods: ["Overripe bananas", "Alcohol (especially tap beer/wine)"],
    preferFoods: ["Fresh foods", "Balanced meals"],
    timingAdvice:
      "Strictly avoid high-tyramine foods while on MAOIs to prevent dangerous BP spikes.",
    notes:
      "High-tyramine foods can trigger hypertensive crisis with MAOI antidepressants.",
  },

  {
    id: "MED010",
    medicine: "SSRIs (e.g., Sertraline, Fluoxetine)",
    category: "Antidepressant (MAOI/SSRI)",
    aliases: ["SSRI", "sertraline", "fluoxetine", "antidepressant"],
    severity: "medium",
    conditions: ["depression_anxiety"],
    avoidFoods: ["Alcohol (can worsen drowsiness and mood symptoms)"],
    limitFoods: ["High caffeine if anxiety worsens", "Grapefruit only if specifically advised for some SSRIs"],
    preferFoods: ["Regular meals", "Hydration", "Balanced diet"],
    timingAdvice: "Take consistently at the same time daily.",
    notes:
      "Alcohol can worsen side effects and reduce symptom control. Dietary issues are usually supportive rather than strict restrictions.",
  },

  {
    id: "MED011",
    medicine: "Metronidazole",
    category: "Antibiotic",
    aliases: ["flagyl", "metronidazole"],
    severity: "high",
    conditions: [],
    avoidFoods: ["Alcohol (including some cough syrups / fermented drinks)"],
    limitFoods: ["Very spicy foods (if stomach upset)", "Excess caffeine"],
    preferFoods: ["Take with food if nausea occurs", "Hydration"],
    timingAdvice: "Avoid alcohol during treatment and for 48–72 hours after the last dose.",
    notes:
      "Alcohol can cause a strong reaction (flushing, nausea, vomiting, headache) with metronidazole.",
  },

  {
    id: "MED012",
    medicine: "Fluoroquinolone antibiotics (e.g., Ciprofloxacin, Levofloxacin)",
    category: "Antibiotic",
    aliases: ["ciprofloxacin", "levofloxacin", "quinolone"],
    severity: "medium",
    conditions: [],
    avoidFoods: ["Taking with dairy at the same time"],
    limitFoods: ["Calcium/iron/zinc supplements near dose"],
    preferFoods: ["Take with water", "Light meal if needed (no dairy)"],
    timingAdvice: "Separate dairy/minerals by 2–4 hours from the dose.",
    notes:
      "Dairy and minerals can reduce absorption and lower antibiotic effectiveness.",
  },

  {
    id: "MED013",
    medicine: "Spironolactone",
    category: "Diuretic",
    aliases: ["potassium-sparing diuretic", "spironolactone"],
    severity: "high",
    conditions: ["heart_disease", "hypertension", "kidney_disease"],
    avoidFoods: ["Salt substitutes high in potassium"],
    limitFoods: ["Excess bananas", "Coconut water", "Very high potassium foods in large amounts"],
    preferFoods: ["Low-salt meals", "Doctor-advised potassium monitoring"],
    timingAdvice: "Avoid unnecessary potassium overload unless your doctor says otherwise.",
    notes:
      "Spironolactone can raise potassium levels. Too much potassium can be dangerous in some patients.",
  },

  {
    id: "MED014",
    medicine: "Digoxin",
    category: "Cardiac (Digoxin)",
    aliases: ["digitalis", "digoxin"],
    severity: "medium",
    conditions: ["heart_disease"],
    avoidFoods: ["Licorice", "Grapefruit"],
    limitFoods: ["Very high-fiber/bran immediately around dose"],
    preferFoods: ["Consistent meals", "Adequate potassium as clinically advised"],
    timingAdvice: "If high-fiber meals reduce effect, take digoxin at a consistent time away from heavy bran meals.",
    notes:
      "Very high-fiber foods can reduce absorption in some people. Electrolyte balance is important for digoxin safety.",
  },

  {
    id: "MED015",
    medicine: "Lithium",
    category: "Mood stabilizer (Lithium)",
    aliases: ["lithium carbonate", "mood stabilizer"],
    severity: "high",
    conditions: ["depression_anxiety"],
    avoidFoods: ["Sudden changes in sodium intake", "NSAIDs (ibuprofen, naproxen)"],
    limitFoods: ["High sodium foods (salt, salty snacks)", "Excess caffeine", "Excess sugar"],
    preferFoods: ["Consistent salt intake", "Adequate water daily"],
    timingAdvice:
      "Keep salt and fluid intake consistent; dehydration can raise lithium levels.",
    notes:
      "Lithium levels are sensitive to hydration and sodium balance. Dehydration increases toxicity risk.",
  },

  {
    id: "MED016",
    medicine: "Isoniazid (TB medication)",
    category: "TB Medication",
    aliases: ["isoniazid", "INH", "tuberculosis medicine"],
    severity: "medium",
    conditions: ["tb"],
    avoidFoods: ["Certain aged/fermented foods (tyramine/histamine) if advised"],
    limitFoods: ["Aged cheese", "Cured meats", "Some fish (histamine-rich)"],
    preferFoods: ["Balanced meals", "Vitamin B6 supplementation if prescribed"],
    timingAdvice: "Take as instructed; food timing depends on GI tolerance and clinician advice.",
    notes:
      "Some people experience reactions with tyramine/histamine foods. Clinicians often prescribe Vitamin B6 to reduce neuropathy risk.",
  },
];
