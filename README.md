# AI-Powered Kitchen Ecosystem

### Topic: AI-Powered Kitchen Ecosystem for Food Waste Reduction and Nutrition Optimization
### Main Research Domain: CoEAI - Centre of Excellence for AI
### Project ID: 25-26J-351
### Repo Link: https://github.com/MethusalaKPerera/AI-POWERED-KITCHEN-ECHO-SYSTEM.git

**AI-Powered Kitchen Ecosystem** is a full-stack, research-driven platform designed to **reduce household food waste** and **optimize nutrition** by supporting the complete food lifecycle—from planning and purchasing to cooking, consumption, and waste reduction. 

This ecosystem integrates **four intelligent modules** working together in a single workflow:

1. **Spontaneous Cooking Assistant** (Computer Vision + Recipe Discovery)
2. **Nutrition Guidance – Predictive Health Intervention System** (ML-based deficiency forecasting + personalized guidance)
3. **AI Shopping Agent** (Voice-enabled product search + cross-platform price comparison)
4. **Behavioral Food Expiry Predictor** (Personalized spoilage/expiry prediction using user behavior feedback)

## 📌 Project Overview

Many existing food-tech applications solve problems in isolation (only recipes, only calorie counting, only shopping lists, only expiry reminders). This project unifies these areas into a **single AI-powered ecosystem** that:

- Maximizes ingredient utilization to reduce food waste
- Provides proactive nutrition guidance (not just reactive summaries)
- Supports smarter household purchasing decisions
- Learns from user habits to continuously improve predictions and recommendations

## ❗ Research Problem

Households face two interconnected challenges:

- **Food Waste:** Items are forgotten, stored incorrectly, or used too late.
- **Poor Nutrition:** People track calories but often miss long-term micro-nutrient imbalance risks.

Most current solutions are **fragmented**, lack **personalization**, and do not provide **end-to-end support** across the food lifecycle. This research addresses that gap by building an integrated, adaptive smart kitchen platform powered by AI.


## 🎯 Research Objectives

### Main Objective
To develop an **AI-powered smart kitchen ecosystem** that reduces household food waste, improves nutrition outcomes, and enhances cooking experiences through integrated AI modules, personalization, and adaptive feedback mechanisms.

### Sub-Objectives (Module-Level)
- Recognize multiple ingredients from a single image and recommend recipes for spontaneous cooking.
- Predict micro-nutrient deficiency risk **2–weeks in advance** and provide personalized nutrition interventions.
- Provide voice-enabled smart shopping with recommendation, comparison, and search history personalization.
- Predict food expiry/spoilage dynamically using user habits, storage patterns, and feedback loops.

## 🏗️ System Architecture

The ecosystem follows a **modular architecture**, where each module exposes REST APIs and integrates through the main frontend experience.

<p align="center">
  <img src="docs/architecture.png" width="750" alt="AI-Powered Kitchen Ecosystem Architecture">
</p>

<p align="center">
  <em>Figure 1: High-level architecture of the AI-Powered Kitchen Ecosystem</em>
</p>


🧩 Core Modules
1️. Spontaneous Cooking Assistant

Goal: Turn a photo of available ingredients into recipe suggestions.

Key Features :

Multi-item ingredient recognition (single photo → multiple detected items)

Confidence scoring + user correction workflow

Recipe matching and ranking based on ingredient overlap

Missing ingredient hints and substitution suggestions

Tech Focus

Computer Vision + ingredient-to-recipe retrieval

Efficient indexing/caching for fast recipe search

2️. Nutrition Guidance – Predictive Health Intervention System (Your Component)

Goal: Transform diet tracking into proactive health intervention.

Key Innovations

Predictive Health AI Engine: forecasts micro-nutrient deficiency risk 2 weeks ahead using dietary patterns + lifestyle signals.

Chrono/Circadian Nutrition Optimization: aligns meal suggestions with the user’s biological rhythm, work schedule, and sleep cycle.

Goal-Based Nutrition Engine: recommends meals/snacks for goals like weight loss, muscle gain, energy support, and recovery.

Medication–Food Interaction Alerts: warns users about potentially harmful interactions for safer nutrition management.

Interactive Feedback Loop: nudges, progress tracking, and habit-building adaptation over time.

Outputs

Weekly/Monthly nutrient summaries

Deficiency risk insights (early warnings)

Personalized recommendations + nudges

Safety alerts (medication-food)


3. AI Shopping Agent

Goal: Make shopping smarter, faster, and hands-free.

Key Features

Voice-based search for hands-free kitchen usage

NLP intent understanding for smarter product matches

Cross-platform price comparison and currency conversion

Search history management (save/view/update/delete)

Context-aware assistant to guide shopping decisions

4. Behavioral Food Expiry Predictor

Goal: Reduce waste using personalized expiry estimates.

Key Features

Learns from purchase date, storage type, and user habits

Predicts expiry/spoilage dynamically (not just label-based)

Feedback-based refinement (user confirms/corrects)

Alerts and reminders for items nearing expiry

Waste analytics dashboard

## 👥 Team Members & Responsibilities

| Name                    | Registration No  |        Responsibility                                   |
| -----------------       | ---------------  | --------------------------------------------------------|
| Methusala U.M.K.        | IT22131942       | Multi-Item Food Recognition and Recipe Discovery System |
| Shahmi M T M            | IT22083982       | Predictive Health Intervention System                   |
| D.H Jayasundara         | IT22117946       | Intelligent E-Commerce Recommendation System            |
| Muraleswaran D          | IT22339010       | Personalized Expiry Prediction System                   |

---

## 👨‍🏫 Supervision

* **Supervisor:** Ms. Lokesha Weerasinghe 
* **Co-Supervisor:** Ms. Chathurya Kumarapperuma

---
## 🛠️ Technical Stack

### Backend 
- **Framework**: Flask (Python)
- **Database**: MongoDB (via Flask-PyMongo)
- **AI/ML**: Scikit-learn, Pandas, NumPy, Google Gemini (LLM Integration)
- **API Integration**: DuckDuckgo Search, Beautiful Soup, multi-site product APIs
- **Security**: Flask-Bcrypt, Flask-JWT-Extended

### Frontend
- **Library**: React.js (Vite)
- **Styling**: Tailwind CSS, Framer Motion (for animations)
- **Icons**: Lucide React, React Icons
- **State Management**: React Context API

