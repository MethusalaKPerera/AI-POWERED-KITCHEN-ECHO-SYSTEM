#!/usr/bin/env python3
"""
Quick Recipe Generator
Generates 20 more authentic Sri Lankan recipes for dataset expansion
"""

import json
from pathlib import Path
from datetime import datetime

def generate_additional_recipes():
    """Generate 20 more Sri Lankan recipes"""
    
    recipes = [
        {
            "id": "recipe_004",
            "name": "Fish Curry (Malu Curry)",
            "name_sinhala": "මාළු කරිය",
            "name_tamil": "மீன் கறி",
            "category": "Curry",
            "region": "Coastal",
            "description": "A tangy fish curry with goraka (garcinia) and coconut milk",
            "ingredients": [
                "500g fish (tuna or mackerel), cut into pieces",
                "300ml coconut milk",
                "2 pieces goraka (garcinia)",
                "2 tbsp curry powder",
                "1 tsp chili powder",
                "1 tsp turmeric",
                "1 large onion, sliced",
                "4 cloves garlic, minced",
                "1 inch ginger, minced",
                "2 green chilies",
                "1 sprig curry leaves",
                "2 tbsp oil",
                "Salt to taste"
            ],
            "instructions": [
                "Marinate fish with turmeric and salt for 15 minutes",
                "Soak goraka in water for 10 minutes",
                "Heat oil and sauté onions, garlic, and ginger",
                "Add curry powder and chili powder",
                "Add goraka water and bring to boil",
                "Add fish pieces gently",
                "Simmer for 15 minutes",
                "Add coconut milk and curry leaves",
                "Cook for 5 more minutes without stirring too much"
            ],
            "prep_time_minutes": 20,
            "cook_time_minutes": 25,
            "servings": 4,
            "difficulty": "Medium",
            "tags": ["seafood", "tangy", "coconut-based", "traditional"],
            "cultural_notes": "Goraka gives this curry its distinctive sour taste, popular in coastal regions",
            "authenticity_score": 0.95
        },
        {
            "id": "recipe_005",
            "name": "Potato Curry (Ala Curry)",
            "name_sinhala": "අල කරිය",
            "name_tamil": "உருளைக்கிழங்கு கறி",
            "category": "Curry",
            "region": "General",
            "description": "Simple and flavorful potato curry, an everyday Sri Lankan staple",
            "ingredients": [
                "500g potatoes, cubed",
                "200ml coconut milk",
                "1 tbsp curry powder",
                "1 tsp chili powder",
                "1/2 tsp turmeric",
                "1 onion, sliced",
                "1 sprig curry leaves",
                "1 tsp mustard seeds",
                "2 green chilies",
                "2 tbsp oil",
                "Salt to taste"
            ],
            "instructions": [
                "Heat oil and add mustard seeds",
                "Add curry leaves and onions",
                "Add curry powder, chili, turmeric",
                "Add potato cubes and mix well",
                "Add water to cover and simmer until potatoes are tender",
                "Add coconut milk and simmer for 5 minutes",
                "Adjust seasoning"
            ],
            "prep_time_minutes": 10,
            "cook_time_minutes": 20,
            "servings": 4,
            "difficulty": "Easy",
            "tags": ["vegetarian", "everyday", "simple", "coconut-based"],
            "cultural_notes": "A daily staple in Sri Lankan households, often served with rice and dhal",
            "authenticity_score": 0.98
        },
        {
            "id": "recipe_006",
            "name": "Egg Curry (Bittara Curry)",
            "name_sinhala": "බිත්තර කරිය",
            "name_tamil": "முட்டை கறி",
            "category": "Curry",
            "region": "General",
            "description": "Hard-boiled eggs in rich coconut gravy",
            "ingredients": [
                "6 hard-boiled eggs",
                "300ml coconut milk",
                "2 tbsp curry powder",
                "1 tsp chili powder",
                "1 tsp turmeric",
                "2 onions, sliced",
                "3 cloves garlic",
                "1 sprig curry leaves",
                "2 green chilies",
                "2 tbsp oil",
                "Salt to taste"
            ],
            "instructions": [
                "Peel and halve the boiled eggs",
                "Lightly fry eggs until golden, set aside",
                "In same pan, sauté onions and garlic",
                "Add curry powder, chili, turmeric",
                "Add coconut milk and simmer",
                "Gently add eggs to the gravy",
                "Simmer for 10 minutes",
                "Garnish with curry leaves"
            ],
            "prep_time_minutes": 15,
            "cook_time_minutes": 20,
            "servings": 4,
            "difficulty": "Easy",
            "tags": ["protein-rich", "everyday", "coconut-based"],
            "cultural_notes": "Popular breakfast curry, often eaten with bread or roti",
            "authenticity_score": 0.92
        },
        {
            "id": "recipe_007",
            "name": "String Hoppers (Idiyappam)",
            "name_sinhala": "ඉඳි ආප්ප",
            "name_tamil": "இடியப்பம்",
            "category": "Bread",
            "region": "General",
            "description": "Steamed rice noodle cakes, a breakfast favorite",
            "ingredients": [
                "2 cups rice flour",
                "2 cups water",
                "1 tsp salt",
                "Oil for greasing"
            ],
            "instructions": [
                "Boil water with salt",
                "Slowly add rice flour while stirring",
                "Mix to form a dough",
                "Let cool slightly",
                "Fill string hopper press with dough",
                "Press onto greased molds in circular patterns",
                "Steam for 5-7 minutes",
                "Serve hot"
            ],
            "prep_time_minutes": 20,
            "cook_time_minutes": 10,
            "servings": 6,
            "difficulty": "Medium",
            "tags": ["breakfast", "steamed", "traditional", "gluten-free"],
            "cultural_notes": "Traditional breakfast served with curry and sambol",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_008",
            "name": "Hoppers (Appa)",
            "name_sinhala": "ආප්ප",
            "name_tamil": "ஆப்பம்",
            "category": "Bread",
            "region": "General",
            "description": "Bowl-shaped fermented rice pancakes with crispy edges",
            "ingredients": [
                "2 cups rice flour",
                "1/2 cup coconut milk",
                "1 tsp sugar",
                "1 tsp yeast",
                "1 cup warm water",
                "1/2 tsp salt"
            ],
            "instructions": [
                "Mix yeast with warm water and sugar, let sit 10 minutes",
                "Combine rice flour and salt",
                "Add yeast mixture and coconut milk",
                "Mix to smooth batter",
                "Let ferment for 4-6 hours",
                "Heat hopper pan, grease lightly",
                "Pour batter and swirl to form bowl shape",
                "Cover and cook until edges are crispy",
                "Center should be soft"
            ],
            "prep_time_minutes": 20,
            "cook_time_minutes": 5,
            "servings": 8,
            "difficulty": "Hard",
            "tags": ["breakfast", "fermented", "traditional", "crispy"],
            "cultural_notes": "Often served with egg in the center for egg hoppers",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_009",
            "name": "Kottu Roti",
            "name_sinhala": "කොත්තු රොටි",
            "name_tamil": "கொத்து ரொட்டி",
            "category": "Rice Dish",
            "region": "General",
            "description": "Chopped roti stir-fried with vegetables and meat",
            "ingredients": [
                "4 godamba roti, chopped",
                "200g chicken, diced",
                "1 onion, sliced",
                "2 carrots, julienned",
                "1 leek, sliced",
                "2 eggs",
                "2 tbsp curry powder",
                "1 tsp chili powder",
                "3 tbsp oil",
                "Salt to taste"
            ],
            "instructions": [
                "Heat oil in large wok or griddle",
                "Fry chicken until cooked",
                "Add onions, carrots, leek",
                "Add curry powder and chili",
                "Push to side, scramble eggs",
                "Add chopped roti",
                "Chop and mix everything together with metal spatulas",
                "Season and serve hot"
            ],
            "prep_time_minutes": 15,
            "cook_time_minutes": 15,
            "servings": 4,
            "difficulty": "Medium",
            "tags": ["street-food", "spicy", "dinner", "popular"],
            "cultural_notes": "Famous Sri Lankan street food with rhythmic chopping sounds",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_010",
            "name": "Lamprais",
            "name_sinhala": "ලම්ප්‍රයිස්",
            "name_tamil": "லம்ப்ரைஸ்",
            "category": "Rice Dish",
            "region": "Burgher",
            "description": "Dutch Burgher rice packet with multiple curries baked in banana leaf",
            "ingredients": [
                "2 cups basmati rice",
                "200g chicken curry",
                "100g beef curry",
                "4 eggs, hard-boiled",
                "Brinjal moju",
                "Seeni sambol",
                "Banana leaves",
                "2 cups chicken stock"
            ],
            "instructions": [
                "Cook rice in chicken stock",
                "Cut banana leaves into squares",
                "Place rice in center of leaf",
                "Add chicken curry, beef curry, egg, moju, sambol",
                "Fold banana leaf into packet",
                "Bake at 180°C for 20 minutes",
                "Serve hot in the packet"
            ],
            "prep_time_minutes": 60,
            "cook_time_minutes": 40,
            "servings": 4,
            "difficulty": "Hard",
            "tags": ["special-occasion", "burgher", "baked", "festive"],
            "cultural_notes": "Dutch Burgher specialty, traditionally served at parties",
            "authenticity_score": 0.95
        },
        {
            "id": "recipe_011",
            "name": "Watalappan",
            "name_sinhala": "වටලප්පන්",
            "name_tamil": "வாதளப்பான்",
            "category": "Dessert",
            "region": "Malay",
            "description": "Sri Lankan coconut custard pudding with jaggery",
            "ingredients": [
                "6 eggs",
                "400ml coconut milk",
                "200g jaggery, melted",
                "1/2 tsp cardamom powder",
                "1/2 tsp nutmeg",
                "Few cashew nuts"
            ],
            "instructions": [
                "Beat eggs well",
                "Add melted jaggery",
                "Add coconut milk, cardamom, nutmeg",
                "Strain mixture",
                "Pour into greased mold",
                "Add cashews on top",
                "Steam for 30-40 minutes until set",
                "Cool and serve"
            ],
            "prep_time_minutes": 15,
            "cook_time_minutes": 40,
            "servings": 8,
            "difficulty": "Medium",
            "tags": ["dessert", "sweet", "steamed", "traditional"],
            "cultural_notes": "Malay-origin dessert, essential at Eid celebrations",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_012",
            "name": "Seeni Sambol",
            "name_sinhala": "සීනි සම්බෝල",
            "name_tamil": "சீனி சம்பல்",
            "category": "Sambol",
            "region": "General",
            "description": "Caramelized onion sambol with Maldive fish",
            "ingredients": [
                "4 large onions, sliced thin",
                "3 tbsp Maldive fish",
                "2 tbsp chili powder",
                "2 tbsp tamarind paste",
                "2 tbsp sugar",
                "1 sprig curry leaves",
                "3 tbsp oil",
                "Salt to taste"
            ],
            "instructions": [
                "Heat oil in pan",
                "Add onions and fry until golden",
                "Add curry leaves",
                "Add chili powder and Maldive fish",
                "Add tamarind paste and sugar",
                "Cook until caramelized and thick",
                "Cool and store"
            ],
            "prep_time_minutes": 10,
            "cook_time_minutes": 30,
            "servings": 8,
            "difficulty": "Medium",
            "tags": ["condiment", "sweet-spicy", "caramelized"],
            "cultural_notes": "Essential condiment for bread, served at breakfast",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_013",
            "name": "Kiribath (Milk Rice)",
            "name_sinhala": "කිරිබත්",
            "name_tamil": "பால் சாதம்",
            "category": "Rice Dish",
            "region": "General",
            "description": "Rice cooked in coconut milk, cut into diamond shapes",
            "ingredients": [
                "2 cups white rice",
                "400ml coconut milk",
                "2 cups water",
                "1 tsp salt"
            ],
            "instructions": [
                "Wash rice thoroughly",
                "Cook rice in water until almost done",
                "Add coconut milk and salt",
                "Simmer until thick and creamy",
                "Pour onto flat plate",
                "Let cool and set",
                "Cut into diamond shapes",
                "Serve with lunu miris"
            ],
            "prep_time_minutes": 5,
            "cook_time_minutes": 25,
            "servings": 6,
            "difficulty": "Easy",
            "tags": ["traditional", "breakfast", "ceremonial", "simple"],
            "cultural_notes": "Ceremonial dish served at New Year and auspicious occasions",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_014",
            "name": "Isso Wade (Prawn Fritters)",
            "name_sinhala": "ඉස්සෝ වඩේ",
            "name_tamil": "இறால் வடை",
            "category": "Snack",
            "region": "General",
            "description": "Crispy lentil fritters with prawns",
            "ingredients": [
                "1 cup urad dal, soaked",
                "200g prawns, chopped",
                "2 green chilies, chopped",
                "1 onion, chopped fine",
                "1 sprig curry leaves",
                "1/2 tsp fennel seeds",
                "Oil for frying",
                "Salt to taste"
            ],
            "instructions": [
                "Grind soaked dal coarsely",
                "Mix in prawns, chilies, onion, curry leaves, fennel",
                "Add salt",
                "Heat oil for deep frying",
                "Shape mixture into small patties",
                "Fry until golden brown",
                "Drain and serve hot"
            ],
            "prep_time_minutes": 20,
            "cook_time_minutes": 15,
            "servings": 6,
            "difficulty": "Medium",
            "tags": ["snack", "fried", "seafood", "crispy"],
            "cultural_notes": "Popular tea-time snack, sold by street vendors",
            "authenticity_score": 0.95
        },
        {
            "id": "recipe_015",
            "name": "Gotukola Sambol",
            "name_sinhala": "ගොටුකොළ සම්බෝල",
            "name_tamil": "வல்லாரை சம்பல்",
            "category": "Sambol",
            "region": "General",
            "description": "Gotu kola leaves salad with coconut",
            "ingredients": [
                "2 cups gotu kola leaves, chopped",
                "1 cup grated coconut",
                "1 small onion, sliced",
                "2 green chilies",
                "1 tbsp lime juice",
                "1/2 tsp chili powder",
                "Salt to taste",
                "Maldive fish (optional)"
            ],
            "instructions": [
                "Wash and finely chop gotu kola leaves",
                "Mix with grated coconut",
                "Add sliced onions and green chilies",
                "Add lime juice, chili powder, salt",
                "Mix well",
                "Add Maldive fish if using",
                "Serve fresh"
            ],
            "prep_time_minutes": 15,
            "cook_time_minutes": 0,
            "servings": 4,
            "difficulty": "Easy",
            "tags": ["healthy", "no-cook", "herbal", "salad"],
            "cultural_notes": "Considered very healthy, gotu kola is believed to boost memory",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_016",
            "name": "Pittu",
            "name_sinhala": "පිට්ටු",
            "name_tamil": "புட்டு",
            "category": "Bread",
            "region": "General",
            "description": "Steamed cylinders of rice flour and coconut",
            "ingredients": [
                "2 cups rice flour",
                "1 cup grated coconut",
                "Water as needed",
                "Salt to taste"
            ],
            "instructions": [
                "Mix rice flour with water to get breadcrumb consistency",
                "Add salt",
                "Layer rice flour and coconut in pittu maker",
                "Alternate layers",
                "Steam for 10-15 minutes",
                "Remove and serve hot",
                "Serve with curry or banana and sugar"
            ],
            "prep_time_minutes": 15,
            "cook_time_minutes": 15,
            "servings": 4,
            "difficulty": "Medium",
            "tags": ["breakfast", "steamed", "traditional"],
            "cultural_notes": "Traditional breakfast, can be eaten sweet or savory",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_017",
            "name": "Pol Roti (Coconut Roti)",
            "name_sinhala": "පොල් රොටි",
            "name_tamil": "தேங்காய் ரொட்டி",
            "category": "Bread",
            "region": "General",
            "description": "Whole wheat flatbread with coconut",
            "ingredients": [
                "2 cups wheat flour",
                "1 cup grated coconut",
                "1 onion, chopped fine",
                "2 green chilies, chopped",
                "Water as needed",
                "Salt to taste",
                "Oil for cooking"
            ],
            "instructions": [
                "Mix flour, coconut, onion, chilies, salt",
                "Add water to form dough",
                "Knead well",
                "Divide into balls",
                "Roll into thin circles",
                "Cook on hot griddle with oil",
                "Flip when brown spots appear",
                "Serve hot"
            ],
            "prep_time_minutes": 20,
            "cook_time_minutes": 20,
            "servings": 6,
            "difficulty": "Easy",
            "tags": ["breakfast", "flatbread", "coconut", "quick"],
            "cultural_notes": "Popular breakfast roti, often served with curry",
            "authenticity_score": 0.98
        },
        {
            "id": "recipe_018",
            "name": "Parippu (Red Lentil Curry)",
            "name_sinhala": "පරිප්පු",
            "name_tamil": "பருப்பு",
            "category": "Curry",
            "region": "General",
            "description": "Simple red lentil curry, daily staple",
            "ingredients": [
                "1 cup red lentils",
                "200ml coconut milk",
                "2 cups water",
                "1 tsp turmeric",
                "1 tsp cumin seeds",
                "2 green chilies",
                "1 sprig curry leaves",
                "1 onion, sliced",
                "2 tbsp oil",
                "Salt to taste"
            ],
            "instructions": [
                "Wash lentils",
                "Boil with water and turmeric until soft",
                "Add coconut milk",
                "For tempering: heat oil, add cumin",
                "Add curry leaves, onions, chilies",
                "Pour over lentils",
                "Mix and serve"
            ],
            "prep_time_minutes": 5,
            "cook_time_minutes": 20,
            "servings": 4,
            "difficulty": "Easy",
            "tags": ["everyday", "vegetarian", "protein-rich", "simple"],
            "cultural_notes": "Eaten daily with rice, essential Sri Lankan dish",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_019",
            "name": "Devilled Chicken",
            "name_sinhala": "ඩෙවල්ඩ් චිකන්",
            "name_tamil": "டெவில்டு சிக்கன்",
            "category": "Curry",
            "region": "Burgher",
            "description": "Spicy stir-fried chicken with peppers",
            "ingredients": [
                "500g chicken, cubed",
                "2 bell peppers, cubed",
                "2 onions, cubed",
                "3 tbsp chili paste",
                "2 tbsp tomato ketchup",
                "2 tbsp soy sauce",
                "1 tbsp vinegar",
                "3 cloves garlic",
                "3 tbsp oil",
                "Salt and pepper"
            ],
            "instructions": [
                "Marinate chicken with salt, pepper, garlic",
                "Heat oil and fry chicken until golden",
                "Remove chicken",
                "Sauté onions and peppers",
                "Add chili paste, ketchup, soy sauce, vinegar",
                "Add chicken back",
                "Toss until coated",
                "Serve hot"
            ],
            "prep_time_minutes": 15,
            "cook_time_minutes": 20,
            "servings": 4,
            "difficulty": "Medium",
            "tags": ["spicy", "stir-fry", "popular", "indo-chinese"],
            "cultural_notes": "Burgher-style dish, very popular in restaurants",
            "authenticity_score": 0.85
        },
        {
            "id": "recipe_020",
            "name": "Kokis",
            "name_sinhala": "කොකිස්",
            "name_tamil": "அச்சப்பம்",
            "category": "Dessert",
            "region": "General",
            "description": "Crispy flower-shaped cookies for New Year",
            "ingredients": [
                "2 cups rice flour",
                "1/2 cup coconut milk",
                "2 eggs",
                "1 tsp sugar",
                "1/2 tsp salt",
                "Oil for frying"
            ],
            "instructions": [
                "Beat eggs with sugar",
                "Add coconut milk",
                "Gradually add rice flour and salt",
                "Mix to smooth batter",
                "Heat oil for deep frying",
                "Dip kokis mold in hot oil",
                "Dip mold in batter",
                "Fry in hot oil until crispy",
                "Remove and cool"
            ],
            "prep_time_minutes": 15,
            "cook_time_minutes": 30,
            "servings": 20,
            "difficulty": "Hard",
            "tags": ["dessert", "crispy", "new-year", "festive"],
            "cultural_notes": "Essential Sinhala and Tamil New Year sweet",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_021",
            "name": "Beetroot Curry",
            "name_sinhala": "බීට්රූට් කරිය",
            "name_tamil": "பீட்ரூட் கறி",
            "category": "Curry",
            "region": "General",
            "description": "Vibrant beetroot curry with coconut",
            "ingredients": [
                "3 large beetroots, cubed",
                "200ml coconut milk",
                "1 onion, sliced",
                "1 tbsp curry powder",
                "1/2 tsp turmeric",
                "1 tsp mustard seeds",
                "1 sprig curry leaves",
                "2 green chilies",
                "2 tbsp oil",
                "Salt to taste"
            ],
            "instructions": [
                "Boil beetroot until tender",
                "Heat oil, add mustard seeds",
                "Add onion, curry leaves, chilies",
                "Add curry powder and turmeric",
                "Add boiled beetroot",
                "Add coconut milk",
                "Simmer for 10 minutes",
                "Season and serve"
            ],
            "prep_time_minutes": 10,
            "cook_time_minutes": 30,
            "servings": 4,
            "difficulty": "Easy",
            "tags": ["vegetarian", "colorful", "healthy"],
            "cultural_notes": "Popular vegetable curry, loved for its color",
            "authenticity_score": 0.90
        },
        {
            "id": "recipe_022",
            "name": "Cashew Curry",
            "name_sinhala": "කජු කරිය",
            "name_tamil": "முந்திரி கறி",
            "category": "Curry",
            "region": "General",
            "description": "Rich curry with cashew nuts",
            "ingredients": [
                "1 cup raw cashews",
                "300ml coconut milk",
                "1 onion, sliced",
                "2 tbsp curry powder",
                "1 tsp chili powder",
                "1/2 tsp turmeric",
                "1 sprig curry leaves",
                "2 green chilies",
                "2 tbsp oil",
                "Salt to taste"
            ],
            "instructions": [
                "Soak cashews for 1 hour",
                "Heat oil and sauté onions",
                "Add curry powder, chili, turmeric",
                "Add cashews and mix",
                "Add coconut milk",
                "Simmer until cashews are soft",
                "Add curry leaves and chilies",
                "Serve hot"
            ],
            "prep_time_minutes": 10,
            "cook_time_minutes": 25,
            "servings": 4,
            "difficulty": "Medium",
            "tags": ["vegetarian", "rich", "special-occasion"],
            "cultural_notes": "Considered a luxury curry, often served at special meals",
            "authenticity_score": 0.92
        },
        {
            "id": "recipe_023",
            "name": "Lunu Miris",
            "name_sinhala": "ලුණු මිරිස්",
            "name_tamil": "உப்பு மிளகாய்",
            "category": "Sambol",
            "region": "General",
            "description": "Simple onion and chili paste",
            "ingredients": [
                "5 dried red chilies",
                "1 small onion, chopped",
                "1/2 tsp Maldive fish",
                "1 tbsp lime juice",
                "Salt to taste"
            ],
            "instructions": [
                "Grind chilies coarsely",
                "Add onion and grind",
                "Add Maldive fish and salt",
                "Add lime juice",
                "Mix to paste consistency",
                "Serve with kiribath or bread"
            ],
            "prep_time_minutes": 10,
            "cook_time_minutes": 0,
            "servings": 4,
            "difficulty": "Easy",
            "tags": ["condiment", "spicy", "traditional", "no-cook"],
            "cultural_notes": "Essential accompaniment to kiribath at breakfast",
            "authenticity_score": 1.0
        }
    ]
    
    return recipes

