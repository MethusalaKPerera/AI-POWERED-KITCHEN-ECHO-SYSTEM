#!/usr/bin/env python3
"""
Quick Recipe Generator - Batch 2
Generates 27 more authentic Sri Lankan recipes (IDs 024-050)
"""

import json
from pathlib import Path
from datetime import datetime

def generate_batch_2_recipes():
    """Generate 27 more Sri Lankan recipes"""
    
    recipes = [
        {
            "id": "recipe_024",
            "name": "Ambul Thiyal (Sour Fish Curry)",
            "name_sinhala": "අඹුල් තියල",
            "name_tamil": "புளி மீன் கறி",
            "category": "Curry",
            "region": "Southern",
            "description": "Dry fish curry with goraka, a Southern specialty",
            "ingredients": ["500g tuna, cubed", "5 pieces goraka", "2 tbsp curry powder", "1 tsp chili powder", "1 tsp black pepper", "2 onions, sliced", "1 sprig curry leaves", "1 stick cinnamon", "2 tbsp oil", "Salt to taste"],
            "instructions": ["Soak goraka in water", "Marinate fish with curry powder, chili, pepper, salt", "Heat oil and fry onions", "Add fish and goraka water", "Add cinnamon and curry leaves", "Cook on low heat until dry", "No coconut milk used", "Serve at room temperature"],
            "prep_time_minutes": 15,
            "cook_time_minutes": 45,
            "servings": 6,
            "difficulty": "Medium",
            "tags": ["dry-curry", "sour", "traditional", "southern"],
            "cultural_notes": "Traditional Southern dish that keeps for days without refrigeration",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_025",
            "name": "Isso Curry (Prawn Curry)",
            "name_sinhala": "ඉස්සෝ කරිය",
            "name_tamil": "இறால் கறி",
            "category": "Curry",
            "region": "Coastal",
            "description": "Rich prawn curry with coconut milk",
            "ingredients": ["500g prawns, cleaned", "400ml coconut milk", "2 tbsp curry powder", "1 tsp chili powder", "1 tsp turmeric", "2 onions, sliced", "4 cloves garlic", "1 inch ginger", "1 sprig curry leaves", "3 green chilies", "2 tbsp oil", "Salt to taste"],
            "instructions": ["Devein and clean prawns", "Marinate with turmeric and salt", "Heat oil, sauté onions, garlic, ginger", "Add curry powder and chili", "Add thin coconut milk", "Add prawns and simmer", "Add thick coconut milk", "Add curry leaves", "Cook for 5 minutes"],
            "prep_time_minutes": 20,
            "cook_time_minutes": 15,
            "servings": 4,
            "difficulty": "Medium",
            "tags": ["seafood", "coconut-based", "spicy"],
            "cultural_notes": "Coastal specialty, best with fresh prawns",
            "authenticity_score": 0.95
        },
        {
            "id": "recipe_026",
            "name": "Brinjal Moju (Eggplant Pickle)",
            "name_sinhala": "වම්බටු මොජු",
            "name_tamil": "கத்தரிக்காய் ஊறுகாய்",
            "category": "Sambol",
            "region": "General",
            "description": "Sweet and sour eggplant pickle",
            "ingredients": ["4 large brinjals, sliced", "3 onions, sliced", "2 tbsp mustard seeds", "10 curry leaves", "3 tbsp vinegar", "3 tbsp sugar", "2 tsp chili powder", "Oil for frying", "Salt to taste"],
            "instructions": ["Fry brinjal slices until golden", "Fry onions separately", "In same oil, add mustard seeds", "Add curry leaves", "Add fried brinjal and onions", "Add vinegar, sugar, chili, salt", "Cook until thick", "Cool and store"],
            "prep_time_minutes": 15,
            "cook_time_minutes": 30,
            "servings": 8,
            "difficulty": "Medium",
            "tags": ["pickle", "sweet-sour", "fried", "condiment"],
            "cultural_notes": "Essential accompaniment for rice and curry, stores well",
            "authenticity_score": 0.95
        },
        {
            "id": "recipe_027",
            "name": "Kiri Hodi (Coconut Milk Gravy)",
            "name_sinhala": "කිරි හොදි",
            "name_tamil": "தேங்காய் பால் குழம்பு",
            "category": "Curry",
            "region": "General",
            "description": "Mild coconut milk curry, served with kiribath",
            "ingredients": ["400ml coconut milk", "1 onion, sliced", "2 green chilies", "1/2 tsp turmeric", "1 sprig curry leaves", "Juice of 1 lime", "Salt to taste"],
            "instructions": ["Heat coconut milk gently", "Add onions, chilies, curry leaves", "Add turmeric and salt", "Simmer for 10 minutes", "Add lime juice at the end", "Don't boil after adding lime", "Serve with kiribath"],
            "prep_time_minutes": 5,
            "cook_time_minutes": 15,
            "servings": 4,
            "difficulty": "Easy",
            "tags": ["mild", "vegetarian", "coconut-based", "traditional"],
            "cultural_notes": "Traditional accompaniment to kiribath at New Year",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_028",
            "name": "Cuttlefish Curry",
            "name_sinhala": "දැල්ල කරිය",
            "name_tamil": "கணவாய் கறி",
            "category": "Curry",
            "region": "Coastal",
            "description": "Tender cuttlefish in spicy curry",
            "ingredients": ["500g cuttlefish, cleaned and cut", "300ml coconut milk", "2 tbsp curry powder", "1 tbsp chili powder", "1 tsp turmeric", "2 onions, sliced", "1 sprig curry leaves", "2 tbsp tamarind paste", "3 tbsp oil", "Salt to taste"],
            "instructions": ["Clean cuttlefish thoroughly", "Cut into rings", "Heat oil and sauté onions", "Add curry powder, chili, turmeric", "Add cuttlefish and mix", "Add tamarind paste", "Add coconut milk", "Simmer until tender (30-40 min)", "Add curry leaves"],
            "prep_time_minutes": 25,
            "cook_time_minutes": 40,
            "servings": 4,
            "difficulty": "Medium",
            "tags": ["seafood", "spicy", "tangy"],
            "cultural_notes": "Requires slow cooking to make cuttlefish tender",
            "authenticity_score": 0.92
        },
        {
            "id": "recipe_029",
            "name": "Batu Moju (Bean Pickle)",
            "name_sinhala": "බෝංචි මොජු",
            "name_tamil": "பீன்ஸ் ஊறுகாய்",
            "category": "Sambol",
            "region": "General",
            "description": "Sweet and sour green bean pickle",
            "ingredients": ["300g green beans, cut", "2 onions, sliced", "2 tbsp mustard seeds", "2 tbsp vinegar", "2 tbsp sugar", "1 tbsp chili powder", "1 sprig curry leaves", "Oil for frying", "Salt to taste"],
            "instructions": ["Blanch beans in boiling water", "Drain well", "Fry beans until slightly crispy", "Fry onions separately", "In same oil, add mustard seeds", "Add curry leaves", "Add beans, onions", "Add vinegar, sugar, chili, salt", "Mix well and cool"],
            "prep_time_minutes": 15,
            "cook_time_minutes": 20,
            "servings": 6,
            "difficulty": "Easy",
            "tags": ["pickle", "vegetarian", "sweet-sour"],
            "cultural_notes": "Popular side dish that pairs well with rice",
            "authenticity_score": 0.90
        },
        {
            "id": "recipe_030",
            "name": "Achcharu (Mixed Pickle)",
            "name_sinhala": "අච්චාරු",
            "name_tamil": "ஊறுகாய்",
            "category": "Sambol",
            "region": "General",
            "description": "Mixed vegetable pickle with mustard",
            "ingredients": ["1 carrot, julienned", "1 cucumber, julienned", "1 onion, sliced", "2 green chilies", "2 tbsp mustard seeds", "2 tbsp vinegar", "1 tbsp sugar", "1 tsp chili powder", "1/2 tsp turmeric", "Salt to taste"],
            "instructions": ["Cut all vegetables into thin strips", "Mix with salt and turmeric", "Let sit for 30 minutes", "Squeeze out excess water", "Grind mustard seeds coarsely", "Mix vegetables with mustard, vinegar, sugar, chili", "Let marinate for 2 hours", "Serve chilled"],
            "prep_time_minutes": 20,
            "cook_time_minutes": 0,
            "servings": 6,
            "difficulty": "Easy",
            "tags": ["pickle", "no-cook", "vegetarian", "tangy"],
            "cultural_notes": "Popular snack pickle, sold by street vendors",
            "authenticity_score": 0.95
        },
        {
            "id": "recipe_031",
            "name": "Chicken Biryani Sri Lankan Style",
            "name_sinhala": "චිකන් බුරියානි",
            "name_tamil": "சிக்கன் பிரியாணி",
            "category": "Rice Dish",
            "region": "Muslim",
            "description": "Fragrant rice layered with spiced chicken",
            "ingredients": ["500g chicken", "2 cups basmati rice", "2 onions, sliced", "1/2 cup yogurt", "1 tbsp ginger-garlic paste", "1 tsp garam masala", "4 cloves", "2 cardamom", "1 cinnamon stick", "Saffron", "Mint leaves", "4 tbsp ghee", "Salt"],
            "instructions": ["Marinate chicken with yogurt, ginger-garlic, garam masala", "Cook rice 70% done", "Fry onions until golden", "Layer rice and chicken", "Sprinkle saffron, fried onions, mint", "Cover and cook on low heat (dum)", "Serve hot with raita"],
            "prep_time_minutes": 30,
            "cook_time_minutes": 45,
            "servings": 6,
            "difficulty": "Hard",
            "tags": ["rice-dish", "festive", "muslim", "layered"],
            "cultural_notes": "Popular at Muslim weddings and celebrations",
            "authenticity_score": 0.90
        },
        {
            "id": "recipe_032",
            "name": "Cutlets (Potato Croquettes)",
            "name_sinhala": "කට්ලට්",
            "name_tamil": "கட்லட்",
            "category": "Snack",
            "region": "Burgher",
            "description": "Spiced potato croquettes, breaded and fried",
            "ingredients": ["4 potatoes, boiled and mashed", "100g beef or chicken, minced", "1 onion, chopped", "2 green chilies", "1 tsp curry powder", "2 eggs", "Breadcrumbs", "Oil for frying", "Salt and pepper"],
            "instructions": ["Fry minced meat with onions, curry powder", "Mix with mashed potato", "Season with salt, pepper, chilies", "Shape into cylinders", "Dip in beaten egg", "Coat with breadcrumbs", "Deep fry until golden", "Serve hot"],
            "prep_time_minutes": 30,
            "cook_time_minutes": 20,
            "servings": 12,
            "difficulty": "Medium",
            "tags": ["snack", "fried", "burgher", "popular"],
            "cultural_notes": "Favorite tea-time snack, Burgher specialty",
            "authenticity_score": 0.88
        },
        {
            "id": "recipe_033",
            "name": "Patties (Curry Puffs)",
            "name_sinhala": "පැටිස්",
            "name_tamil": "பட்டீஸ்",
            "category": "Snack",
            "region": "Burgher",
            "description": "Flaky pastry filled with spiced meat or fish",
            "ingredients": ["2 cups flour", "100g butter", "1 egg", "200g beef or fish", "1 onion, chopped", "1 tbsp curry powder", "1 tsp chili powder", "Salt", "Oil for frying"],
            "instructions": ["Make pastry with flour, butter, egg", "Rest for 30 minutes", "Cook filling with meat, onions, curry powder", "Roll pastry thin", "Cut circles", "Fill with mixture", "Fold and seal edges", "Deep fry until golden"],
            "prep_time_minutes": 45,
            "cook_time_minutes": 20,
            "servings": 15,
            "difficulty": "Hard",
            "tags": ["snack", "fried", "flaky", "burgher"],
            "cultural_notes": "Popular street food and party snack",
            "authenticity_score": 0.90
        },
        {
            "id": "recipe_034",
            "name": "Murukku (Crispy Snack)",
            "name_sinhala": "මුරුක්කු",
            "name_tamil": "முறுக்கு",
            "category": "Snack",
            "region": "Tamil",
            "description": "Crispy spiral-shaped rice flour snack",
            "ingredients": ["2 cups rice flour", "1/2 cup urad dal flour", "1 tsp cumin seeds", "1 tsp sesame seeds", "1/2 tsp chili powder", "2 tbsp butter", "Salt to taste", "Oil for frying"],
            "instructions": ["Mix all dry ingredients", "Add melted butter", "Add water to form dough", "Fill murukku press", "Press spirals into hot oil", "Fry until golden and crispy", "Drain and cool", "Store in airtight container"],
            "prep_time_minutes": 20,
            "cook_time_minutes": 30,
            "servings": 20,
            "difficulty": "Medium",
            "tags": ["snack", "crispy", "tamil", "savory"],
            "cultural_notes": "Traditional Tamil snack for festivals",
            "authenticity_score": 0.95
        },
        {
            "id": "recipe_035",
            "name": "Wade (Lentil Fritters)",
            "name_sinhala": "වඩේ",
            "name_tamil": "வடை",
            "category": "Snack",
            "region": "Tamil",
            "description": "Savory lentil donuts, crispy outside, soft inside",
            "ingredients": ["1 cup urad dal, soaked", "2 green chilies", "1 onion, chopped", "1 sprig curry leaves", "1/2 tsp fennel seeds", "Salt to taste", "Oil for frying"],
            "instructions": ["Drain soaked dal", "Grind coarsely (not smooth)", "Add chilies, onions, curry leaves, fennel", "Add salt and mix", "Heat oil for frying", "Shape into donuts with hole in center", "Fry until golden brown", "Serve hot with sambol"],
            "prep_time_minutes": 20,
            "cook_time_minutes": 20,
            "servings": 12,
            "difficulty": "Medium",
            "tags": ["snack", "fried", "tamil", "protein-rich"],
            "cultural_notes": "Classic tea-time snack, sold everywhere",
            "authenticity_score": 0.98
        },
        {
            "id": "recipe_036",
            "name": "Kavum (Oil Cakes)",
            "name_sinhala": "කැවුම්",
            "name_tamil": "கவும்",
            "category": "Dessert",
            "region": "General",
            "description": "Deep-fried rice flour cakes with treacle",
            "ingredients": ["2 cups rice flour", "1 cup kithul treacle", "1/4 cup coconut milk", "1/2 tsp cardamom powder", "Salt pinch", "Oil for frying"],
            "instructions": ["Mix rice flour with treacle", "Add coconut milk to form thick batter", "Add cardamom and salt", "Let rest for 2 hours", "Heat oil for deep frying", "Drop spoonfuls of batter", "Fry until dark brown", "Drain and cool"],
            "prep_time_minutes": 20,
            "cook_time_minutes": 30,
            "servings": 20,
            "difficulty": "Medium",
            "tags": ["dessert", "sweet", "fried", "new-year"],
            "cultural_notes": "Essential New Year sweet, made with kithul treacle",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_037",
            "name": "Aggala (Sweet Balls)",
            "name_sinhala": "අග්ගල",
            "name_tamil": "அக்கல",
            "category": "Dessert",
            "region": "General",
            "description": "Sweet rice flour balls with coconut",
            "ingredients": ["2 cups roasted rice flour", "1 cup jaggery, melted", "1 cup grated coconut", "1/2 tsp cardamom powder", "Water as needed"],
            "instructions": ["Roast rice flour until fragrant", "Mix with melted jaggery", "Add grated coconut", "Add cardamom", "Add water to bind", "Shape into small balls", "Let dry for 2-3 hours", "Store in airtight container"],
            "prep_time_minutes": 30,
            "cook_time_minutes": 10,
            "servings": 30,
            "difficulty": "Easy",
            "tags": ["dessert", "sweet", "no-fry", "traditional"],
            "cultural_notes": "Healthy traditional sweet, no oil used",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_038",
            "name": "Athirasa (Jaggery Pancakes)",
            "name_sinhala": "අතිරස",
            "name_tamil": "அதிரசம்",
            "category": "Dessert",
            "region": "General",
            "description": "Sweet rice flour pancakes fried in oil",
            "ingredients": ["2 cups rice flour", "1 cup jaggery", "1/2 cup water", "1/2 tsp cardamom", "Oil for deep frying"],
            "instructions": ["Melt jaggery in water", "Strain and cool", "Mix with rice flour to form dough", "Add cardamom", "Let rest overnight", "Heat oil for frying", "Flatten small balls into discs", "Fry until puffed and golden", "Drain and cool"],
            "prep_time_minutes": 20,
            "cook_time_minutes": 30,
            "servings": 20,
            "difficulty": "Medium",
            "tags": ["dessert", "sweet", "fried", "festive"],
            "cultural_notes": "Popular Tamil and Sinhala sweet for festivals",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_039",
            "name": "Kalu Dodol (Black Toffee)",
            "name_sinhala": "කළු දොඩොල්",
            "name_tamil": "கருப்பு டோடோல்",
            "category": "Dessert",
            "region": "General",
            "description": "Sticky black toffee made with kithul treacle",
            "ingredients": ["2 cups kithul treacle", "2 cups coconut milk", "1 cup rice flour", "1/2 cup cashews, chopped", "1/2 tsp cardamom"],
            "instructions": ["Mix rice flour with coconut milk", "Add treacle and mix well", "Cook on low heat, stirring constantly", "Mixture will thicken (45-60 min)", "Add cashews and cardamom", "Cook until it doesn't stick to pan", "Pour into greased tray", "Cool and cut into pieces"],
            "prep_time_minutes": 15,
            "cook_time_minutes": 90,
            "servings": 30,
            "difficulty": "Hard",
            "tags": ["dessert", "sweet", "sticky", "traditional"],
            "cultural_notes": "Labor-intensive traditional sweet, requires constant stirring",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_040",
            "name": "Aasmi (Crispy Sweets)",
            "name_sinhala": "ආස්මි",
            "name_tamil": "ஆஸ்மி",
            "category": "Dessert",
            "region": "Muslim",
            "description": "Crispy fried swirls dipped in sugar syrup",
            "ingredients": ["1 cup rice flour", "1/2 cup wheat flour", "1 egg", "1 cup sugar", "1/2 cup water", "1/2 tsp cardamom", "Oil for frying", "Food coloring (optional)"],
            "instructions": ["Make sugar syrup with water", "Add cardamom to syrup", "Mix flours with egg and water", "Make smooth batter", "Heat oil", "Drizzle batter in circular patterns", "Fry until crispy", "Dip in sugar syrup", "Drain and serve"],
            "prep_time_minutes": 20,
            "cook_time_minutes": 30,
            "servings": 25,
            "difficulty": "Medium",
            "tags": ["dessert", "sweet", "crispy", "muslim"],
            "cultural_notes": "Muslim Eid specialty, colorful and festive",
            "authenticity_score": 0.95
        },
        {
            "id": "recipe_041",
            "name": "Milk Toffee",
            "name_sinhala": "කිරි ටොෆි",
            "name_tamil": "பால் டாஃபி",
            "category": "Dessert",
            "region": "General",
            "description": "Creamy milk fudge with cashews",
            "ingredients": ["2 cups full cream milk powder", "1 cup sugar", "1/2 cup water", "1/2 cup cashews, chopped", "1/2 tsp cardamom", "1 tbsp butter"],
            "instructions": ["Boil sugar and water to syrup", "Add milk powder gradually", "Stir constantly on low heat", "Add butter", "Mixture will thicken", "Add cashews and cardamom", "Pour into greased tray", "Cool and cut into squares"],
            "prep_time_minutes": 10,
            "cook_time_minutes": 30,
            "servings": 25,
            "difficulty": "Medium",
            "tags": ["dessert", "sweet", "fudge", "popular"],
            "cultural_notes": "Modern Sri Lankan favorite, popular gift item",
            "authenticity_score": 0.85
        },
        {
            "id": "recipe_042",
            "name": "Bombai Muttai (Candy Floss)",
            "name_sinhala": "බොම්බේ මුට්ටෙ",
            "name_tamil": "பாம்பே முட்டை",
            "category": "Dessert",
            "region": "General",
            "description": "Crispy meringue balls, light and sweet",
            "ingredients": ["4 egg whites", "2 cups sugar", "1/2 tsp vinegar", "1/4 tsp cream of tartar", "Pink food coloring"],
            "instructions": ["Beat egg whites until stiff", "Gradually add sugar", "Add vinegar and cream of tartar", "Add food coloring", "Pipe onto baking tray", "Bake at very low temp (100°C)", "Dry for 2-3 hours", "Store in airtight container"],
            "prep_time_minutes": 20,
            "cook_time_minutes": 180,
            "servings": 30,
            "difficulty": "Medium",
            "tags": ["dessert", "sweet", "baked", "crispy"],
            "cultural_notes": "Popular children's sweet, sold at fairs",
            "authenticity_score": 0.80
        },
        {
            "id": "recipe_043",
            "name": "Pani Pol (Coconut Toffee)",
            "name_sinhala": "පැණි පොල්",
            "name_tamil": "தேங்காய் கேண்டி",
            "category": "Dessert",
            "region": "General",
            "description": "Sweet coconut jaggery toffee",
            "ingredients": ["2 cups jaggery", "2 cups grated coconut", "1/2 tsp cardamom", "Cashews (optional)"],
            "instructions": ["Melt jaggery in pan", "Add grated coconut", "Cook stirring constantly", "Mixture will become thick", "Add cardamom", "Test by dropping in water", "Should form a ball", "Pour into greased tray", "Cut while warm"],
            "prep_time_minutes": 10,
            "cook_time_minutes": 25,
            "servings": 20,
            "difficulty": "Medium",
            "tags": ["dessert", "sweet", "coconut", "traditional"],
            "cultural_notes": "Simple traditional sweet, made at home",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_044",
            "name": "Ginger Beer",
            "name_sinhala": "ඉඟුරු බියර්",
            "name_tamil": "இஞ்சி பீர்",
            "category": "Beverage",
            "region": "General",
            "description": "Homemade ginger drink, fizzy and spicy",
            "ingredients": ["100g ginger, crushed", "2 cups sugar", "2 liters water", "1/2 tsp cream of tartar", "1/4 tsp yeast", "Juice of 2 limes"],
            "instructions": ["Boil ginger with 1 liter water", "Strain and cool", "Add sugar and stir to dissolve", "Add cream of tartar", "Add remaining water", "Add yeast and lime juice", "Pour into bottles", "Leave for 24 hours to ferment", "Chill and serve"],
            "prep_time_minutes": 20,
            "cook_time_minutes": 15,
            "servings": 8,
            "difficulty": "Easy",
            "tags": ["beverage", "fizzy", "spicy", "fermented"],
            "cultural_notes": "Traditional homemade soda, Christmas favorite",
            "authenticity_score": 0.95
        },
        {
            "id": "recipe_045",
            "name": "Faluda",
            "name_sinhala": "ෆලූඩා",
            "name_tamil": "பலூடா",
            "category": "Beverage",
            "region": "Muslim",
            "description": "Rose-flavored milk drink with jelly and ice cream",
            "ingredients": ["2 cups milk", "4 tbsp rose syrup", "2 tbsp basil seeds (soaked)", "100g agar jelly, cubed", "Vanilla ice cream", "Cashews and raisins", "Ice cubes"],
            "instructions": ["Soak basil seeds for 30 minutes", "Prepare agar jelly and cut into cubes", "In tall glass, add rose syrup", "Add basil seeds and jelly cubes", "Pour chilled milk", "Add ice cubes", "Top with ice cream", "Garnish with cashews", "Serve with spoon and straw"],
            "prep_time_minutes": 40,
            "cook_time_minutes": 5,
            "servings": 4,
            "difficulty": "Easy",
            "tags": ["beverage", "sweet", "cold", "festive"],
            "cultural_notes": "Popular Ramadan drink, sold by Muslim vendors",
            "authenticity_score": 0.90
        },
        {
            "id": "recipe_046",
            "name": "Woodapple Juice",
            "name_sinhala": "දිවුල් ජූස්",
            "name_tamil": "விளாம்பழம் ஜூஸ்",
            "category": "Beverage",
            "region": "General",
            "description": "Refreshing juice from wood apple fruit",
            "ingredients": ["2 wood apples", "1/2 cup jaggery or sugar", "4 cups water", "Pinch of salt", "Ice cubes"],
            "instructions": ["Break open wood apples", "Scoop out pulp", "Mix with water", "Strain to remove seeds", "Add jaggery or sugar", "Add pinch of salt", "Mix well until dissolved", "Chill", "Serve with ice"],
            "prep_time_minutes": 15,
            "cook_time_minutes": 0,
            "servings": 4,
            "difficulty": "Easy",
            "tags": ["beverage", "fresh", "healthy", "cooling"],
            "cultural_notes": "Cooling drink for hot weather, very healthy",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_047",
            "name": "King Coconut Water (Thambili)",
            "name_sinhala": "තැඹිලි",
            "name_tamil": "தெண்ணிர்",
            "category": "Beverage",
            "region": "General",
            "description": "Fresh king coconut water, nature's electrolyte drink",
            "ingredients": ["1 king coconut (orange variety)"],
            "instructions": ["Choose tender orange king coconut", "Cut top with machete", "Insert straw", "Drink the water", "Optional: scrape soft flesh and eat"],
            "prep_time_minutes": 2,
            "cook_time_minutes": 0,
            "servings": 1,
            "difficulty": "Easy",
            "tags": ["beverage", "healthy", "natural", "fresh"],
            "cultural_notes": "National drink of Sri Lanka, sold by roadside vendors",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_048",
            "name": "Curd with Treacle",
            "name_sinhala": "මී කිරි",
            "name_tamil": "தயிர் மற்றும் பன்னீர்",
            "category": "Dessert",
            "region": "General",
            "description": "Buffalo curd served with palm treacle",
            "ingredients": ["1 clay pot buffalo curd", "4 tbsp kithul treacle", "1 tbsp cashew nuts (optional)"],
            "instructions": ["Open curd pot", "Pour treacle over curd", "Mix gently", "Add cashews if desired", "Serve immediately"],
            "prep_time_minutes": 2,
            "cook_time_minutes": 0,
            "servings": 2,
            "difficulty": "Easy",
            "tags": ["dessert", "healthy", "traditional", "no-cook"],
            "cultural_notes": "Traditional dessert, curd in clay pots is special",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_049",
            "name": "Mung Kavum",
            "name_sinhala": "මුං කැවුම්",
            "name_tamil": "பயறு கவும்",
            "category": "Dessert",
            "region": "General",
            "description": "Mung bean oil cakes",
            "ingredients": ["1 cup mung flour", "1/2 cup rice flour", "1 cup kithul treacle", "1/4 cup coconut milk", "1/2 tsp cardamom", "Oil for frying"],
            "instructions": ["Mix mung flour and rice flour", "Add treacle and coconut milk", "Add cardamom", "Mix to thick batter", "Let rest for 1 hour", "Heat oil", "Drop spoonfuls and fry", "Fry until dark brown", "Drain and cool"],
            "prep_time_minutes": 15,
            "cook_time_minutes": 25,
            "servings": 20,
            "difficulty": "Medium",
            "tags": ["dessert", "sweet", "fried", "traditional"],
            "cultural_notes": "Variation of kavum, lighter texture",
            "authenticity_score": 0.95
        },
        {
            "id": "recipe_050",
            "name": "Bibikkan (Coconut Cake)",
            "name_sinhala": "බිබික්කන්",
            "name_tamil": "பிபிக்கன்",
            "category": "Dessert",
            "region": "General",
            "description": "Rich coconut and jaggery cake with cashews",
            "ingredients": ["2 cups grated coconut", "1 cup jaggery", "1 cup rice flour", "1/2 cup semolina", "1/2 cup cashews", "1/2 cup raisins", "1 tsp cardamom", "1/2 tsp nutmeg", "4 eggs"],
            "instructions": ["Melt jaggery with little water", "Mix coconut, rice flour, semolina", "Add melted jaggery", "Add beaten eggs", "Add cashews, raisins, spices", "Mix well", "Pour into greased pan", "Bake at 180°C for 45 minutes", "Cool and cut"],
            "prep_time_minutes": 20,
            "cook_time_minutes": 45,
            "servings": 12,
            "difficulty": "Medium",
            "tags": ["dessert", "baked", "rich", "traditional"],
            "cultural_notes": "Traditional Christmas and New Year cake",
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
    
    print(f"OK Added {len(recipes)} new recipes (IDs 024-050)")
    print(f"OK Total recipes now: {len(all_recipes)}")
    print(f"OK Saved to: {output_dir}")

if __name__ == "__main__":
    print("\nGenerating Batch 2: 27 more Sri Lankan recipes (IDs 024-050)...")
    recipes = generate_batch_2_recipes()
    save_recipes(recipes)
    print("\nOK Complete! You now have 50 recipes!")
    print("\nNext: Run recipe_rag_system.py to rebuild RAG with all 50 recipes")