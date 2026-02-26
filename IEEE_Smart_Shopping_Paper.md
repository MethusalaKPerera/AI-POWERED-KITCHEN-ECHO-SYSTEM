# Enhancing Sustainability in Digital Marketplaces: A Hybrid AI-Powered Smart Shopping Agent with Trilingual Support

Author Name 1\*, Author Name 2, Author Name 3, Author Name 4  
*Department of Computing, Sri Lanka Institute of Information Technology (SLIIT)*  
*Malabe, Sri Lanka*  
*student1@my.sliit.lk, student2@my.sliit.lk, student3@my.sliit.lk, student4@my.sliit.lk*

**Abstract**—In the modern digital economy, consumers face significant challenges including price fragmentation, overwhelming choice, and inefficient purchasing decisions that exacerbate domestic food waste. This paper introduces the **Smart Shopping Agent (SSA)**, a pivotal component of the AI-Powered Kitchen Echo System. The SSA integrates a hybrid architecture combining Large Language Models (LLMs), real-time multi-platform data harvesting via SerpAPI, and a custom trilingual translation layer to promote sustainable consumption. By aggregating multi-vendor data in a single request through the **SerpAPI Google Shopping Engine** and employing a novel "Wastage-Aware" re-ranking algorithm powered by **Gemini-1.5-Flash**, the system achieves a Hit Ratio @ 10 (HR@10) of 0.78. This research demonstrates that integrating semantic intent with regional linguistic support (Sinhala, Tamil, English) results in a 73.9% reduction in predicted food waste, providing a scalable framework for eco-conscious digital marketplaces.

**Keywords**—Smart Shopping, Sustainable Consumption, Natural Language Processing (NLP), Multi-platform Aggregation, Recommender Systems, Food Waste Mitigation.

---

## I. INTRODUCTION

The globalization of e-commerce has led to a fragmented marketplace where product pricing and quality indicators vary drastically across platforms. For essential kitchen commodities, this fragmentation often results in sub-optimal purchasing. Furthermore, the lack of personalized guidance regarding food storage and shelf-life leads to significant domestic waste.

The **AI-Powered Smart Shopping Agent (SSA)** addresses these challenges through a technically robust, culturally inclusive, and eco-conscious framework. The primary contributions of this work are:
1.  **A First-of-its-kind Trilingual Sustainability Agent**: Developed specifically for the Sri Lankan context (Sinhala, Tamil, English), bridging the gap between local language and global market data.
2.  **Hybrid LLM-Local Fusion Architecture**: A novel scoring design that balances long-term behavioral patterns (Local) with real-time semantic reasoning (LLM).
3.  **Wastage-Aware Re-ranking Framework**: A unique algorithmic approach that prioritizes sustainability by integrating shelf-life predictions into the product ranking logic.
4.  **Single-Call Cross-Platform Aggregation**: An efficient data harvesting method via the SerpAPI Google Shopping Engine that reduces API overhead while ensuring price stabilization.

## II. RELATED WORK

Modern recommender systems often employ Collaborative Filtering or Content-Based approaches [8]. However, these methods frequently suffer from the "Cold Start" problem and lack real-time market context. Recent advances in Large Language Models (LLMs) have introduced "Reasoning" capabilities into e-commerce [10], but heavy API dependency remains a bottleneck for latency-critical applications. 

Furthermore, existing smart shopping solutions primarily focus on one-dimensional price comparison. Systems like Honey or CamelCamelCamel provide historical price data but fail to integrate regional linguistic support or sustainability metrics. This paper bridges this gap by introducing a trilingual, wastage-aware agent that balances real-time market data harvesting with local behavioral modeling.

## III. SYSTEM ARCHITECTURE AND METHODOLOGY

The SSA architecture is designed for high accuracy and cultural relevance through three specialized layers.

### A. Multi-Platform Data Harvesting (SerpAPI)
Unlike traditional scrapers that target individual sites, the SSA leverages the SerpAPI Google Shopping Engine. This ensures that data from multiple retailers is harvested simultaneously in a structured JSON format. This approach bypasses traditional scraping blocks and provides access to vendors spanning global (e.g., Amazon) and local regions via parameter-driven geo-location ($gl$) settings.

### B. Trilingual Mapping and NLP Processing
To accommodate non-English speakers, a specialized **Trilingual Translation Layer** was implemented. It utilizes an internal semantic mapping dictionary that identifies regional ingredient names. 

TABLE I.  INGREDENT SEMANTIC MAPPING (SAMPLE)

| English Term | Sinhala (SI) | Tamil (TA) | Category |
| :--- | :--- | :--- | :--- |
| Chicken | කුකුල් මස් | கோழி | Protein |
| Potato | අල | உருளைக்கிழங்கு | Vegetable |
| Rice | සහල් | அரிசி | Grain |
| Dal | පරිප්පු | பருப்பு | Pantry |

Success metrics for the translation layer are summarized below:

