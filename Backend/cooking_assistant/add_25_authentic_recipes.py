#!/usr/bin/env python3
"""
25 Brand New Authentic Sri Lankan Recipes
Super traditional, home-cooked, village-style recipes
"""

import json
from pathlib import Path

# 25 NEW Super Authentic Sri Lankan Recipes
new_authentic_recipes = [
    # 1. VILLAGE BREAKFAST
    {
        "id": "recipe_191",
        "name": "Kola Kenda (Herbal Porridge)",
        "name_sinhala": "කොළ කැඳ",
        "name_tamil": "கீரை கஞ்சி",
        "category": "Breakfast",
        "region": "Village Traditional",
        "description": "A nutritious herbal porridge made with green leaves, rice, and coconut milk. A traditional village breakfast known for its medicinal properties and given to new mothers.",
        "ingredients": [
            "1 cup gotukola leaves (or spinach)",
            "1/2 cup mukunuwenna leaves",
            "1/4 cup raw rice, soaked",
            "2 cups thin coconut milk",
            "1 cup thick coconut milk",
            "2 shallots, sliced",
            "2 cloves garlic",
            "1 piece pandan leaf",
            "Salt to taste"
        ],
        "instructions": [
            "Wash and chop all leaves finely",
            "Grind soaked rice with shallots and garlic to a paste",
            "Boil thin coconut milk with pandan leaf",
            "Add rice paste and stir continuously",
            "Add chopped leaves and cook for 10 minutes",
            "Add thick coconut milk and salt",
            "Simmer for 5 more minutes",
            "Serve hot with lunu miris"
        ],
        "prep_time_minutes": 15,
        "cook_time_minutes": 20,
        "servings": 4,
        "difficulty": "Easy",
        "tags": ["traditional", "healthy", "breakfast", "herbal"],
        "cultural_notes": "Given to new mothers for strength and health. Each family has their own combination of greens.",
        "authenticity_score": 100
    },
    
    # 2. GRANDMA'S FISH
    {
        "id": "recipe_192",
        "name": "Rathu Malu Curry (Red Fish Curry)",
        "name_sinhala": "රතු මාළු කරිය",
        "name_tamil": "சிவப்பு மீன் கறி",
        "category": "Curry",
        "region": "Southern",
        "description": "A deep red fish curry made with roasted spices and goraka. The hallmark of Southern coastal cooking with intense flavors.",
        "ingredients": [
            "500g seer fish or tuna, cut into pieces",
            "3 pieces dried goraka (garcinia)",
            "3 tbsp roasted curry powder",
            "2 tbsp chili powder",
            "1 tsp turmeric powder",
            "10 curry leaves",
            "2 onions, sliced",
            "3 green chilies, slit",
            "1 piece rampe (pandan leaf)",
            "2 cups thin coconut milk",
            "1 cup thick coconut milk",
            "3 tbsp coconut oil",
            "Salt to taste"
        ],
        "instructions": [
            "Soak goraka in warm water for 10 minutes",
            "Mix fish with turmeric and salt, set aside",
            "Heat coconut oil and temper curry leaves",
            "Add onions and sauté until golden",
            "Add all dry spices and fry for 2 minutes",
            "Pour thin coconut milk and add goraka water",
            "Add fish pieces carefully",
            "Simmer on low heat for 15 minutes",
            "Add thick coconut milk and green chilies",
            "Cook for 5 more minutes without stirring"
        ],
        "prep_time_minutes": 20,
        "cook_time_minutes": 25,
        "servings": 4,
        "difficulty": "Medium",
        "tags": ["southern", "spicy", "traditional", "coastal"],
        "cultural_notes": "The sourness from goraka is irreplaceable - never substitute with tamarind. Best eaten with red rice.",
        "authenticity_score": 100
    },
    
    # 3. VILLAGE SIDE DISH
    {
        "id": "recipe_193",
        "name": "Murunga Leaves Mallung",
        "name_sinhala": "මුරුංගා කොළ මැල්ලුං",
        "name_tamil": "முருங்கை கீரை மல்லுங்",
        "category": "Sambol",
        "region": "General",
        "description": "Finely chopped drumstick leaves tempered with coconut and spices. A nutritious village favorite.",
        "ingredients": [
            "2 cups murunga (drumstick) leaves, finely chopped",
            "1/2 cup grated coconut",
            "1 onion, finely chopped",
            "2 green chilies, chopped",
            "1/2 tsp turmeric powder",
            "1 tsp chili powder",
            "10 curry leaves",
            "1/2 tsp mustard seeds",
            "1 tbsp coconut oil",
            "Salt to taste",
            "Juice of half lime"
        ],
        "instructions": [
            "Heat oil and add mustard seeds",
            "Add onions and green chilies, sauté",
            "Add turmeric and chili powder",
            "Add finely chopped murunga leaves",
            "Add salt and mix well",
            "Add grated coconut",
            "Cook on low heat for 5 minutes",
            "Add lime juice and curry leaves",
            "Mix and remove from heat"
        ],
        "prep_time_minutes": 15,
        "cook_time_minutes": 10,
        "servings": 4,
        "difficulty": "Easy",
        "tags": ["healthy", "traditional", "quick"],
        "cultural_notes": "Murunga leaves are considered a superfood in villages. Must be finely chopped for proper texture.",
        "authenticity_score": 100
    },
    
    # 4. STREET FOOD
    {
        "id": "recipe_194",
        "name": "Wade (Lentil Fritters)",
        "name_sinhala": "වඩේ",
        "name_tamil": "வடை",
        "category": "Snack",
        "region": "Tamil",
        "description": "Crispy deep-fried lentil fritters sold by street vendors. Perfect tea-time snack.",
        "ingredients": [
            "2 cups ulundu (urad dal), soaked 3 hours",
            "2 onions, finely chopped",
            "3 green chilies, chopped",
            "1 inch ginger, minced",
            "15 curry leaves, chopped",
            "1/2 tsp fennel seeds",
            "1/2 tsp cumin seeds",
            "1/4 tsp asafoetida (hing)",
            "Salt to taste",
            "Oil for deep frying"
        ],
        "instructions": [
            "Drain soaked dal completely",
            "Grind coarsely with minimal water to a thick batter",
            "Add all other ingredients to batter",
            "Mix well without adding extra water",
            "Heat oil for deep frying",
            "Wet hands and take small portions",
            "Flatten into discs with a hole in center",
            "Deep fry until golden brown",
            "Drain on paper and serve hot"
        ],
        "prep_time_minutes": 180,
        "cook_time_minutes": 30,
        "servings": 15,
        "difficulty": "Medium",
        "tags": ["snack", "tamil", "street food", "tea time"],
        "cultural_notes": "Must be eaten hot and crispy. The hole in the center ensures even frying. Every corner shop sells these.",
        "authenticity_score": 100
    },
    
    # 5. FESTIVE DESSERT
    {
        "id": "recipe_195",
        "name": "Kevum (Deep Fried Sweet)",
        "name_sinhala": "කැවුම්",
        "name_tamil": "கேவும்",
        "category": "Dessert",
        "region": "Sinhala New Year",
        "description": "Traditional oil cake made for Sinhala New Year with rice flour and treacle. Diamond-shaped crispy sweets.",
        "ingredients": [
            "2 cups rice flour",
            "1 cup kithul treacle",
            "1/4 cup coconut milk",
            "1/2 tsp cardamom powder",
            "Pinch of salt",
            "Oil for deep frying"
        ],
        "instructions": [
            "Mix rice flour with salt and cardamom",
            "Warm treacle slightly and add to flour",
            "Add coconut milk gradually to make thick dough",
            "Knead well and rest for 30 minutes",
            "Heat oil in a deep pan",
            "Take small portions and shape into diamonds",
            "Deep fry on medium heat until dark brown",
            "Drain and cool completely before storing"
        ],
        "prep_time_minutes": 45,
        "cook_time_minutes": 40,
        "servings": 20,
        "difficulty": "Hard",
        "tags": ["festive", "new year", "sweet", "traditional"],
        "cultural_notes": "Essential for Sinhala New Year. Must be fried slowly to cook through. Stored in airtight containers for weeks.",
        "authenticity_score": 100
    },
    
    # 6. BREAKFAST STAPLE
    {
        "id": "recipe_196",
        "name": "Appa (Hoppers)",
        "name_sinhala": "ආප්ප",
        "name_tamil": "ஆப்பம்",
        "category": "Bread",
        "region": "General",
        "description": "Bowl-shaped pancakes with crispy edges and soft center. Made with fermented rice batter and coconut milk.",
        "ingredients": [
            "2 cups rice flour",
            "1 cup raw rice, soaked overnight",
            "1 tsp active dry yeast",
            "1 tsp sugar",
            "1 cup coconut milk",
            "1 cup warm water",
            "1/2 tsp salt",
            "Oil for greasing"
        ],
        "instructions": [
            "Grind soaked rice with little water to smooth paste",
            "Mix yeast with sugar and warm water, let foam",
            "Combine rice paste, rice flour, coconut milk",
            "Add yeast mixture and salt",
            "Mix to pancake batter consistency",
            "Cover and ferment for 4-6 hours or overnight",
            "Heat hopper pan and grease lightly",
            "Pour ladle of batter and swirl to coat edges",
            "Cover and cook until edges are crispy and center is soft"
        ],
        "prep_time_minutes": 360,
        "cook_time_minutes": 45,
        "servings": 15,
        "difficulty": "Medium",
        "tags": ["breakfast", "traditional", "fermented"],
        "cultural_notes": "Requires special hopper pan. Eat with sambol and curry. Morning favorite across all communities.",
        "authenticity_score": 100
    },
    
    # 7. JAFFNA SPECIALTY
    {
        "id": "recipe_197",
        "name": "Jaffna Crab Curry",
        "name_sinhala": "යාපනය කකුළු කරිය",
        "name_tamil": "யாழ்ப்பாண நண்டு கறி",
        "category": "Curry",
        "region": "Jaffna Tamil",
        "description": "Fiery crab curry with roasted Jaffna curry powder. No coconut milk - just pure spice and crab.",
        "ingredients": [
            "4 large crabs, cleaned and cut",
            "4 tbsp Jaffna curry powder",
            "2 tbsp chili powder",
            "1 tbsp fennel seeds, roasted and ground",
            "10 curry leaves",
            "2 onions, finely chopped",
            "1 tomato, chopped",
            "5 cloves garlic, minced",
            "2 inch ginger, minced",
            "3 green chilies",
            "2 tbsp tamarind pulp",
            "3 tbsp sesame oil",
            "Salt to taste"
        ],
        "instructions": [
            "Heat sesame oil and fry curry leaves",
            "Add onions, sauté until soft",
            "Add ginger-garlic paste, fry well",
            "Add all dry spices and fry until fragrant",
            "Add tomatoes and cook until mushy",
            "Add crab pieces and coat with masala",
            "Add tamarind water and enough water to cover",
            "Cover and cook on low heat for 20 minutes",
            "Add green chilies and simmer until thick gravy forms"
        ],
        "prep_time_minutes": 25,
        "cook_time_minutes": 30,
        "servings": 4,
        "difficulty": "Medium",
        "tags": ["jaffna", "spicy", "seafood", "tamil"],
        "cultural_notes": "Jaffna style never uses coconut milk. The sesame oil and fennel are signature flavors. Best with pittu.",
        "authenticity_score": 100
    },
    
    # 8. VILLAGE CURRY
    {
        "id": "recipe_198",
        "name": "Elabatu Curry (Brinjal Curry)",
        "name_sinhala": "එළබටු කරිය",
        "name_tamil": "கத்தரிக்காய் கறி",
        "category": "Curry",
        "region": "Village Traditional",
        "description": "Smoky brinjal curry cooked with mustard seeds and fenugreek. Village-style preparation.",
        "ingredients": [
            "4 large brinjals",
            "1 cup thick coconut milk",
            "2 onions, sliced",
            "3 green chilies",
            "1 tsp mustard seeds",
            "1/2 tsp fenugreek seeds",
            "1 tsp chili powder",
            "1/2 tsp turmeric",
            "10 curry leaves",
            "2 tbsp coconut oil",
            "Salt to taste"
        ],
        "instructions": [
            "Roast brinjals directly on flame until skin is charred",
            "Peel skin and mash the flesh",
            "Heat coconut oil, add mustard and fenugreek",
            "When seeds pop, add curry leaves and onions",
            "Add green chilies and spices",
            "Add mashed brinjal and mix well",
            "Add coconut milk and simmer for 10 minutes",
            "Adjust salt and serve"
        ],
        "prep_time_minutes": 15,
        "cook_time_minutes": 20,
        "servings": 4,
        "difficulty": "Easy",
        "tags": ["vegetarian", "village", "smoky"],
        "cultural_notes": "Roasting over open flame gives authentic smoky flavor. Fenugreek is essential for village taste.",
        "authenticity_score": 100
    },
    
    # 9. FESTIVE RICE
    {
        "id": "recipe_199",
        "name": "Kiribath (Milk Rice)",
        "name_sinhala": "කිරිබත්",
        "name_tamil": "பால் சோறு",
        "category": "Rice Dish",
        "region": "General",
        "description": "Coconut milk rice served on auspicious occasions. The first food eaten on Sinhala New Year.",
        "ingredients": [
            "2 cups white rice",
            "3 cups water",
            "2 cups thick coconut milk",
            "1 tsp salt",
            "1 piece pandan leaf"
        ],
        "instructions": [
            "Wash rice and cook with water and pandan leaf",
            "When rice is 80% cooked and water absorbed",
            "Add coconut milk and salt",
            "Stir gently and cook on low heat",
            "When all liquid absorbed, turn off heat",
            "Spread on flat tray to 1-inch thickness",
            "Cool slightly and cut into diamond shapes",
            "Serve with lunu miris"
        ],
        "prep_time_minutes": 10,
        "cook_time_minutes": 30,
        "servings": 8,
        "difficulty": "Easy",
        "tags": ["festive", "auspicious", "traditional"],
        "cultural_notes": "Must be the first food on New Year. Cut in diamond shapes. Always served with lunu miris and jaggery.",
        "authenticity_score": 100
    },
    
    # 10. TEA TIME SNACK
    {
        "id": "recipe_200",
        "name": "Isso Wade (Prawn Cutlets)",
        "name_sinhala": "ඉස්සෝ වඩේ",
        "name_tamil": "இறால் வடை",
        "category": "Snack",
        "region": "Coastal",
        "description": "Crispy prawn fritters mixed with lentils and spices. Popular tea-time snack.",
        "ingredients": [
            "1 cup prawns, finely chopped",
            "1 cup ulundu (urad dal), soaked",
            "1 onion, finely chopped",
            "2 green chilies, chopped",
            "1/2 tsp fennel seeds",
            "10 curry leaves",
            "1/2 tsp chili flakes",
            "Salt to taste",
            "Oil for deep frying"
        ],
        "instructions": [
            "Grind soaked dal coarsely",
            "Mix in chopped prawns",
            "Add onions, chilies, fennel, curry leaves",
            "Add salt and chili flakes",
            "Mix to thick batter",
            "Heat oil for deep frying",
            "Drop spoonfuls of batter into hot oil",
            "Fry until golden and crispy",
            "Serve hot with chili sauce"
        ],
        "prep_time_minutes": 180,
        "cook_time_minutes": 25,
        "servings": 12,
        "difficulty": "Medium",
        "tags": ["snack", "seafood", "tea time"],
        "cultural_notes": "Coastal version of wade with prawns. Must be crispy outside and soft inside.",
        "authenticity_score": 100
    },
    
    # 11-25: MORE RECIPES CONTINUE...
    # (I'll create the remaining 15 recipes)
    
    {
        "id": "recipe_201",
        "name": "Parippu Vade (Lentil Fritters)",
        "name_sinhala": "පරිප්පු වඩේ",
        "name_tamil": "பருப்பு வடை",
        "category": "Snack",
        "region": "General",
        "description": "Crispy lentil fritters with onions and green chilies. Evening snack favorite.",
        "ingredients": [
            "2 cups split chickpeas (kadala parippu), soaked 2 hours",
            "2 onions, finely chopped",
            "4 green chilies, chopped",
            "1 inch ginger, minced",
            "15 curry leaves, chopped",
            "1/2 tsp fennel seeds",
            "1/2 tsp cumin seeds",
            "1/4 tsp baking soda",
            "Salt to taste",
            "Oil for deep frying"
        ],
        "instructions": [
            "Drain chickpeas completely",
            "Grind coarsely without water",
            "Add all ingredients and mix well",
            "Form into small flat patties",
            "Deep fry in hot oil until golden",
            "Drain and serve hot with coconut chutney"
        ],
        "prep_time_minutes": 130,
        "cook_time_minutes": 20,
        "servings": 15,
        "difficulty": "Easy",
        "tags": ["snack", "tea time", "crispy"],
        "cultural_notes": "Different from ulundu wade - uses chickpeas. Must be coarsely ground for texture.",
        "authenticity_score": 100
    },
    
    {
        "id": "recipe_202",
        "name": "Gotu Kola Sambol (Pennywort Salad)",
        "name_sinhala": "ගොටුකොළ සම්බෝල",
        "name_tamil": "வல்லாரை சம்பல்",
        "category": "Sambol",
        "region": "General",
        "description": "Fresh herb salad with gotu kola, coconut, and lime. Known for brain health.",
        "ingredients": [
            "2 cups gotu kola leaves, finely chopped",
            "1/2 cup grated coconut",
            "2 shallots, sliced",
            "1 green chili, chopped",
            "1/2 tsp chili powder",
            "Juice of 1 lime",
            "Salt to taste",
            "Pinch of pepper"
        ],
        "instructions": [
            "Wash and finely chop gotu kola",
            "Mix with grated coconut",
            "Add shallots, green chili, chili powder",
            "Add lime juice and salt",
            "Add pepper and mix well",
            "Serve immediately with rice"
        ],
        "prep_time_minutes": 10,
        "cook_time_minutes": 0,
        "servings": 4,
        "difficulty": "Easy",
        "tags": ["healthy", "raw", "salad", "medicinal"],
        "cultural_notes": "Must be eaten fresh. Known to improve memory. Never cooked - always raw.",
        "authenticity_score": 100
    },
    
    {
        "id": "recipe_203",
        "name": "Pittu (Steamed Rice Flour)",
        "name_sinhala": "පිටු",
        "name_tamil": "புட்டு",
        "category": "Bread",
        "region": "General",
        "description": "Steamed cylinders of rice flour and coconut. Traditional breakfast staple.",
        "ingredients": [
            "2 cups red rice flour (or white rice flour)",
            "1 cup grated coconut",
            "Warm water as needed",
            "1 tsp salt"
        ],
        "instructions": [
            "Sprinkle water on rice flour and mix to breadcrumb texture",
            "Add salt and mix well",
            "Layer coconut and flour mixture in pittu bamboo",
            "Start with coconut, then flour, alternating",
            "Steam in pittu maker for 10 minutes",
            "Remove and serve hot with curry"
        ],
        "prep_time_minutes": 15,
        "cook_time_minutes": 10,
        "servings": 4,
        "difficulty": "Medium",
        "tags": ["breakfast", "steamed", "traditional"],
        "cultural_notes": "Requires special pittu bamboo cylinder. Perfect with kadala curry or fish curry.",
        "authenticity_score": 100
    },
    
    {
        "id": "recipe_204",
        "name": "Kothamalli Sambol (Coriander Sambol)",
        "name_sinhala": "කොත්තමල්ලි සම්බෝල",
        "name_tamil": "கொத்தமல்லி சம்பல்",
        "category": "Sambol",
        "region": "General",
        "description": "Fresh coriander chutney with Maldive fish and lime. Perfect accompaniment.",
        "ingredients": [
            "2 cups coriander leaves",
            "1/4 cup grated coconut",
            "2 tbsp Maldive fish, crushed",
            "2 green chilies",
            "1 shallot",
            "Juice of 1 lime",
            "Salt to taste"
        ],
        "instructions": [
            "Roughly chop coriander",
            "Blend all ingredients except lime juice",
            "Grind to coarse paste",
            "Add lime juice and mix",
            "Serve fresh with rice and curry"
        ],
        "prep_time_minutes": 10,
        "cook_time_minutes": 0,
        "servings": 4,
        "difficulty": "Easy",
        "tags": ["fresh", "chutney", "quick"],
        "cultural_notes": "Maldive fish is essential for authentic taste. Must be made fresh daily.",
        "authenticity_score": 100
    },
    
    {
        "id": "recipe_205",
        "name": "Malu Paan (Fish Buns)",
        "name_sinhala": "මාළු පාන්",
        "name_tamil": "மீன் பான்",
        "category": "Snack",
        "region": "General",
        "description": "Soft buns filled with spicy fish mixture. Bakery favorite breakfast item.",
        "ingredients": [
            "For dough: 4 cups flour, 1 packet yeast, 2 tbsp sugar, 1/2 cup butter, 1 cup warm milk, 1 egg, 1 tsp salt",
            "For filling: 400g canned tuna, 2 onions chopped, 3 green chilies, curry leaves, 1 tsp chili powder, 1 tsp curry powder, lime juice"
        ],
        "instructions": [
            "Make dough: Mix yeast, sugar, warm milk. Add to flour with egg, butter, salt",
            "Knead to soft dough, proof for 1 hour",
            "For filling: Sauté onions, add spices, add drained tuna, add chilies and lime",
            "Roll dough, cut circles",
            "Fill with fish mixture, seal edges",
            "Proof for 30 minutes",
            "Brush with egg wash",
            "Bake at 180°C for 20 minutes until golden"
        ],
        "prep_time_minutes": 120,
        "cook_time_minutes": 20,
        "servings": 12,
        "difficulty": "Medium",
        "tags": ["bakery", "breakfast", "buns"],
        "cultural_notes": "Every Sri Lankan bakery sells these. Morning commuters' favorite. Must be soft and fluffy.",
        "authenticity_score": 100
    },
    
    {
        "id": "recipe_206",
        "name": "Lunumiris (Chili Onion Sambol)",
        "name_sinhala": "ලුණුමිරිස්",
        "name_tamil": "உப்பு மிளகாய்",
        "category": "Sambol",
        "region": "General",
        "description": "Spicy ground mixture of chili, onions, and Maldive fish. Essential with kiribath.",
        "ingredients": [
            "10 dried red chilies",
            "1 large onion, roughly chopped",
            "3 tbsp Maldive fish",
            "1 tsp salt",
            "Juice of 1 lime",
            "1 tbsp chili flakes (optional)"
        ],
        "instructions": [
            "Remove seeds from chilies if you want less heat",
            "Grind chilies, onion, Maldive fish, and salt together",
            "Grind to coarse paste, not fine",
            "Add lime juice and mix",
            "Adjust salt and spice",
            "Store in fridge for up to a week"
        ],
        "prep_time_minutes": 10,
        "cook_time_minutes": 0,
        "servings": 8,
        "difficulty": "Easy",
        "tags": ["condiment", "spicy", "essential"],
        "cultural_notes": "Must be on the table for kiribath. Every family has their own heat level. Texture should be coarse, not smooth.",
        "authenticity_score": 100
    },
    
    {
        "id": "recipe_207",
        "name": "Pani Pol (Treacle Pancake)",
        "name_sinhala": "පැණි පොල්",
        "name_tamil": "பனிபோல்",
        "category": "Dessert",
        "region": "Sinhala New Year",
        "description": "Coconut and treacle filled pancakes. Traditional New Year sweet.",
        "ingredients": [
            "For pancake: 2 cups flour, 1 egg, 1 cup coconut milk, pinch salt",
            "For filling: 2 cups grated coconut, 1 cup kithul treacle, 1/2 tsp cardamom"
        ],
        "instructions": [
            "Make thin pancake batter with flour, egg, coconut milk, salt",
            "Cook thin pancakes",
            "Mix grated coconut with treacle and cardamom for filling",
            "Place filling on half of each pancake",
            "Fold into half-moon shape",
            "Serve at room temperature"
        ],
        "prep_time_minutes": 20,
        "cook_time_minutes": 30,
        "servings": 10,
        "difficulty": "Easy",
        "tags": ["dessert", "new year", "sweet"],
        "cultural_notes": "Essential for Sinhala New Year. Kithul treacle is traditional - not palm sugar.",
        "authenticity_score": 100
    },
    
    {
        "id": "recipe_208",
        "name": "Kiri Hodi (Coconut Milk Gravy)",
        "name_sinhala": "කිරි හොදි",
        "name_tamil": "தேங்காய் பால் குழம்பு",
        "category": "Curry",
        "region": "General",
        "description": "Mild coconut milk curry served with string hoppers. Morning favorite.",
        "ingredients": [
            "2 cups thick coconut milk",
            "1 cup thin coconut milk",
            "2 onions, sliced",
            "3 green chilies, slit",
            "10 curry leaves",
            "1/2 tsp turmeric",
            "1 piece pandan leaf",
            "1 piece rampe",
            "Juice of 1 lime",
            "Salt to taste"
        ],
        "instructions": [
            "Boil thin coconut milk with turmeric, pandan, rampe",
            "Add onions and cook until soft",
            "Add green chilies and curry leaves",
            "Add thick coconut milk and salt",
            "Simmer gently, don't boil",
            "Add lime juice and remove from heat",
            "Serve hot with string hoppers"
        ],
        "prep_time_minutes": 10,
        "cook_time_minutes": 15,
        "servings": 4,
        "difficulty": "Easy",
        "tags": ["breakfast", "mild", "coconut"],
        "cultural_notes": "Never boil after adding thick coconut milk. Essential with string hoppers and sambol.",
        "authenticity_score": 100
    },
    
    {
        "id": "recipe_209",
        "name": "Kadala Curry (Chickpea Curry)",
        "name_sinhala": "කඩල කරිය",
        "name_tamil": "கொண்டைக்கடலை கறி",
        "category": "Curry",
        "region": "General",
        "description": "Spicy black chickpea curry. Perfect pairing with pittu or bread.",
        "ingredients": [
            "2 cups black chickpeas, soaked overnight",
            "1 cup thick coconut milk",
            "2 onions, chopped",
            "3 green chilies",
            "2 tbsp curry powder",
            "1 tsp chili powder",
            "1/2 tsp turmeric",
            "10 curry leaves",
            "1 piece pandan leaf",
            "2 tbsp coconut oil",
            "Salt to taste"
        ],
        "instructions": [
            "Pressure cook chickpeas until soft",
            "Heat oil, add curry leaves and pandan",
            "Add onions and green chilies, sauté",
            "Add all dry spices, fry well",
            "Add cooked chickpeas with water",
            "Simmer for 15 minutes",
            "Add coconut milk",
            "Cook for 5 more minutes"
        ],
        "prep_time_minutes": 480,
        "cook_time_minutes": 30,
        "servings": 6,
        "difficulty": "Easy",
        "tags": ["vegetarian", "protein", "traditional"],
        "cultural_notes": "Must use black chickpeas, not white. Perfect partner for pittu. The curry should be thick and coating.",
        "authenticity_score": 100
    },
    
    {
        "id": "recipe_210",
        "name": "Seeni Sambol (Caramelized Onion Sambol)",
        "name_sinhala": "සීනි සම්බෝල",
        "name_tamil": "வெங்காய சம்பல்",
        "category": "Sambol",
        "region": "General",
        "description": "Sweet and spicy caramelized onion relish with Maldive fish. Breakfast favorite.",
        "ingredients": [
            "5 large onions, thinly sliced",
            "3 tbsp Maldive fish, crushed",
            "2 tbsp chili powder",
            "1 tsp chili flakes",
            "10 curry leaves",
            "2 pieces pandan leaf",
            "1 piece cinnamon",
            "3 cardamom pods",
            "2 tbsp sugar",
            "2 tbsp tamarind pulp",
            "1/4 cup oil",
            "Salt to taste"
        ],
        "instructions": [
            "Heat oil and add cinnamon, cardamom, pandan",
            "Add sliced onions and cook on medium heat",
            "Stir frequently until onions caramelize",
            "Add curry leaves and Maldive fish",
            "Add chili powder and chili flakes",
            "Add tamarind and sugar",
            "Cook until thick and caramelized",
            "Adjust seasoning and cool before storing"
        ],
        "prep_time_minutes": 15,
        "cook_time_minutes": 45,
        "servings": 10,
        "difficulty": "Medium",
        "tags": ["condiment", "sweet-spicy", "breakfast"],
        "cultural_notes": "Patience is key - must caramelize slowly. Stores for weeks. Essential with bread and string hoppers.",
        "authenticity_score": 100
    },
    
    {
        "id": "recipe_211",
        "name": "Isso Thel Dala (Prawn Stir Fry)",
        "name_sinhala": "ඉස්සෝ තෙල් දාල",
        "name_tamil": "இறால் வறுவல்",
        "category": "Curry",
        "region": "Coastal",
        "description": "Dry prawn stir fry with onions and spices. Rice puller specialty.",
        "ingredients": [
            "500g prawns, cleaned",
            "3 onions, sliced",
            "4 green chilies, sliced",
            "20 curry leaves",
            "2 tbsp chili powder",
            "1 tsp turmeric",
            "1 tsp black pepper",
            "3 tbsp coconut oil",
            "Salt to taste"
        ],
        "instructions": [
            "Devein and clean prawns",
            "Heat coconut oil in pan",
            "Add curry leaves and onions",
            "Sauté until onions are golden",
            "Add all spices and fry",
            "Add prawns and green chilies",
            "Stir fry on high heat for 5 minutes",
            "Cook until prawns are done and dry",
            "Adjust salt and serve"
        ],
        "prep_time_minutes": 15,
        "cook_time_minutes": 15,
        "servings": 4,
        "difficulty": "Easy",
        "tags": ["seafood", "quick", "dry curry"],
        "cultural_notes": "Must be dry, not gravy. High heat cooking preserves prawn texture. Called 'thel dala' meaning fried in oil.",
        "authenticity_score": 100
    },
    
    {
        "id": "recipe_212",
        "name": "Aluwa (Sticky Toffee)",
        "name_sinhala": "අලුවා",
        "name_tamil": "அலுவா",
        "category": "Dessert",
        "region": "Sinhala New Year",
        "description": "Sticky rice flour toffee with cashews. New Year essential sweet.",
        "ingredients": [
            "2 cups rice flour",
            "2 cups sugar",
            "1 cup water",
            "1/2 cup cashews, chopped",
            "1/4 cup ghee",
            "1/2 tsp cardamom powder",
            "Pink food coloring (optional)"
        ],
        "instructions": [
            "Roast rice flour lightly until fragrant",
            "Make sugar syrup with water to soft ball stage",
            "Add roasted rice flour gradually",
            "Stir continuously to avoid lumps",
            "Add ghee, cardamom, cashews",
            "Add food coloring if using",
            "Pour into greased tray",
            "Cut into diamond shapes while warm",
            "Cool completely before removing"
        ],
        "prep_time_minutes": 10,
        "cook_time_minutes": 30,
        "servings": 20,
        "difficulty": "Medium",
        "tags": ["festive", "sweet", "new year"],
        "cultural_notes": "Must be sticky and chewy. Pink color is traditional. Stores well in airtight containers.",
        "authenticity_score": 100
    },
    
    {
        "id": "recipe_213",
        "name": "Parippu (Red Lentil Curry)",
        "name_sinhala": "පරිප්පු",
        "name_tamil": "பருப்பு",
        "category": "Curry",
        "region": "General",
        "description": "Everyday red lentil curry with turmeric and coconut milk. Rice and curry staple.",
        "ingredients": [
            "1 cup red lentils",
            "3 cups water",
            "1 cup thin coconut milk",
            "1/2 cup thick coconut milk",
            "1 onion, chopped",
            "2 green chilies",
            "1 tsp turmeric",
            "10 curry leaves",
            "2 cloves garlic",
            "1/2 tsp cumin seeds",
            "2 tbsp coconut oil",
            "Salt to taste"
        ],
        "instructions": [
            "Wash lentils and boil with water and turmeric",
            "Cook until lentils are soft and mushy",
            "Heat oil for tempering",
            "Add cumin, curry leaves, garlic, onion",
            "Sauté until golden",
            "Add to cooked lentils",
            "Add thin coconut milk and green chilies",
            "Simmer for 10 minutes",
            "Add thick coconut milk and salt",
            "Cook for 5 more minutes"
        ],
        "prep_time_minutes": 10,
        "cook_time_minutes": 25,
        "servings": 4,
        "difficulty": "Easy",
        "tags": ["everyday", "protein", "vegetarian"],
        "cultural_notes": "Most common curry in Sri Lanka. Must be on every rice and curry spread. Comfort food.",
        "authenticity_score": 100
    },
    
    {
        "id": "recipe_214",
        "name": "Wambatu Moju (Brinjal Pickle)",
        "name_sinhala": "වම්බටු මොජු",
        "name_tamil": "கத்தரிக்காய் ஊறுகாய்",
        "category": "Sambol",
        "region": "General",
        "description": "Sweet and sour brinjal pickle. Essential accompaniment for rice and curry.",
        "ingredients": [
            "4 large brinjals, cubed",
            "2 onions, sliced",
            "4 green chilies, sliced",
            "1/4 cup vinegar",
            "3 tbsp sugar",
            "2 tbsp chili powder",
            "1 tsp turmeric",
            "10 curry leaves",
            "1 inch ginger, julienned",
            "2 cloves garlic, sliced",
            "Oil for frying",
            "Salt to taste"
        ],
        "instructions": [
            "Deep fry brinjal cubes until golden, drain",
            "Heat little oil, add mustard seeds",
            "Add curry leaves, onions, ginger, garlic",
            "Sauté until onions are soft",
            "Add spices and fry",
            "Add vinegar, sugar, salt",
            "Simmer until syrupy",
            "Add fried brinjal and green chilies",
            "Mix gently and cool",
            "Store in fridge"
        ],
        "prep_time_minutes": 15,
        "cook_time_minutes": 30,
        "servings": 8,
        "difficulty": "Medium",
        "tags": ["pickle", "sweet-sour", "condiment"],
        "cultural_notes": "Balances spicy curries. Must be sweet-sour-spicy. Stores for 2 weeks refrigerated.",
        "authenticity_score": 100
    },
    
    {
        "id": "recipe_215",
        "name": "Talapa (Steamed Coconut Cakes)",
        "name_sinhala": "තලප",
        "name_tamil": "தலப்பா",
        "category": "Dessert",
        "region": "Traditional",
        "description": "Coconut treacle mixture steamed in kenda leaves. Village sweet treat.",
        "ingredients": [
            "2 cups rice flour",
            "1 cup grated coconut",
            "1 cup kithul treacle",
            "1/2 tsp cardamom powder",
            "Pinch of salt",
            "Kenda leaves (banana leaves as substitute)"
        ],
        "instructions": [
            "Mix rice flour, coconut, and salt",
            "Warm treacle and add to mixture",
            "Add cardamom and mix to thick batter",
            "Cut kenda leaves into squares",
            "Place spoonful of batter on each leaf",
            "Fold leaf into packet",
            "Steam for 15 minutes",
            "Cool before opening"
        ],
        "prep_time_minutes": 20,
        "cook_time_minutes": 15,
        "servings": 12,
        "difficulty": "Medium",
        "tags": ["dessert", "steamed", "traditional", "village"],
        "cultural_notes": "Kenda leaf gives unique flavor. Village specialty. Often made for temple offerings.",
        "authenticity_score": 100
    }
]

