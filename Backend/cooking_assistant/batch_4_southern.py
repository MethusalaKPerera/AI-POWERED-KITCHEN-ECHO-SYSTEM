#!/usr/bin/env python3
"""
Recipe Generator - Batch 4: Southern/Coastal Specialties
25 authentic recipes from Southern Sri Lanka (IDs 103-127)
"""

import json
from pathlib import Path
from datetime import datetime

def generate_batch_4_southern_recipes():
    """Generate 25 Southern/Coastal specialty recipes"""
    
    recipes = [
        {
            "id": "recipe_103",
            "name": "Galle Fish Curry",
            "name_sinhala": "ගාල්ල මාළු කරිය",
            "name_tamil": "காலி மீன் கறி",
            "category": "Curry",
            "region": "Southern",
            "description": "Rich Southern fish curry with thick coconut milk",
            "ingredients": ["1kg fish (seer or tuna)", "500ml thick coconut milk", "3 tbsp curry powder", "2 tbsp chili powder", "1 tbsp tamarind paste", "3 onions, sliced", "10 goraka pieces", "2 pandan leaves", "3 green chilies", "1 sprig curry leaves", "3 tbsp oil", "Salt"],
            "instructions": ["Marinate fish with salt and turmeric", "Soak goraka in water", "Heat oil and fry onions", "Add curry powder and chili", "Add goraka water", "Add fish pieces", "Add thick coconut milk", "Add pandan and curry leaves", "Simmer gently for 20 minutes", "Adjust seasoning"],
            "prep_time_minutes": 20,
            "cook_time_minutes": 25,
            "servings": 6,
            "difficulty": "Medium",
            "tags": ["southern", "seafood", "rich", "coconut"],
            "cultural_notes": "Galle's signature fish curry, very rich",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_104",
            "name": "Matara Crab Curry",
            "name_sinhala": "මාතර කකුළු කරිය",
            "name_tamil": "மாத்தறை நண்டு கறி",
            "category": "Curry",
            "region": "Southern",
            "description": "Spicy crab curry with coconut and spices",
            "ingredients": ["6 large crabs", "400ml coconut milk", "4 tbsp curry powder", "1 tbsp chili powder", "10 curry leaves", "2 onions, sliced", "5 garlic cloves", "1 inch ginger", "2 tomatoes", "3 tbsp oil", "Salt"],
            "instructions": ["Clean and cut crabs", "Grind curry powder with garlic, ginger", "Fry onions in oil", "Add ground paste", "Add tomatoes", "Add crabs and mix", "Add coconut milk", "Add curry leaves", "Cook until crabs are done", "Serve with rice"],
            "prep_time_minutes": 30,
            "cook_time_minutes": 25,
            "servings": 4,
            "difficulty": "Hard",
            "tags": ["southern", "seafood", "spicy", "special"],
            "cultural_notes": "Matara's famous crab preparation",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_105",
            "name": "Pol Roti with Lunumiris",
            "name_sinhala": "පොල් රොටි ලුණු මිරිස් සමග",
            "name_tamil": "தேங்காய் ரொட்டி",
            "category": "Bread",
            "region": "Southern",
            "description": "Coconut flatbread with chili sambol",
            "ingredients": ["For roti: 3 cups flour, 2 cups coconut, 1 onion, 2 chilies, salt", "For lunumiris: 5 chilies, 1 onion, Maldive fish, lime, salt"],
            "instructions": ["Mix flour, coconut, chopped onion, chilies", "Add water to form dough", "Roll into flat circles", "Cook on griddle", "For sambol: grind chilies, onion, Maldive fish", "Add lime juice", "Serve roti with lunumiris"],
            "prep_time_minutes": 25,
            "cook_time_minutes": 20,
            "servings": 8,
            "difficulty": "Easy",
            "tags": ["southern", "breakfast", "coconut", "simple"],
            "cultural_notes": "Daily Southern breakfast staple",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_106",
            "name": "Parippu Pol Sambol",
            "name_sinhala": "පරිප්පු පොල් සම්බෝල",
            "name_tamil": "பருப்பு தேங்காய் சம்பல்",
            "category": "Sambol",
            "region": "Southern",
            "description": "Lentil and coconut sambol, Southern style",
            "ingredients": ["1 cup red lentils, cooked", "1 cup grated coconut", "1 onion, chopped", "3 green chilies", "1 tbsp chili powder", "1 tbsp Maldive fish", "Lime juice", "Salt"],
            "instructions": ["Cook lentils until soft", "Mix with grated coconut", "Add chopped onion and chilies", "Add chili powder", "Add Maldive fish", "Add lime juice and salt", "Mix well and serve"],
            "prep_time_minutes": 10,
            "cook_time_minutes": 15,
            "servings": 6,
            "difficulty": "Easy",
            "tags": ["southern", "sambol", "protein-rich", "simple"],
            "cultural_notes": "Protein-rich Southern sambol",
            "authenticity_score": 0.95
        },
        {
            "id": "recipe_107",
            "name": "Katta Sambol (Chili Paste)",
            "name_sinhala": "කට්ට සම්බෝල",
            "name_tamil": "கட்ட சம்பல்",
            "category": "Sambol",
            "region": "Southern",
            "description": "Fiery dried fish chili paste",
            "ingredients": ["10 dried red chilies", "1/2 cup dried sprats", "1 onion, chopped", "2 tbsp Maldive fish", "2 tbsp lime juice", "Salt to taste"],
            "instructions": ["Roast dried chilies", "Roast dried sprats separately", "Grind chilies coarsely", "Add sprats and grind", "Add onion and Maldive fish", "Add lime juice and salt", "Mix to paste", "Store in jar"],
            "prep_time_minutes": 15,
            "cook_time_minutes": 10,
            "servings": 10,
            "difficulty": "Easy",
            "tags": ["southern", "spicy", "condiment", "traditional"],
            "cultural_notes": "Extremely spicy, Southern favorite",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_108",
            "name": "Pol Maalu (Coconut Fish)",
            "name_sinhala": "පොල් මාලු",
            "name_tamil": "தேங்காய் மீன்",
            "category": "Curry",
            "region": "Southern",
            "description": "Fish tempered with coconut",
            "ingredients": ["500g fish, sliced", "2 cups grated coconut", "2 onions, sliced", "3 green chilies", "1 tsp turmeric", "10 curry leaves", "2 tbsp oil", "Salt"],
            "instructions": ["Marinate fish with turmeric and salt", "Fry fish lightly", "In same pan, fry onions", "Add grated coconut", "Add chilies and curry leaves", "Add fried fish", "Mix gently", "Serve with rice"],
            "prep_time_minutes": 15,
            "cook_time_minutes": 15,
            "servings": 4,
            "difficulty": "Easy",
            "tags": ["southern", "seafood", "coconut", "simple"],
            "cultural_notes": "Quick Southern fish dish",
            "authenticity_score": 0.95
        },
        {
            "id": "recipe_109",
            "name": "Ala Thel Dala (Fried Potatoes)",
            "name_sinhala": "අල තෙල් දළ",
            "name_tamil": "உருளைக்கிழங்கு பொரியல்",
            "category": "Curry",
            "region": "Southern",
            "description": "Tempered fried potatoes, Southern style",
            "ingredients": ["4 potatoes, cubed", "2 onions, sliced", "1 tsp mustard seeds", "10 curry leaves", "1 tsp turmeric", "1 tsp chili powder", "3 tbsp oil", "Salt"],
            "instructions": ["Boil potatoes until tender", "Heat oil and add mustard seeds", "Add onions and fry", "Add turmeric and chili", "Add boiled potatoes", "Add curry leaves", "Toss until crispy", "Serve as side"],
            "prep_time_minutes": 10,
            "cook_time_minutes": 15,
            "servings": 4,
            "difficulty": "Easy",
            "tags": ["southern", "vegetarian", "quick", "crispy"],
            "cultural_notes": "Common Southern side dish",
            "authenticity_score": 0.90
        },
        {
            "id": "recipe_110",
            "name": "Snoek Fish Curry",
            "name_sinhala": "හුරුල්ලො කරිය",
            "name_tamil": "ஸ்னோக் மீன் கறி",
            "category": "Curry",
            "region": "Southern",
            "description": "Canned snoek fish curry, Southern favorite",
            "ingredients": ["1 can snoek fish", "300ml coconut milk", "2 tbsp curry powder", "1 tsp chili powder", "2 onions, sliced", "2 tomatoes, chopped", "10 curry leaves", "2 tbsp oil", "Salt"],
            "instructions": ["Open can and drain oil", "Heat oil and fry onions", "Add curry powder and chili", "Add tomatoes", "Add snoek fish", "Add coconut milk", "Add curry leaves", "Simmer for 10 minutes", "Serve with bread"],
            "prep_time_minutes": 10,
            "cook_time_minutes": 15,
            "servings": 4,
            "difficulty": "Easy",
            "tags": ["southern", "seafood", "quick", "convenient"],
            "cultural_notes": "Popular store-cupboard meal",
            "authenticity_score": 0.85
        },
        {
            "id": "recipe_111",
            "name": "Murunga Leaves Malluma (Drumstick Leaves)",
            "name_sinhala": "මුරුංගා මල්ලුම",
            "name_tamil": "முருங்கை கீரை",
            "category": "Curry",
            "region": "Southern",
            "description": "Drumstick leaves tempered with coconut",
            "ingredients": ["2 cups drumstick leaves", "1 cup grated coconut", "1 onion, sliced", "2 green chilies", "1 tsp turmeric", "1 tsp mustard seeds", "10 curry leaves", "2 tbsp oil", "Salt"],
            "instructions": ["Wash drumstick leaves", "Heat oil and add mustard", "Add onions and chilies", "Add turmeric", "Add drumstick leaves", "Cook until wilted", "Add grated coconut", "Mix and serve"],
            "prep_time_minutes": 10,
            "cook_time_minutes": 10,
            "servings": 4,
            "difficulty": "Easy",
            "tags": ["southern", "vegetarian", "healthy", "greens"],
            "cultural_notes": "Very nutritious Southern green",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_112",
            "name": "Batu Moju (Southern Style)",
            "name_sinhala": "බෝංචි මොජු දකුණු විලාසය",
            "name_tamil": "பீன்ஸ் ஊறுகாய்",
            "category": "Sambol",
            "region": "Southern",
            "description": "Sweet and sour bean pickle with extra spices",
            "ingredients": ["300g green beans", "2 onions, sliced", "3 tbsp mustard seeds", "3 tbsp vinegar", "3 tbsp sugar", "2 tbsp chili powder", "1 tsp turmeric", "15 curry leaves", "Oil for frying", "Salt"],
            "instructions": ["Cut beans and blanch", "Fry until crispy", "Fry onions separately", "In oil, add mustard seeds", "Add turmeric and chili powder", "Add fried beans and onions", "Add vinegar and sugar", "Add curry leaves", "Mix and cool"],
            "prep_time_minutes": 15,
            "cook_time_minutes": 25,
            "servings": 8,
            "difficulty": "Medium",
            "tags": ["southern", "pickle", "sweet-sour", "spicy"],
            "cultural_notes": "Spicier than other regional versions",
            "authenticity_score": 0.95
        },
        {
            "id": "recipe_113",
            "name": "Pol Sambol (Southern Spicy Version)",
            "name_sinhala": "පොල් සම්බෝල (දකුණු)",
            "name_tamil": "தேங்காய் சம்பல்",
            "category": "Sambol",
            "region": "Southern",
            "description": "Extra spicy coconut sambol",
            "ingredients": ["2 cups grated coconut", "2 onions, chopped", "10 dried red chilies", "3 tbsp Maldive fish", "3 tbsp lime juice", "2 tsp chili powder", "Salt"],
            "instructions": ["Grind chilies coarsely", "Mix with grated coconut", "Add chopped onions", "Add Maldive fish", "Add extra chili powder", "Add lime juice and salt", "Mix well", "Serve fresh"],
            "prep_time_minutes": 15,
            "cook_time_minutes": 0,
            "servings": 6,
            "difficulty": "Easy",
            "tags": ["southern", "spicy", "sambol", "traditional"],
            "cultural_notes": "Southern version is notably spicier",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_114",
            "name": "Karawila Curry (Bitter Gourd)",
            "name_sinhala": "කරවිල කරිය",
            "name_tamil": "பாகற்காய் கறி",
            "category": "Curry",
            "region": "Southern",
            "description": "Bitter gourd curry with coconut",
            "ingredients": ["3 bitter gourds, sliced", "200ml coconut milk", "2 onions, sliced", "2 green chilies", "1 tsp turmeric", "1 tbsp curry powder", "10 curry leaves", "2 tbsp oil", "Salt"],
            "instructions": ["Slice bitter gourd and soak in salt water", "Squeeze out water", "Fry in oil until slightly crispy", "Remove and set aside", "Fry onions in same oil", "Add curry powder and turmeric", "Add fried bitter gourd", "Add coconut milk", "Add curry leaves", "Simmer and serve"],
            "prep_time_minutes": 20,
            "cook_time_minutes": 20,
            "servings": 4,
            "difficulty": "Medium",
            "tags": ["southern", "vegetarian", "healthy", "bitter"],
            "cultural_notes": "Believed to be very healthy, acquired taste",
            "authenticity_score": 0.95
        },
        {
            "id": "recipe_115",
            "name": "Papadam (Lentil Crackers)",
            "name_sinhala": "පාපඩම්",
            "name_tamil": "அப்பளம்",
            "category": "Snack",
            "region": "Southern",
            "description": "Thin crispy lentil crackers, Southern style",
            "ingredients": ["2 cups urad dal flour", "1 tsp salt", "1/2 tsp asafoetida", "1 tsp black pepper", "1 tsp cumin seeds", "Water as needed"],
            "instructions": ["Mix flour with salt, asafoetida", "Add pepper and cumin", "Add water to form stiff dough", "Roll very thin", "Dry in sun for 2 days", "Fry or roast before serving", "Store in airtight container"],
            "prep_time_minutes": 30,
            "cook_time_minutes": 2,
            "servings": 30,
            "difficulty": "Hard",
            "tags": ["southern", "snack", "crispy", "traditional"],
            "cultural_notes": "Made in bulk, sun-dried and stored",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_116",
            "name": "Bandakka Curry (Okra)",
            "name_sinhala": "බණ්ඩක්කා කරිය",
            "name_tamil": "வெண்டைக்காய் கறி",
            "category": "Curry",
            "region": "Southern",
            "description": "Okra curry with mustard seeds",
            "ingredients": ["300g okra, cut", "1 onion, sliced", "2 green chilies", "1 tsp mustard seeds", "1 tsp turmeric", "10 curry leaves", "100ml coconut milk", "2 tbsp oil", "Salt"],
            "instructions": ["Wash and dry okra completely", "Cut into pieces", "Heat oil and add mustard", "Add onions and fry", "Add okra and fry on high heat", "Add turmeric and salt", "Add coconut milk", "Add curry leaves", "Cook until tender"],
            "prep_time_minutes": 15,
            "cook_time_minutes": 15,
            "servings": 4,
            "difficulty": "Easy",
            "tags": ["southern", "vegetarian", "simple"],
            "cultural_notes": "Important to dry okra well",
            "authenticity_score": 0.90
        },
        {
            "id": "recipe_117",
            "name": "Kokis (Southern Style)",
            "name_sinhala": "කොකිස් (දකුණු)",
            "name_tamil": "கோக்கிஸ்",
            "category": "Dessert",
            "region": "Southern",
            "description": "Crispy flower-shaped cookies",
            "ingredients": ["2 cups rice flour", "1/2 cup coconut milk", "3 eggs", "1 tbsp sugar", "1/2 tsp salt", "1/4 tsp turmeric", "Oil for frying"],
            "instructions": ["Beat eggs with sugar", "Add coconut milk", "Gradually add rice flour", "Add salt and turmeric", "Mix to smooth batter", "Heat oil", "Dip kokis mold in hot oil", "Dip in batter", "Fry until crispy", "Store in airtight container"],
            "prep_time_minutes": 15,
            "cook_time_minutes": 40,
            "servings": 30,
            "difficulty": "Hard",
            "tags": ["southern", "dessert", "crispy", "festive"],
            "cultural_notes": "New Year essential, yellow color is traditional",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_118",
            "name": "Kiri Aluwa (Milk Toffee Squares)",
            "name_sinhala": "කිරි අලුව",
            "name_tamil": "பால் அலுவா",
            "category": "Dessert",
            "region": "Southern",
            "description": "Creamy milk fudge with cashews",
            "ingredients": ["3 cups milk powder", "2 cups sugar", "1 cup water", "1 cup cashews, chopped", "1 tsp cardamom powder", "2 tbsp butter"],
            "instructions": ["Boil sugar in water to syrup", "Add milk powder gradually", "Stir constantly on low heat", "Add butter", "Mixture will thicken", "Add cashews and cardamom", "Pour into greased tray", "Cool and cut squares"],
            "prep_time_minutes": 10,
            "cook_time_minutes": 35,
            "servings": 30,
            "difficulty": "Medium",
            "tags": ["southern", "dessert", "sweet", "festive"],
            "cultural_notes": "Popular gift during festivals",
            "authenticity_score": 0.90
        },
        {
            "id": "recipe_119",
            "name": "Rasa Kavili (Red Rice Flour Sweet)",
            "name_sinhala": "රස කැවිලි",
            "name_tamil": "ரசக்கவிலி",
            "category": "Dessert",
            "region": "Southern",
            "description": "Sweet rice flour diamonds",
            "ingredients": ["2 cups red rice flour", "1 cup jaggery, melted", "1 cup grated coconut", "1 tsp cardamom", "Water as needed"],
            "instructions": ["Roast rice flour until fragrant", "Mix with melted jaggery", "Add grated coconut", "Add cardamom", "Add water to bind", "Spread on tray", "Cut into diamond shapes", "Let set and serve"],
            "prep_time_minutes": 15,
            "cook_time_minutes": 10,
            "servings": 25,
            "difficulty": "Easy",
            "tags": ["southern", "dessert", "traditional", "no-fry"],
            "cultural_notes": "Healthy traditional sweet",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_120",
            "name": "Pol Toffee (Coconut Toffee)",
            "name_sinhala": "පොල් ටොෆි",
            "name_tamil": "தேங்காய் டாஃபி",
            "category": "Dessert",
            "region": "Southern",
            "description": "Chewy coconut jaggery toffee",
            "ingredients": ["3 cups grated coconut", "2 cups jaggery", "1 tsp cardamom", "1/2 cup cashews"],
            "instructions": ["Melt jaggery in pan", "Add grated coconut", "Cook stirring constantly", "Mixture will thicken", "Add cardamom and cashews", "Test by dropping in water", "Should form soft ball", "Pour into greased tray", "Cool and cut"],
            "prep_time_minutes": 10,
            "cook_time_minutes": 30,
            "servings": 25,
            "difficulty": "Medium",
            "tags": ["southern", "dessert", "chewy", "traditional"],
            "cultural_notes": "Made during coconut season",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_121",
            "name": "Aluwa (Diamond Shaped Sweet)",
            "name_sinhala": "අලුව",
            "name_tamil": "அலுவா",
            "category": "Dessert",
            "region": "Southern",
            "description": "Rice flour sweet with jaggery",
            "ingredients": ["2 cups rice flour, roasted", "1.5 cups jaggery, melted", "1 cup grated coconut", "1/2 cup cashews", "1 tsp cardamom", "Water"],
            "instructions": ["Roast rice flour", "Mix with melted jaggery", "Add coconut and cashews", "Add cardamom", "Add water to bind", "Spread on greased tray", "Cut diamond shapes", "Let set"],
            "prep_time_minutes": 15,
            "cook_time_minutes": 15,
            "servings": 30,
            "difficulty": "Easy",
            "tags": ["southern", "dessert", "traditional", "festive"],
            "cultural_notes": "Essential New Year sweet",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_122",
            "name": "Welithalapa (Pancake Rolls)",
            "name_sinhala": "වැලිතලප",
            "name_tamil": "வெலித்தலப",
            "category": "Dessert",
            "region": "Southern",
            "description": "Thin pancakes filled with jaggery coconut",
            "ingredients": ["For pancake: 2 cups flour, 2 eggs, milk, salt", "For filling: 2 cups coconut, 1 cup jaggery, cardamom"],
            "instructions": ["Make thin batter with flour, eggs, milk", "Make very thin pancakes", "For filling: cook coconut with jaggery", "Add cardamom", "Place filling on pancake", "Roll tightly", "Serve warm"],
            "prep_time_minutes": 25,
            "cook_time_minutes": 30,
            "servings": 15,
            "difficulty": "Medium",
            "tags": ["southern", "dessert", "sweet", "festive"],
            "cultural_notes": "Traditional Sinhala New Year sweet",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_123",
            "name": "Thalaguli (Sesame Balls)",
            "name_sinhala": "තල ගුලි",
            "name_tamil": "எள்ளு உருண்டை",
            "category": "Dessert",
            "region": "Southern",
            "description": "Sesame seed and jaggery balls",
            "ingredients": ["2 cups sesame seeds", "1.5 cups jaggery", "1/2 tsp cardamom", "1 tbsp ghee"],
            "instructions": ["Dry roast sesame seeds", "Melt jaggery with ghee", "Mix roasted sesame with jaggery", "Add cardamom", "Shape into small balls", "Let cool and set", "Store in container"],
            "prep_time_minutes": 15,
            "cook_time_minutes": 20,
            "servings": 25,
            "difficulty": "Easy",
            "tags": ["southern", "dessert", "healthy", "traditional"],
            "cultural_notes": "Nutritious traditional sweet",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_124",
            "name": "Unduwel (Sweet Coconut Balls)",
            "name_sinhala": "උඳුවැල්",
            "name_tamil": "இனிப்பு தேங்காய் உருண்டை",
            "category": "Dessert",
            "region": "Southern",
            "description": "Soft coconut jaggery balls",
            "ingredients": ["3 cups grated coconut", "1.5 cups jaggery", "1/2 cup rice flour", "1 tsp cardamom"],
            "instructions": ["Cook coconut with jaggery", "Stir until thick", "Add rice flour", "Cook until mixture leaves pan", "Add cardamom", "Cool slightly", "Shape into balls", "Serve at room temperature"],
            "prep_time_minutes": 10,
            "cook_time_minutes": 25,
            "servings": 20,
            "difficulty": "Medium",
            "tags": ["southern", "dessert", "soft", "traditional"],
            "cultural_notes": "Soft sweet for elders and children",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_125",
            "name": "Thala Guli (Sesame Jaggery Balls)",
            "name_sinhala": "තල ගුලි",
            "name_tamil": "எள்ளு வெல்லம் உருண்டை",
            "category": "Dessert",
            "region": "Southern",
            "description": "Roasted sesame balls with jaggery",
            "ingredients": ["2 cups sesame seeds", "1 cup jaggery", "1/2 tsp cardamom", "Ghee for greasing"],
            "instructions": ["Roast sesame until golden", "Melt jaggery to soft ball stage", "Mix sesame with jaggery", "Add cardamom", "Grease hands with ghee", "Shape into small balls quickly", "Cool and store"],
            "prep_time_minutes": 10,
            "cook_time_minutes": 15,
            "servings": 20,
            "difficulty": "Medium",
            "tags": ["southern", "dessert", "healthy", "calcium-rich"],
            "cultural_notes": "Good for bone health, given to children",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_126",
            "name": "Mun Kavum (Mung Bean Cakes)",
            "name_sinhala": "මුං කැවුම්",
            "name_tamil": "பயறு கேக்",
            "category": "Dessert",
            "region": "Southern",
            "description": "Sweet mung bean oil cakes",
            "ingredients": ["1 cup mung flour", "1/2 cup rice flour", "1 cup kithul treacle", "1/4 cup coconut milk", "1/2 tsp cardamom", "Oil for frying"],
            "instructions": ["Mix flours with treacle", "Add coconut milk", "Add cardamom", "Rest for 30 minutes", "Heat oil", "Drop spoonfuls and fry", "Fry until dark brown", "Drain and cool"],
            "prep_time_minutes": 15,
            "cook_time_minutes": 25,
            "servings": 20,
            "difficulty": "Medium",
            "tags": ["southern", "dessert", "fried", "traditional"],
            "cultural_notes": "Lighter version of regular kavum",
            "authenticity_score": 0.95
        },
        {
            "id": "recipe_127",
            "name": "Dodol (Sticky Toffee)",
            "name_sinhala": "දොඩොල්",
            "name_tamil": "டோடோல்",
            "category": "Dessert",
            "region": "Southern",
            "description": "Sticky coconut jaggery toffee",
            "ingredients": ["3 cups kithul treacle", "3 cups coconut milk", "2 cups rice flour", "1 cup cashews", "1 tsp cardamom"],
            "instructions": ["Mix rice flour with coconut milk", "Add treacle", "Cook on low heat stirring constantly", "Stir for 60-90 minutes", "Mixture will become very thick", "Add cashews and cardamom", "Pour into greased tray", "Cool and cut"],
            "prep_time_minutes": 15,
            "cook_time_minutes": 120,
            "servings": 40,
            "difficulty": "Hard",
            "tags": ["southern", "dessert", "sticky", "labor-intensive"],
            "cultural_notes": "Labor of love, requires constant stirring",
            "authenticity_score": 1.0
        }
    ]
    
    return recipes