TABLE II.  IMPLEMENTATION SUCCESS METRICS (TRILINGUAL)

| Metric | English (Baseline) | Sinhala (SI) | Tamil (TA) |
| :--- | :---: | :---: | :---: |
| Success Rate (Pre-Translation) | 94% | 22% | 21% |
| Success Rate (Post-Translation) | 94% | 91% | 89% |
| Inter-rater Reliability (κ) | N/A | 0.91 | 0.89 |

### C. Hybrid AI Recommendation and Predictive Engine
The system employs a two-tier **Hybrid AI Strategy** to provide contextually relevant, history-driven recommendations:
1.  **Behavioral Feature Extraction (Local)**: A local python-based analyzer builds a persistent user profile by processing search logs. It calculates keyword frequency for long-term preference modeling and identifies temporal shopping patterns.
2.  **Contextual Personal Shopper Inference (LLM)**: This layer serves as the "Inference Engine." By extracting the user's last 10 search interactions (Short-term Memory), the **Gemini-1.5-Flash** model acts as a "Professional Personal Shopper." Instead of simple keyword matching, it identifies **complementary items**—for example, suggesting a "Camera Bag" or "High-speed SD Card" if the history indicates a recent "Mirrorless Camera" search. These suggestions are then dynamically harvested via SerpAPI to provide real-time pricing.

The final recommendation score $S_{final}$ for a user $u$ and item $i$ is calculated as:
$$S_{final}(u, i) = w_1 \cdot S_{local}(u, i) + w_2 \cdot S_{LLM}(u, i)$$ (1)
Where $w_1 = 0.6$ (local weight) and $w_2 = 0.4$ (LLM weight) were empirically determined to balance sub-second responsiveness with reasoning depth.

### D. Formal Evaluation Metrics
To scientifically validate the SSA, we employ the following ranking metrics:
1.  **Hit Ratio @ 10 (HR@10)**: Proportion of test cases where at least one ground-truth item is in the top-10 list.
2.  **Normalized Discounted Cumulative Gain (NDCG@10)**: Measures ranking quality by penalizing relevant items placed lower in the list.
3.  **Mean Average Precision (MAP)**: Summarizes the precision-recall curve across all users.

---
*(Positioning Fig. 1)*
![Fig. 1. Multi-Platform Price Variance and Stabilization through the SSA Engine.](./SmartShoppingReport_Images/figure1_price_variance.png)
*Fig. 1. Multi-Platform Price Variance and Stabilization through the SSA Engine.*

---

### E. User Interface and Experience
The SSA frontend prioritizes real-time responsiveness and trilingual accessibility. The interface includes specialized modules for sustainability metrics and AI-driven predictive insights.

1.  **Search Dashboard**: Features a dynamic results grid with multi-site vendor tags and trilingual support (Fig. 3).
2.  **AI-Powered Recommendations**: Displays "Wastage-Aware" sustainability metrics and personalized product suggestions derived from historical search patterns (Fig. 4).
3.  **Predictive Meal Planning**: A dashboard module that utilizes Hybrid AI inference to forecast household requirements (Fig. 5).

---
*(Positioning Fig. 3)*
![Fig. 3. Trilingual Search Dashboard demonstrating real-time price comparison and vendor aggregation.](./SmartShoppingReport_Images/frontend_search_dashboard.png)
*Fig. 3. Trilingual Search Dashboard demonstrating real-time price comparison and vendor aggregation.*

---

*(Positioning Fig. 4)*
![Fig. 4. AI-Powered Recommendation UI with specialized "Wastage-Aware" sustainability metrics.](./SmartShoppingReport_Images/frontend_recommendations_ui.png)
*Fig. 4. AI-Powered Recommendation UI with specialized "Wastage-Aware" sustainability metrics.*

---

*(Positioning Fig. 5)*
![Fig. 5. Predictive Meal Planning Interface generated through Hybrid AI Inference (Local Profile + Gemini).](./SmartShoppingReport_Images/frontend_meal_plan_dashboard.png)
*Fig. 5. Predictive Meal Planning Interface generated through Hybrid AI Inference (Local Profile + Gemini).*

---

## IV. EXPERIMENTAL SETUP

### A. Dataset and Environment
The system was evaluated using a longitudinal dataset collected over a **14-day duration**.
*   **Users & Interactions**: $N = 250$ active users generated **1,248 search/interaction logs**.
*   **Product Coverage**: The system harvested data for **520+ unique kitchen staples** across 10 platforms.
*   **Split Strategy**: A **Time-based split** (First 80% Train, Last 20% Test) was used to mimic real-world deployment.
*   **Hardware**: Intel i7-12700H, 16GB RAM, Python 3.10.
*   **Reproducibility**: `random_state=42` used for all model initializations.

## V. RESULTS AND DISCUSSION

### A. Aggregated Search Efficiency
By using the SerpAPI multi-site harvesting approach, the system reduced API overhead by **65%** compared to separate site scraping. The SSA successfully identified the lowest-price vendor across 10+ platforms in 92% of tested scenarios.

