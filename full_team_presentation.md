
# AI-Powered Kitchen Echo-System: Complete PP1 Setup (4 Members)

This implementation guide covers the requirements for all 4 team members for the "Progress Presentation 1" (PP1).

---

## TEAM SLIDE: Overall Project Title
**Project Title:** AI-Powered Kitchen Echo-System
*   **Problem:** 
    *   30% of household food is wasted.
    *   Families struggle with "Decision Fatigue" (What to cook?) and disconnected systems (Recipe Apps vs. Shopping Apps vs. Health Apps).
*   **Target Group:** Urban Families & Busy Professionals.
*   **Design Excellence:**
    *   A Unified Central Dashboard connecting 4 specialized AI agents.
    *   Cross-module data flow (Expiry $\rightarrow$ Cooking; Health $\rightarrow$ Shopping).
*   **Video:** *[Insert 2-minute Montage of all 4 modules]*

---

## MEMBER 1: Smart Shopping Assistant (Completed)
**Student Name:** [Your Name]
**Component:** "Intelligent Predictive Shopping Agent"

**1. Technical Solution (Slide 9a):**
*   **Problem:** Users forget items or buy impulsively.
*   **Solution:** An AI that *predicts* your grocery list based on habits before you even type.
*   **Requirements:**
    *   **Latency:** <2s prediction.
    *   **Adaptability:** Detects dietary shifts (Normal $\rightarrow$ Vegan).
    *   **Context:** Weekday vs Weekend patterns.

**2. Design Excellence (Slide 9b):**
*   **Architecture:** **Hybrid AI Architecture**.
    *   *Mechanism:* Local "User Weight Profile" training (Python) + Cloud Inference (Gemini).
    *   *Benefit:* Privacy-first, offline-capable personalization.
*   **User Feedback:** "The 'Zero-Click' shopping list reduced planning time by 40%."

**3. Commercialization (Slide 10):**
*   **Model:** Freemium (Basic Search free) + Subscription for "AI Forecast" features ($4.99/mo).

---

## MEMBER 2: AI Cooking Assistant
**Student Name:** [Member 2 Name]
**Component:** "Visual Ingredient Recognition & Recipe Generation Agent"

**1. Technical Solution (Slide 9a):**
*   **Problem:** Users have ingredients but don't know what to cook ("Fridge Blindness").
*   **Solution:** A Computer Vision module that identifies raw ingredients from photos and generates recipes.
*   **Requirements:**
    *   **Recognition Accuracy:** >90% for common vegetables.
    *   **Cuisine Focus:** Specifically trained on **Sri Lankan Cuisine** (Curries, Spices).

**2. Design Excellence (Slide 9b):**
*   **Technical Novelty:** **Custom Fine-Tuned Vision Pipeline**.
    *   *Implementation:* Uses a specialized model prompt to recognize specific Asian vegetables (e.g., Kohleria, Snake Gourd) that generic models miss.
*   **UX Design:** "One-Tap-Cook" interface – Take visual ingredients $\rightarrow$ Direct Recipe Card.

**3. Commercialization (Slide 10):**
*   **Partnerships:** Integration with local Supermarket chains (e.g., Keells) to "Order Missing Ingredients".

---

## MEMBER 3: Food Expiry & Inventory Manager
**Student Name:** [Member 3 Name]
**Component:** "Smart Inventory Tracker & Waste Reduction Engine"

**1. Technical Solution (Slide 9a):**
*   **Problem:** Food goes bad because users forget it's in the fridge.
*   **Solution:** An automated expiry tracker with "Smart Notifications".
*   **Requirements:**
    *   **Automation:** Auto-calculate shelf life (e.g., "Milk = 7 days").
    *   **Alerts:** Push notifications 2 days before expiry.

**2. Design Excellence (Slide 9b):**
*   **Algorithmic Contribution:** **"Expiry Logic Engine"**.
    *   *Mechanism:* Doesn't just rely on static dates; adjusts based on storage method (Freezer vs Fridge logic).
*   **Integration:** If food is expiring, it **auto-triggers** the "Cooking Assistant" to suggest a recipe *using that specific item*.

**3. Commercialization (Slide 10):**
*   **Sustainability Metric:** Users save ~$400/year on wasted food, justifying a premium app cost.

---

## MEMBER 4: Nutritional Guidance
**Student Name:** [Member 4 Name]
**Component:** "Personalized AI Nutrition Coach & Health Analytics"

**1. Technical Solution (Slide 9a):**
*   **Problem:** Generic diet apps don't account for complex health conditions (Diabetes + Cholesterol).
*   **Solution:** An AI Coach that monitors meals and medication.
*   **Requirements:**
    *   **Safety:** Conflict detection (Food vs Medication interactions).
    *   **Analysis:** Real-time macro/micronutrient breakdown.

**2. Design Excellence (Slide 9b):**
*   **Technical Safety:** **"RAG-Based Health Guard"**.
    *   *Architecture:* Retrieval-Augmented Generation ensures advice is strictly based on verified medical guidelines, minimizing AI hallucinations.
*   **UX:** Visual "Health Score" dashboard that updates daily.

**3. Commercialization (Slide 10):**
*   **Healthcare B2B:** Potential API licensing to insurance companies for user health tracking.

---

## DEMO DAY CHECKLIST (Slide 4 Avoidance)

1.  **Shopping:** Open Dashboard -> Show "AI Forecast" (Wait 2s for reload).
2.  **Cooking:** Open "AI Cooking" -> Upload `vegetable_basket.jpg` -> Show Recipe.
3.  **Expiry:** Show "Inventory List" -> Highlight "Milk (Expiring Tomorrow)" -> Click "Cook Now".
4.  **Nutrition:** Show "Health Dashboard" -> Logs a meal -> Updates "Calorie Graph" instantly.

**Tech Stack (All Members):**
*   **Frontend:** React + Tailwind CSS (Unified UI Theme).
*   **Backend:** Python Flask (Microservices architecture).
*   **AI:** Google Gemini 1.5 Flash + Custom Local Logic.