def save_recipes(recipes, output_dir='rag/data/recipes'):
    """Save recipes to database"""
    
    # Load existing recipes
    db_path = Path(output_dir) / 'recipe_database.json'
    
    try:
        with open(db_path, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
            existing_recipes = existing_data.get('recipes', [])
    except FileNotFoundError:
        existing_recipes = []
    
    # Combine recipes
    all_recipes = existing_recipes + recipes
    
    # Save combined database
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump({
            'total_recipes': len(all_recipes),
            'created_date': datetime.now().isoformat(),
            'recipes': all_recipes
        }, f, indent=2, ensure_ascii=False)
    
    # Save individual files
    for recipe in recipes:
        recipe_file = Path(output_dir) / f"{recipe['id']}.json"
        with open(recipe_file, 'w', encoding='utf-8') as f:
            json.dump(recipe, f, indent=2, ensure_ascii=False)
    
    print(f"OK Added {len(recipes)} new recipes")
    print(f"OK Total recipes: {len(all_recipes)}")
    print(f"OK Saved to: {output_dir}")

if __name__ == "__main__":
    print("\nGenerating 20 additional Sri Lankan recipes...")
    recipes = generate_additional_recipes()
    save_recipes(recipes)
    print("\nOK Complete! Run pp1_preparation.py to update stats.")