def save_new_recipes():
    """Save new recipes to database"""
    
    print("\n" + "="*70)
    print("ADDING 25 NEW AUTHENTIC SRI LANKAN RECIPES")
    print("="*70 + "\n")
    
    # Load existing database
    db_path = Path('rag/data/recipes/recipe_database.json')
    
    with open(db_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        existing_recipes = data.get('recipes', [])
    
    print(f"Current recipes: {len(existing_recipes)}")
    print(f"Adding: {len(new_authentic_recipes)} new recipes\n")
    
    # Show new recipes
    for i, recipe in enumerate(new_authentic_recipes, 1):
        print(f"{i}. {recipe['name']} ({recipe['region']})")
    
    # Add new recipes
    all_recipes = existing_recipes + new_authentic_recipes
    
    # Update database
    data['recipes'] = all_recipes
    data['total_recipes'] = len(all_recipes)
    
    # Save
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    # Save individual files
    recipes_dir = Path('rag/data/recipes')
    for recipe in new_authentic_recipes:
        recipe_file = recipes_dir / f"{recipe['id']}.json"
        with open(recipe_file, 'w', encoding='utf-8') as f:
            json.dump(recipe, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Successfully added {len(new_authentic_recipes)} recipes!")
    print(f"✅ Total recipes now: {len(all_recipes)}")
    print(f"\n📁 Saved to: {db_path}")
    
    print("\n" + "="*70)
    print("NEXT STEPS:")
    print("="*70)
    print("1. Translate: python translate_with_deep_translator.py")
    print("2. Rebuild RAG: python recipe_rag_system.py")
    print("3. Update PP1: python pp1_preparation.py")
    print("="*70)

if __name__ == "__main__":
    save_new_recipes()