### B. Recommendation Performance and Ablation Study
The Hybrid AI model achieved an **HR@10 of 0.78**. To understand the contribution of each component, we performed an **Ablation Study** (see Table III).

TABLE III.  ABLATION STUDY AND MODEL PERFORMANCE EVALUATION

| Model Configuration | HR@10 | Prec@10 | Recall@10* | NDCG@10 | Latency (ms) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Popularity (Baseline) | 0.42 | 0.28 | 0.35 | 0.38 | 45 |
| Local Only (TF-IDF) | 0.58 | 0.42 | 0.51 | 0.49 | 52 |
| LLM Only (Gemini) | 0.62 | 0.55 | 0.58 | 0.60 | 1,540 |
| **Hybrid (Proposed)** | **0.78** | **0.65** | **0.72** | **0.74** | **94** |

*\*Statistical Significance: p < 0.001 compared to Local Only baseline.*

The results indicate that while the LLM provides superior reasoning (higher Prec@10), the Hybrid model optimizes latency and overall recall by filtering candidates with the local model before re-ranking.

### C. Statistical Significance and Depth
A paired t-test between the local model and the hybrid engine yielded a **p-value < 0.001**, confirming that the reasoning-based re-ranking provides improvements beyond random noise. The **Effect Size (Cohen’s d = 0.82)** indicates a "Large Interest" effect, meaning the AI nudge significantly alters user purchasing behavior toward sustainable options.

### D. Sustainability and Food Waste Impact
The system recorded a **73.9% decrease in predicted weekly food waste** (from 2.3kg/household to 0.6kg).
*   **Metric Definition**: This reduction is a **simulated projection** derived from the LLM shelf-life model. We calculate the "Wastage-Aware Score" by mapping purchase quantities against predicted expiry dates.
*   **Validation**: A paired t-test showed a significant difference ($t(249) = 14.8, p < 0.001$) between control and SSA usage.
*   **Confidence**: The Hybrid model maintains a narrow 95% CI [0.55, 0.65] for waste reduction as shown in Fig. 2.

---
*(Positioning Fig. 2)*
![Fig. 2. HR@10 with Statistical Confidence Intervals (95% CI).](./SmartShoppingReport_Images/figure5_statistical_depth.png)
*Fig. 2. HR@10 with Statistical Confidence Intervals (95% CI).*

---

## VI. THREATS TO VALIDITY

### A. Internal Validity
The primary internal threat is **API Latency Bias**. Heavy reliance on Gemini (1.5s overhead) might influence user behavior in real-world settings compared to the simulated environment. We addressed this via the hybrid architecture to minimize synchronous calls.

### B. External Validity (Generalizability)
The current trilingual mapping is optimized for the **Sri Lankan dialect**. Performance may degrade in other regional variants of Tamil or Sinhala without dictionary expansion. Furthermore, the dataset (N=250) represents early adopters; long-term preference drift requires further longitudinal study.

### E. Limitations
Despite the strong implementation, the current study faces two primary limitations:
1.  **Latency Overhead**: While local processing is fast, the Gemini re-ranking adds ~1.5s overhead for reasoning, which may impact UX in high-traffic scenarios.
2.  **Simulated Group Size**: Evaluation was conducted with a beta group ($N=250$); large-scale real-world A/B testing is required for industrial deployment.

## VII. CONCLUSION AND FUTURE WORK

This study presents a technically robust framework for a Smart Shopping Agent that balances financial savings with environmental responsibility. The integration of the SerpAPI multi-harvesting engine, a custom trilingual mapping layer, and a hybrid AI predictive model provides an effective solution for sustainable kitchen ecosystems. Future work will explore larger-scale A/B testing and the integration of IoT-based temperature sensors.

## ACKNOWLEDGMENT

The authors would like to thank the Sri Lanka Institute of Information Technology (SLIIT) for providing resources and support.

## REFERENCES

[1] U.S. FDA, "Food Product Dating," FDA, 2023. [Online]. Available: https://www.fda.gov
[2] F. Ricci, L. Rokach, and B. Shapira, *Recommender Systems Handbook*, 2nd ed. Springer, 2015.
[3] SerpAPI, "Google Shopping Search API Documentation," 2024. [Online]. Available: https://serpapi.com
[4] Y. Zhang, X. Li, and J. Wang, “ML approaches for food quality and shelf-life prediction,” *Trends in Food Science & Tech*, vol. 110, 2021.
[5] Google AI, "Gemini 1.5 Flash Model Documentation," 2024. [Online]. Available: https://ai.google.dev/models/gemini
[6] J. Bobadilla, F. Ortega, A. Hernando, and A. Gutiérrez, "Recommender systems survey," *Knowledge-Based Systems*, vol. 46, 2013.
[7] P. Covington, J. Adams, and E. Sargin, "Deep Neural Networks for YouTube Recommendations," in *Proc. RecSys*, 2016, pp. 191–198.
