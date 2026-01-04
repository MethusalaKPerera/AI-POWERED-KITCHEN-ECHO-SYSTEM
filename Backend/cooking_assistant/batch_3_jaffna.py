#!/usr/bin/env python3
"""
Recipe Generator - Batch 3: Jaffna Tamil Specialties
25 authentic recipes from Northern Sri Lanka (IDs 078-102)
"""

import json
from pathlib import Path
from datetime import datetime

def generate_batch_3_jaffna_recipes():
    """Generate 25 Jaffna Tamil specialty recipes"""
    
    recipes = [
        {
            "id": "recipe_078",
            "name": "Jaffna Crab Curry",
            "name_sinhala": "යාපනය කකුළු කරිය",
            "name_tamil": "யாழ்ப்பாண நண்டு கறி",
            "category": "Curry",
            "region": "Jaffna",
            "description": "Spicy crab curry with roasted spices, Jaffna signature dish",
            "ingredients": ["4 large crabs, cleaned", "400ml coconut milk", "3 tbsp Jaffna curry powder", "2 tbsp roasted curry powder", "1 tsp fennel seeds", "1 tsp black pepper", "3 onions, sliced", "8 garlic cloves", "2 inch ginger", "2 tomatoes, chopped", "3 green chilies", "2 sprigs curry leaves", "3 tbsp oil", "Salt to taste"],
            "instructions": ["Clean crabs and cut into pieces", "Roast curry powder until fragrant", "Heat oil and fry onions, garlic, ginger", "Add roasted curry powder and fennel", "Add tomatoes and cook until soft", "Add crab pieces and mix well", "Add thin coconut milk and simmer", "Add thick coconut milk", "Add curry leaves and chilies", "Simmer until crabs are cooked"],
            "prep_time_minutes": 30,
            "cook_time_minutes": 25,
            "servings": 4,
            "difficulty": "Hard",
            "tags": ["jaffna", "seafood", "spicy", "signature"],
            "cultural_notes": "Jaffna's most famous dish, served at special occasions",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_079",
            "name": "Jaffna Mutton Curry",
            "name_sinhala": "යාපනය එළු මස් කරිය",
            "name_tamil": "யாழ்ப்பாண ஆட்டு கறி",
            "category": "Curry",
            "region": "Jaffna",
            "description": "Rich mutton curry with roasted spices",
            "ingredients": ["1kg mutton, cubed", "300ml coconut milk", "4 tbsp Jaffna curry powder", "2 tbsp roasted curry powder", "2 onions, sliced", "6 garlic cloves", "1 inch ginger", "2 tomatoes", "10 curry leaves", "1 cinnamon stick", "4 cardamom", "3 cloves", "3 tbsp oil", "Salt"],
            "instructions": ["Pressure cook mutton with salt until tender", "Roast curry powder", "Fry whole spices in oil", "Add onions, garlic, ginger", "Add roasted curry powder", "Add tomatoes", "Add cooked mutton with stock", "Add coconut milk", "Simmer until thick", "Garnish with curry leaves"],
            "prep_time_minutes": 20,
            "cook_time_minutes": 60,
            "servings": 6,
            "difficulty": "Medium",
            "tags": ["jaffna", "mutton", "spicy", "rich"],
            "cultural_notes": "Traditional Jaffna Tamil wedding dish",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_080",
            "name": "Crab Kool (Crab Soup)",
            "name_sinhala": "කකුළු කූල්",
            "name_tamil": "நண்டு கூழ்",
            "category": "Curry",
            "region": "Jaffna",
            "description": "Thick crab soup with palmyrah flour",
            "ingredients": ["500g crab meat", "1 cup palmyrah flour", "2 onions, chopped", "4 garlic cloves", "1 inch ginger", "2 green chilies", "1 tsp turmeric", "1 tsp black pepper", "1 liter water", "2 tbsp oil", "Salt"],
            "instructions": ["Extract crab meat", "Sauté onions, garlic, ginger in oil", "Add turmeric and pepper", "Add water and bring to boil", "Mix palmyrah flour with water", "Add to pot while stirring", "Add crab meat", "Simmer until thick", "Add chilies", "Serve hot"],
            "prep_time_minutes": 25,
            "cook_time_minutes": 30,
            "servings": 4,
            "difficulty": "Medium",
            "tags": ["jaffna", "soup", "seafood", "traditional"],
            "cultural_notes": "Ancient Jaffna recipe using palmyrah flour",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_081",
            "name": "Jaffna Dosai",
            "name_sinhala": "යාපනය දොසයි",
            "name_tamil": "யாழ்ப்பாண தோசை",
            "category": "Bread",
            "region": "Jaffna",
            "description": "Crispy fermented rice and lentil crepes",
            "ingredients": ["2 cups parboiled rice", "1 cup urad dal", "1/2 tsp fenugreek seeds", "Salt to taste", "Water for grinding", "Oil for cooking"],
            "instructions": ["Soak rice, dal, and fenugreek overnight", "Drain and grind to smooth batter", "Add salt and ferment for 8-12 hours", "Heat griddle and grease lightly", "Pour batter and spread thin", "Cook until crispy and golden", "Flip and cook other side", "Serve with sambol or chutney"],
            "prep_time_minutes": 20,
            "cook_time_minutes": 5,
            "servings": 10,
            "difficulty": "Medium",
            "tags": ["jaffna", "breakfast", "fermented", "crispy"],
            "cultural_notes": "Daily breakfast staple in Jaffna homes",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_082",
            "name": "Kool (Seafood Soup)",
            "name_sinhala": "කූල්",
            "name_tamil": "கூழ்",
            "category": "Curry",
            "region": "Jaffna",
            "description": "Hearty seafood soup with mixed seafood",
            "ingredients": ["200g prawns", "200g squid", "200g fish", "1 cup palmyrah flour", "2 onions", "5 garlic cloves", "1 inch ginger", "1 tsp pepper", "1 tsp turmeric", "2 green chilies", "1.5 liters water", "Salt"],
            "instructions": ["Clean all seafood", "Boil water with onions, garlic, ginger", "Add turmeric and pepper", "Add seafood", "Mix palmyrah flour with water", "Add to pot while stirring", "Cook until thick", "Add chilies", "Season and serve"],
            "prep_time_minutes": 30,
            "cook_time_minutes": 25,
            "servings": 6,
            "difficulty": "Medium",
            "tags": ["jaffna", "seafood", "soup", "hearty"],
            "cultural_notes": "Traditional Jaffna comfort food",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_083",
            "name": "Odiyal Kool",
            "name_sinhala": "ඔඩියල් කූල්",
            "name_tamil": "ஒடியல் கூழ்",
            "category": "Curry",
            "region": "Jaffna",
            "description": "Vegetarian version of kool with odiyal root",
            "ingredients": ["500g odiyal root, diced", "1 cup palmyrah flour", "2 onions", "3 garlic cloves", "1 tsp cumin", "1 tsp fennel", "2 green chilies", "1 liter water", "2 tbsp oil", "Salt"],
            "instructions": ["Peel and dice odiyal root", "Boil until tender", "In separate pot, fry spices", "Add onions and garlic", "Add boiled odiyal", "Add water", "Mix palmyrah flour with water", "Add to pot stirring continuously", "Cook until thick", "Serve hot"],
            "prep_time_minutes": 20,
            "cook_time_minutes": 30,
            "servings": 4,
            "difficulty": "Medium",
            "tags": ["jaffna", "vegetarian", "traditional", "soup"],
            "cultural_notes": "Healthy Jaffna soup made during fasting",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_084",
            "name": "Puttu (Steamed Rice Cake)",
            "name_sinhala": "පුට්ටු",
            "name_tamil": "புட்டு",
            "category": "Bread",
            "region": "Jaffna",
            "description": "Cylindrical steamed rice cake with coconut",
            "ingredients": ["2 cups puttu flour (rice flour)", "1 cup grated coconut", "Water as needed", "Salt to taste"],
            "instructions": ["Mix rice flour with water to breadcrumb consistency", "Add salt", "Layer flour and coconut in puttu maker", "Alternate layers", "Steam for 10-12 minutes", "Remove and serve hot", "Traditionally served with banana and jaggery"],
            "prep_time_minutes": 15,
            "cook_time_minutes": 12,
            "servings": 4,
            "difficulty": "Medium",
            "tags": ["jaffna", "breakfast", "steamed", "traditional"],
            "cultural_notes": "Breakfast staple, eaten sweet or with curry",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_085",
            "name": "Ulundu Vadai (Lentil Donuts)",
            "name_sinhala": "උලුඳු වඩේ",
            "name_tamil": "உளுந்து வடை",
            "category": "Snack",
            "region": "Jaffna",
            "description": "Crispy urad dal fritters with onions",
            "ingredients": ["2 cups urad dal, soaked", "3 green chilies", "2 onions, chopped", "1 inch ginger", "10 curry leaves", "1 tsp cumin seeds", "Salt to taste", "Oil for frying"],
            "instructions": ["Soak dal for 4 hours", "Drain and grind coarsely", "Add chilies, ginger, cumin", "Add onions and curry leaves", "Add salt and mix", "Heat oil", "Shape into donuts with hole", "Fry until golden brown", "Serve with chutney"],
            "prep_time_minutes": 20,
            "cook_time_minutes": 20,
            "servings": 15,
            "difficulty": "Medium",
            "tags": ["jaffna", "snack", "fried", "crispy"],
            "cultural_notes": "Popular tea-time snack in Jaffna",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_086",
            "name": "Thengai Sadam (Coconut Rice)",
            "name_sinhala": "පොල් බත්",
            "name_tamil": "தேங்காய் சாதம்",
            "category": "Rice Dish",
            "region": "Jaffna",
            "description": "Fragrant coconut rice with cashews",
            "ingredients": ["2 cups basmati rice", "1 cup grated coconut", "10 cashew nuts", "1 tsp mustard seeds", "1 tsp urad dal", "2 green chilies", "10 curry leaves", "1/2 tsp turmeric", "3 tbsp ghee", "Salt"],
            "instructions": ["Cook rice and cool", "Fry cashews in ghee", "Add mustard seeds and urad dal", "Add curry leaves and chilies", "Add grated coconut and turmeric", "Mix with rice", "Season with salt", "Serve at room temperature"],
            "prep_time_minutes": 15,
            "cook_time_minutes": 20,
            "servings": 4,
            "difficulty": "Easy",
            "tags": ["jaffna", "rice", "coconut", "simple"],
            "cultural_notes": "Traditional temple offering and festival food",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_087",
            "name": "Masala Vadai",
            "name_sinhala": "මසාලා වඩේ",
            "name_tamil": "மசாலா வடை",
            "category": "Snack",
            "region": "Jaffna",
            "description": "Spiced chana dal fritters",
            "ingredients": ["2 cups chana dal, soaked", "4 dried red chilies", "1 tsp fennel seeds", "2 onions, chopped", "1 inch ginger", "10 curry leaves", "1/2 tsp asafoetida", "Salt", "Oil for frying"],
            "instructions": ["Soak dal for 2 hours", "Drain and grind coarsely with chilies", "Add fennel, ginger, asafoetida", "Add onions and curry leaves", "Add salt", "Heat oil", "Drop spoonfuls into oil", "Fry until golden", "Drain and serve hot"],
            "prep_time_minutes": 20,
            "cook_time_minutes": 20,
            "servings": 20,
            "difficulty": "Easy",
            "tags": ["jaffna", "snack", "spicy", "fried"],
            "cultural_notes": "Popular street food in Jaffna town",
            "authenticity_score": 0.95
        },
        {
            "id": "recipe_088",
            "name": "Kuzhi Paniyaram",
            "name_sinhala": "කුෂි පණියාරම්",
            "name_tamil": "குழி பணியாரம்",
            "category": "Snack",
            "region": "Jaffna",
            "description": "Small round fermented rice balls",
            "ingredients": ["2 cups parboiled rice", "1/2 cup urad dal", "Salt to taste", "1 tsp fenugreek", "Water for grinding", "Oil for paniyaram pan"],
            "instructions": ["Soak rice, dal, fenugreek overnight", "Grind to smooth batter", "Ferment for 8 hours", "Add salt", "Heat paniyaram pan with oil in each cavity", "Pour batter into cavities", "Cook until golden on both sides", "Serve with chutney"],
            "prep_time_minutes": 20,
            "cook_time_minutes": 15,
            "servings": 25,
            "difficulty": "Medium",
            "tags": ["jaffna", "snack", "fermented", "traditional"],
            "cultural_notes": "Made in special paniyaram pan with round cavities",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_089",
            "name": "Prawn Varuval (Dry Prawn Fry)",
            "name_sinhala": "ඉස්සෝ වරුවල්",
            "name_tamil": "இறால் வறுவல்",
            "category": "Curry",
            "region": "Jaffna",
            "description": "Spicy dry fried prawns",
            "ingredients": ["500g prawns, cleaned", "2 tbsp Jaffna curry powder", "1 tsp chili powder", "1/2 tsp turmeric", "2 onions, sliced", "5 curry leaves", "1 tsp fennel seeds", "3 tbsp oil", "Salt"],
            "instructions": ["Marinate prawns with curry powder, chili, turmeric, salt", "Heat oil and add fennel seeds", "Add onions and fry", "Add marinated prawns", "Fry on high heat until dry", "Add curry leaves", "Cook until prawns are crispy", "Serve as side dish"],
            "prep_time_minutes": 15,
            "cook_time_minutes": 15,
            "servings": 4,
            "difficulty": "Easy",
            "tags": ["jaffna", "seafood", "dry", "spicy"],
            "cultural_notes": "Popular side dish with rice",
            "authenticity_score": 0.95
        },
        {
            "id": "recipe_090",
            "name": "Rasam (Tamarind Soup)",
            "name_sinhala": "රසම්",
            "name_tamil": "ரசம்",
            "category": "Curry",
            "region": "Jaffna",
            "description": "Tangy tamarind soup with spices",
            "ingredients": ["2 tbsp tamarind paste", "2 tomatoes, chopped", "1 tsp rasam powder", "1/2 tsp turmeric", "1 tsp mustard seeds", "1 tsp cumin seeds", "10 curry leaves", "3 garlic cloves, crushed", "2 cups water", "2 tbsp oil", "Salt", "Coriander leaves"],
            "instructions": ["Extract tamarind juice", "Boil with tomatoes, turmeric, salt", "Add rasam powder", "In separate pan, temper mustard and cumin", "Add curry leaves and garlic", "Add to tamarind mixture", "Bring to boil", "Garnish with coriander", "Serve with rice"],
            "prep_time_minutes": 10,
            "cook_time_minutes": 15,
            "servings": 4,
            "difficulty": "Easy",
            "tags": ["jaffna", "soup", "tangy", "light"],
            "cultural_notes": "Digestive soup served with every meal",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_091",
            "name": "Thayir Sadam (Curd Rice)",
            "name_sinhala": "දධි සදම්",
            "name_tamil": "தயிர் சாதம்",
            "category": "Rice Dish",
            "region": "Jaffna",
            "description": "Cooling yogurt rice with tempering",
            "ingredients": ["2 cups cooked rice", "1 cup yogurt", "1/2 cup milk", "1 tsp mustard seeds", "1 tsp urad dal", "2 green chilies", "1 inch ginger, chopped", "10 curry leaves", "2 tbsp oil", "Salt", "Coriander leaves"],
            "instructions": ["Mash cooked rice slightly", "Mix with yogurt and milk", "Add salt", "Heat oil and add mustard seeds", "Add urad dal until golden", "Add chilies, ginger, curry leaves", "Pour over rice mixture", "Mix well", "Garnish with coriander", "Serve chilled"],
            "prep_time_minutes": 10,
            "cook_time_minutes": 10,
            "servings": 4,
            "difficulty": "Easy",
            "tags": ["jaffna", "rice", "cooling", "probiotic"],
            "cultural_notes": "Cooling meal for hot weather, aids digestion",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_092",
            "name": "Aviyal (Mixed Vegetable Curry)",
            "name_sinhala": "අවියල්",
            "name_tamil": "அவியல்",
            "category": "Curry",
            "region": "Jaffna",
            "description": "Mild vegetable curry with coconut and yogurt",
            "ingredients": ["2 carrots, cubed", "1 drumstick, cut", "1 raw banana, cubed", "10 beans, cut", "1 cup grated coconut", "2 green chilies", "1 tsp cumin", "1/2 cup yogurt", "10 curry leaves", "1 tbsp coconut oil", "Salt"],
            "instructions": ["Boil vegetables with turmeric and salt until tender", "Grind coconut, cumin, chilies to paste", "Add to vegetables", "Add yogurt and mix", "Simmer for 5 minutes", "Add curry leaves and coconut oil", "Mix and serve"],
            "prep_time_minutes": 20,
            "cook_time_minutes": 20,
            "servings": 6,
            "difficulty": "Medium",
            "tags": ["jaffna", "vegetarian", "healthy", "mild"],
            "cultural_notes": "Traditional feast dish, very nutritious",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_093",
            "name": "Paruppu Urundai Kulambu (Lentil Ball Curry)",
            "name_sinhala": "පරුප්පු උරුන්ඩයි",
            "name_tamil": "பருப்பு உருண்டை குழம்பு",
            "category": "Curry",
            "region": "Jaffna",
            "description": "Lentil balls in tamarind gravy",
            "ingredients": ["1 cup toor dal", "3 dried red chilies", "1 tsp fennel seeds", "2 tbsp tamarind paste", "2 tomatoes", "1 tsp sambar powder", "1 tsp mustard seeds", "10 curry leaves", "2 tbsp oil", "Salt"],
            "instructions": ["Soak and grind dal with chilies and fennel", "Shape into small balls", "Steam for 15 minutes", "Make tamarind gravy with tomatoes, sambar powder", "Add steamed balls to gravy", "Temper with mustard and curry leaves", "Simmer for 10 minutes", "Serve with rice"],
            "prep_time_minutes": 25,
            "cook_time_minutes": 30,
            "servings": 4,
            "difficulty": "Medium",
            "tags": ["jaffna", "vegetarian", "protein-rich", "tangy"],
            "cultural_notes": "Special Sunday curry in Jaffna homes",
            "authenticity_score": 0.95
        },
        {
            "id": "recipe_094",
            "name": "Sambar (Lentil Vegetable Stew)",
            "name_sinhala": "සම්බාර්",
            "name_tamil": "சாம்பார்",
            "category": "Curry",
            "region": "Jaffna",
            "description": "Tangy lentil stew with vegetables",
            "ingredients": ["1 cup toor dal", "2 tomatoes", "1 drumstick, cut", "1 carrot, cubed", "1 onion, chopped", "2 tbsp sambar powder", "1 tbsp tamarind paste", "1 tsp mustard seeds", "10 curry leaves", "2 tbsp oil", "Salt", "Coriander leaves"],
            "instructions": ["Cook dal until soft", "Boil vegetables with turmeric", "Mash dal slightly", "Add vegetables to dal", "Add tamarind and sambar powder", "Simmer for 10 minutes", "Temper mustard, curry leaves in oil", "Add to sambar", "Garnish with coriander"],
            "prep_time_minutes": 15,
            "cook_time_minutes": 25,
            "servings": 6,
            "difficulty": "Easy",
            "tags": ["jaffna", "vegetarian", "tangy", "daily"],
            "cultural_notes": "Essential accompaniment to rice, dosai, idli",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_095",
            "name": "Kootu (Vegetable with Lentils)",
            "name_sinhala": "කූටු",
            "name_tamil": "கூட்டு",
            "category": "Curry",
            "region": "Jaffna",
            "description": "Mild vegetable and lentil curry",
            "ingredients": ["1 cup chana dal", "2 carrots, cubed", "1 raw banana, cubed", "1/2 cup grated coconut", "1 tsp cumin", "2 green chilies", "1/2 tsp turmeric", "10 curry leaves", "1 tbsp coconut oil", "Salt"],
            "instructions": ["Cook dal and vegetables separately until tender", "Grind coconut, cumin, chilies to paste", "Mix dal, vegetables, and coconut paste", "Add turmeric and salt", "Simmer for 5 minutes", "Add curry leaves and coconut oil", "Serve with rice"],
            "prep_time_minutes": 15,
            "cook_time_minutes": 20,
            "servings": 4,
            "difficulty": "Easy",
            "tags": ["jaffna", "vegetarian", "mild", "healthy"],
            "cultural_notes": "Comfort food, easy to digest",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_096",
            "name": "Elumichai Sadam (Lemon Rice)",
            "name_sinhala": "ලෙමන් සදම්",
            "name_tamil": "எலுமிச்சை சாதம்",
            "category": "Rice Dish",
            "region": "Jaffna",
            "description": "Tangy lemon-flavored rice",
            "ingredients": ["2 cups cooked rice", "Juice of 2 lemons", "1 tsp mustard seeds", "1 tsp urad dal", "2 green chilies", "10 cashew nuts", "10 curry leaves", "1/2 tsp turmeric", "3 tbsp oil", "Salt"],
            "instructions": ["Cook rice and cool", "Heat oil and add mustard seeds", "Add urad dal and cashews", "Add curry leaves and chilies", "Add turmeric", "Pour over rice", "Add lemon juice and salt", "Mix gently", "Serve at room temperature"],
            "prep_time_minutes": 10,
            "cook_time_minutes": 10,
            "servings": 4,
            "difficulty": "Easy",
            "tags": ["jaffna", "rice", "tangy", "quick"],
            "cultural_notes": "Popular travel food, stays fresh",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_097",
            "name": "Milagai Bajji (Chili Fritters)",
            "name_sinhala": "මිරිස් බජ්ජි",
            "name_tamil": "மிளகாய் பஜ்ஜி",
            "category": "Snack",
            "region": "Jaffna",
            "description": "Batter-fried green chilies",
            "ingredients": ["10 large green chilies", "1 cup gram flour", "1/4 cup rice flour", "1/2 tsp chili powder", "1/4 tsp asafoetida", "1/2 tsp baking soda", "Salt to taste", "Water for batter", "Oil for frying"],
            "instructions": ["Slit chilies lengthwise, remove seeds", "Mix flours, chili powder, asafoetida, salt", "Add water to make thick batter", "Add baking soda just before frying", "Dip chilies in batter", "Deep fry until golden", "Drain and serve hot", "Serve with chutney"],
            "prep_time_minutes": 15,
            "cook_time_minutes": 15,
            "servings": 10,
            "difficulty": "Easy",
            "tags": ["jaffna", "snack", "fried", "spicy"],
            "cultural_notes": "Rainy day favorite snack",
            "authenticity_score": 0.95
        },
        {
            "id": "recipe_098",
            "name": "Tomato Thokku (Tomato Chutney)",
            "name_sinhala": "තක්කාලි තොක්කු",
            "name_tamil": "தக்காளி தொக்கு",
            "category": "Sambol",
            "region": "Jaffna",
            "description": "Spicy tomato preserve",
            "ingredients": ["1kg tomatoes, chopped", "10 garlic cloves", "2 tbsp chili powder", "1 tsp mustard seeds", "1 tsp fenugreek seeds", "10 curry leaves", "1/2 cup oil", "Salt to taste", "1 tsp jaggery"],
            "instructions": ["Heat oil and add mustard, fenugreek", "Add garlic and fry", "Add tomatoes and salt", "Cook until soft and mushy", "Add chili powder", "Cook until oil separates", "Add curry leaves and jaggery", "Cool and store"],
            "prep_time_minutes": 10,
            "cook_time_minutes": 30,
            "servings": 20,
            "difficulty": "Easy",
            "tags": ["jaffna", "condiment", "spicy", "preserve"],
            "cultural_notes": "Long-lasting condiment, stored in clay pots",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_099",
            "name": "Idli (Steamed Rice Cakes)",
            "name_sinhala": "ඉඩ්ලි",
            "name_tamil": "இட்லி",
            "category": "Bread",
            "region": "Jaffna",
            "description": "Soft steamed fermented rice cakes",
            "ingredients": ["2 cups parboiled rice", "1 cup urad dal", "1 tsp fenugreek", "Salt to taste", "Water for grinding"],
            "instructions": ["Soak rice, dal, fenugreek separately for 6 hours", "Grind dal to fluffy batter", "Grind rice to slightly coarse batter", "Mix both batters", "Add salt and ferment overnight", "Pour into greased idli molds", "Steam for 12-15 minutes", "Serve hot with sambar and chutney"],
            "prep_time_minutes": 20,
            "cook_time_minutes": 15,
            "servings": 20,
            "difficulty": "Medium",
            "tags": ["jaffna", "breakfast", "fermented", "healthy"],
            "cultural_notes": "Healthy breakfast, easy to digest",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_100",
            "name": "Pongal (Savory Rice)",
            "name_sinhala": "පොංගල්",
            "name_tamil": "பொங்கல்",
            "category": "Rice Dish",
            "region": "Jaffna",
            "description": "Creamy rice and lentil dish",
            "ingredients": ["1 cup rice", "1/2 cup moong dal", "1 tsp cumin seeds", "1 tsp black pepper", "1 inch ginger, chopped", "10 cashew nuts", "10 curry leaves", "4 cups water", "3 tbsp ghee", "Salt"],
            "instructions": ["Dry roast dal lightly", "Cook rice and dal together until very soft", "Mash slightly", "Heat ghee and add cumin, pepper", "Add ginger, cashews, curry leaves", "Pour over rice mixture", "Add salt and mix", "Serve hot with chutney"],
            "prep_time_minutes": 10,
            "cook_time_minutes": 25,
            "servings": 4,
            "difficulty": "Easy",
            "tags": ["jaffna", "rice", "comfort", "festive"],
            "cultural_notes": "Made during Pongal festival, comfort food",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_101",
            "name": "Bonda (Potato Fritters)",
            "name_sinhala": "බොන්ඩා",
            "name_tamil": "போண்டா",
            "category": "Snack",
            "region": "Jaffna",
            "description": "Spiced potato balls in gram flour batter",
            "ingredients": ["4 potatoes, boiled and mashed", "2 onions, chopped", "2 green chilies", "1 tsp ginger, minced", "10 curry leaves", "1 cup gram flour", "1/2 tsp chili powder", "1/4 tsp asafoetida", "1/2 tsp baking soda", "Oil for frying", "Salt"],
            "instructions": ["Mix mashed potato with onions, chilies, ginger, curry leaves", "Add salt and shape into small balls", "Make batter with gram flour, chili powder, asafoetida, salt", "Add baking soda just before frying", "Dip potato balls in batter", "Deep fry until golden", "Serve hot with chutney"],
            "prep_time_minutes": 20,
            "cook_time_minutes": 20,
            "servings": 15,
            "difficulty": "Medium",
            "tags": ["jaffna", "snack", "fried", "popular"],
            "cultural_notes": "Popular tea-time snack",
            "authenticity_score": 0.95
        },
        {
            "id": "recipe_102",
            "name": "Kanji (Rice Porridge)",
            "name_sinhala": "කඤ්ජි",
            "name_tamil": "கஞ்சி",
            "category": "Rice Dish",
            "region": "Jaffna",
            "description": "Simple rice porridge, comfort food",
            "ingredients": ["1 cup rice", "6 cups water", "1 tsp salt", "1 tsp cumin seeds", "1/2 tsp pepper", "1 tbsp ghee"],
            "instructions": ["Wash rice", "Boil with water until very soft and creamy", "Add salt", "Mash slightly", "Temper cumin and pepper in ghee", "Pour over kanji", "Serve hot with papadum and pickle"],
            "prep_time_minutes": 5,
            "cook_time_minutes": 30,
            "servings": 4,
            "difficulty": "Easy",
            "tags": ["jaffna", "comfort", "simple", "healing"],
            "cultural_notes": "Given to sick people, easy to digest",
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
    
    print(f"OK Added {len(recipes)} Jaffna Tamil recipes (IDs 078-102)")
    print(f"OK Total recipes now: {len(all_recipes)}")
    print(f"OK Saved to: {output_dir}")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("BATCH 3: JAFFNA TAMIL SPECIALTIES")
    print("="*70 + "\n")
    recipes = generate_batch_3_jaffna_recipes()
    save_recipes(recipes)
    print("\nOK Batch 3 Complete! Northern Sri Lankan cuisine added!")