def save_recipes(recipes, output_dir='rag/data/recipes'):
    """Save recipes to database"""
    
    db_path = Path(output_dir) / 'recipe_database.json'
    
    try:
        with open(db_path, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
            existing_recipes = existing_data.get('recipes', [])
    except FileNotFoundError:
        existing_recipes = []
    
    all_recipes = existing_recipes + recipes
    
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump({
            'total_recipes': len(all_recipes),
            'created_date': datetime.now().isoformat(),
            'recipes': all_recipes
        }, f, indent=2, ensure_ascii=False)
    
    for recipe in recipes:
        recipe_file = Path(output_dir) / f"{recipe['id']}.json"
        with open(recipe_file, 'w', encoding='utf-8') as f:
            json.dump(recipe, f, indent=2, ensure_ascii=False)
    
    print(f"OK Added {len(recipes)} Southern/Coastal recipes (IDs 103-127)")
    print(f"OK Total recipes now: {len(all_recipes)}")
    print(f"OK Saved to: {output_dir}")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("BATCH 4: SOUTHERN/COASTAL SPECIALTIES")
    print("="*70 + "\n")
    recipes = generate_batch_4_southern_recipes()
    save_recipes(recipes)
    print("\nOK Batch 4 Complete! Southern Sri Lankan cuisine added!")