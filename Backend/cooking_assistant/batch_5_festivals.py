#!/usr/bin/env python3
"""
Recipe Generator - Batch 5: Festival & Celebration Foods
25 authentic festival recipes from all communities (IDs 128-152)
"""

import json
from pathlib import Path
from datetime import datetime

def generate_batch_5_festival_recipes():
    """Generate 25 festival and celebration recipes"""
    
    recipes = [
        # SINHALA NEW YEAR (8 recipes)
        {
            "id": "recipe_128",
            "name": "Kiribath (Milk Rice - New Year Special)",
            "name_sinhala": "කිරිබත් (අලුත් අවුරුද්ද)",
            "name_tamil": "பால் சாதம்",
            "category": "Rice Dish",
            "region": "General",
            "description": "Auspicious milk rice for New Year",
            "ingredients": ["3 cups white rice", "600ml thick coconut milk", "3 cups water", "2 tsp salt", "Pandan leaves"],
            "instructions": ["Wash rice thoroughly", "Cook with water until almost done", "Add thick coconut milk and salt", "Add pandan leaves", "Stir gently and simmer", "Cook until very creamy", "Pour onto banana leaf or flat plate", "Let set for 30 minutes", "Cut into diamond shapes", "Serve with lunu miris at auspicious time"],
            "prep_time_minutes": 10,
            "cook_time_minutes": 30,
            "servings": 10,
            "difficulty": "Easy",
            "tags": ["new-year", "ceremonial", "auspicious", "traditional"],
            "cultural_notes": "Must be made at auspicious time on New Year morning",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_129",
            "name": "Mung Kavum (New Year Special)",
            "name_sinhala": "මුං කැවුම් (අලුත් අවුරුද්ද)",
            "name_tamil": "பயறு கவும்",
            "category": "Dessert",
            "region": "General",
            "description": "Traditional New Year sweet made with mung flour",
            "ingredients": ["2 cups mung flour", "1 cup rice flour", "1.5 cups kithul treacle", "1/2 cup coconut milk", "1 tsp cardamom powder", "Pinch of salt", "Oil for deep frying"],
            "instructions": ["Mix mung flour and rice flour", "Warm treacle and coconut milk", "Add to flour mixture", "Add cardamom and salt", "Mix to thick batter", "Rest for 2 hours", "Heat oil for deep frying", "Drop spoonfuls of batter", "Fry until dark golden brown", "Drain on paper", "Cool and store in airtight container"],
            "prep_time_minutes": 20,
            "cook_time_minutes": 30,
            "servings": 25,
            "difficulty": "Medium",
            "tags": ["new-year", "sweet", "fried", "traditional"],
            "cultural_notes": "Essential New Year sweet, represents prosperity",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_130",
            "name": "Athirasa (New Year Pancakes)",
            "name_sinhala": "අතිරස (අලුත් අවුරුද්ද)",
            "name_tamil": "அதிரசம்",
            "category": "Dessert",
            "region": "General",
            "description": "Sweet rice pancakes fried until puffed",
            "ingredients": ["3 cups rice flour", "1.5 cups jaggery", "1 cup water", "1 tsp cardamom powder", "Pinch of salt", "Oil for deep frying"],
            "instructions": ["Melt jaggery in water and strain", "Cool jaggery syrup completely", "Mix rice flour with jaggery syrup", "Add cardamom and salt", "Knead to smooth dough", "Rest overnight covered", "Heat oil for frying", "Flatten small balls into thin discs", "Fry until puffed and golden", "Drain and cool", "Store in container"],
            "prep_time_minutes": 30,
            "cook_time_minutes": 40,
            "servings": 30,
            "difficulty": "Medium",
            "tags": ["new-year", "sweet", "fried", "puffed"],
            "cultural_notes": "Must rest overnight for best puffing",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_131",
            "name": "Kokis (New Year Cookies)",
            "name_sinhala": "කොකිස් (අලුත් අවුරුද්ද)",
            "name_tamil": "கோக்கிஸ்",
            "category": "Dessert",
            "region": "General",
            "description": "Crispy flower-shaped cookies, New Year essential",
            "ingredients": ["2.5 cups rice flour", "1/2 cup coconut milk", "3 eggs", "1 tbsp sugar", "1/2 tsp salt", "1/4 tsp turmeric powder", "Oil for deep frying"],
            "instructions": ["Beat eggs with sugar", "Add coconut milk and mix", "Gradually add rice flour", "Add salt and turmeric", "Mix to smooth flowing batter", "Heat oil in deep pan", "Heat kokis mold in oil", "Dip hot mold in batter (don't cover top)", "Immerse in hot oil", "Kokis will drop off when ready", "Fry until crispy and golden", "Drain and store"],
            "prep_time_minutes": 20,
            "cook_time_minutes": 45,
            "servings": 40,
            "difficulty": "Hard",
            "tags": ["new-year", "crispy", "traditional", "festive"],
            "cultural_notes": "Symbol of New Year, requires special mold",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_132",
            "name": "Aluwa (New Year Diamond Sweet)",
            "name_sinhala": "අලුව (අලුත් අවුරුද්ද)",
            "name_tamil": "அலுவா",
            "category": "Dessert",
            "region": "General",
            "description": "Diamond-shaped rice flour sweet",
            "ingredients": ["3 cups rice flour, roasted", "2 cups jaggery, melted", "1.5 cups grated coconut", "1 cup cashews, chopped", "1 tsp cardamom powder", "1/2 cup water"],
            "instructions": ["Roast rice flour until fragrant", "Melt jaggery with water", "Strain jaggery syrup", "Mix rice flour with jaggery syrup", "Add grated coconut", "Add cashews and cardamom", "Mix well to form mass", "Spread on greased tray", "Press flat with greased spatula", "Cut diamond shapes while warm", "Let set completely", "Store in container"],
            "prep_time_minutes": 20,
            "cook_time_minutes": 15,
            "servings": 35,
            "difficulty": "Easy",
            "tags": ["new-year", "sweet", "no-fry", "diamond-cut"],
            "cultural_notes": "Easier to make than fried sweets",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_133",
            "name": "Aggala (Sweet Balls)",
            "name_sinhala": "අග්ගල (අලුත් අවුරුද්ද)",
            "name_tamil": "அக்கல",
            "category": "Dessert",
            "region": "General",
            "description": "Roasted rice flour balls with jaggery",
            "ingredients": ["3 cups rice flour, roasted", "1.5 cups jaggery, melted", "1 cup grated coconut", "1 tsp cardamom powder", "Water as needed"],
            "instructions": ["Roast rice flour until aromatic", "Cool completely", "Melt jaggery and strain", "Mix roasted flour with jaggery", "Add grated coconut", "Add cardamom", "Add water if needed to bind", "Shape into small balls", "Let dry for few hours", "Store in airtight container"],
            "prep_time_minutes": 25,
            "cook_time_minutes": 15,
            "servings": 40,
            "difficulty": "Easy",
            "tags": ["new-year", "sweet", "healthy", "no-fry"],
            "cultural_notes": "Healthy option, no oil used",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_134",
            "name": "Konda Kavum (Round Oil Cakes)",
            "name_sinhala": "කොණ්ඩ කැවුම්",
            "name_tamil": "கொண்ட கவும்",
            "category": "Dessert",
            "region": "General",
            "description": "Round sweet cakes with treacle",
            "ingredients": ["2 cups rice flour", "1 cup kithul treacle", "1/4 cup coconut milk", "1/2 tsp cardamom", "Pinch of salt", "Oil for frying"],
            "instructions": ["Mix rice flour with treacle", "Add coconut milk gradually", "Add cardamom and salt", "Mix to thick batter", "Rest for 1-2 hours", "Heat oil for deep frying", "Drop rounded spoonfuls", "Fry until dark brown and cooked through", "Drain well", "Cool and store"],
            "prep_time_minutes": 15,
            "cook_time_minutes": 30,
            "servings": 20,
            "difficulty": "Medium",
            "tags": ["new-year", "sweet", "fried", "round"],
            "cultural_notes": "Variant of regular kavum, rounder shape",
            "authenticity_score": 0.95
        },
        {
            "id": "recipe_135",
            "name": "Pani Dodol (Jaggery Coconut Toffee)",
            "name_sinhala": "පැණි දොඩොල්",
            "name_tamil": "பணிடோல்",
            "category": "Dessert",
            "region": "General",
            "description": "Quick jaggery coconut sweet for New Year",
            "ingredients": ["3 cups jaggery, chopped", "2 cups grated coconut", "1 tsp cardamom powder", "1/2 cup cashews, chopped", "Ghee for greasing"],
            "instructions": ["Melt jaggery in heavy pan", "Add grated coconut", "Stir constantly on medium heat", "Cook until thick (15-20 min)", "Add cardamom", "Test by dropping in water - should form ball", "Add cashews", "Pour into greased tray", "Cool slightly and cut", "Let set completely"],
            "prep_time_minutes": 10,
            "cook_time_minutes": 25,
            "servings": 25,
            "difficulty": "Medium",
            "tags": ["new-year", "sweet", "coconut", "quick"],
            "cultural_notes": "Faster version of traditional dodol",
            "authenticity_score": 0.95
        },
        
        # VESAK/POSON (Buddhist) (5 recipes)
        {
            "id": "recipe_136",
            "name": "Dansala Rice (Vesak Free Food)",
            "name_sinhala": "දන්සල් බත්",
            "name_tamil": "தான் சாலை சாதம்",
            "category": "Rice Dish",
            "region": "General",
            "description": "Simple rice meal distributed free during Vesak",
            "ingredients": ["5 kg rice", "3 liters coconut milk", "10 liters water", "Salt to taste", "Curry leaves"],
            "instructions": ["Cook large quantity of rice", "Add coconut milk for richness", "Season with salt", "Serve hot to devotees", "Typically served with simple curry", "Free distribution to all"],
            "prep_time_minutes": 30,
            "cook_time_minutes": 45,
            "servings": 50,
            "difficulty": "Easy",
            "tags": ["vesak", "dansala", "free-food", "buddhist"],
            "cultural_notes": "Offered free to public during Vesak",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_137",
            "name": "Kiribath for Vesak",
            "name_sinhala": "කිරිබත් (වෙසක්)",
            "name_tamil": "பால் சாதம்",
            "category": "Rice Dish",
            "region": "General",
            "description": "Milk rice for temple offerings",
            "ingredients": ["3 cups rice", "600ml coconut milk", "Water", "Salt", "Pandan leaves"],
            "instructions": ["Cook rice in water", "Add coconut milk and pandan", "Cook until creamy", "Spread on lotus leaves", "Cut into squares", "Offer to Buddha statue", "Serve at temple"],
            "prep_time_minutes": 10,
            "cook_time_minutes": 30,
            "servings": 12,
            "difficulty": "Easy",
            "tags": ["vesak", "offering", "ceremonial", "buddhist"],
            "cultural_notes": "Traditional temple offering on Vesak",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_138",
            "name": "Dansala Noodles",
            "name_sinhala": "දන්සල් නූඩ්ල්ස්",
            "name_tamil": "நூடுல்ஸ்",
            "category": "Rice Dish",
            "region": "General",
            "description": "Fried noodles for Vesak distribution",
            "ingredients": ["2 kg noodles", "1 kg mixed vegetables", "500g chicken (optional)", "Soy sauce", "Chili sauce", "Oil", "Salt"],
            "instructions": ["Boil noodles", "Stir-fry vegetables", "Add noodles", "Season with sauces", "Serve in paper cones", "Distribute to public"],
            "prep_time_minutes": 20,
            "cook_time_minutes": 25,
            "servings": 40,
            "difficulty": "Medium",
            "tags": ["vesak", "dansala", "street-food", "modern"],
            "cultural_notes": "Modern dansala favorite",
            "authenticity_score": 0.80
        },
        {
            "id": "recipe_139",
            "name": "Poson Porridge",
            "name_sinhala": "පොසොන් කැඳ",
            "name_tamil": "பொசன் கஞ்சி",
            "category": "Rice Dish",
            "region": "General",
            "description": "Sweet coconut milk porridge for Poson",
            "ingredients": ["2 cups rice flour", "4 cups coconut milk", "1 cup jaggery", "1 tsp cardamom", "Cashews", "Water"],
            "instructions": ["Mix rice flour with water", "Boil coconut milk with jaggery", "Add rice flour mixture", "Stir until thick", "Add cardamom", "Garnish with cashews", "Serve warm"],
            "prep_time_minutes": 10,
            "cook_time_minutes": 20,
            "servings": 8,
            "difficulty": "Easy",
            "tags": ["poson", "sweet", "porridge", "buddhist"],
            "cultural_notes": "Offered at temples during Poson",
            "authenticity_score": 0.95
        },
        {
            "id": "recipe_140",
            "name": "Vesak Kavili (Festival Sweet)",
            "name_sinhala": "වෙසක් කැවිලි",
            "name_tamil": "வேசாக் இனிப்பு",
            "category": "Dessert",
            "region": "General",
            "description": "Simple sweet for Vesak distribution",
            "ingredients": ["2 cups rice flour", "1 cup jaggery", "1 cup coconut", "Cardamom", "Water"],
            "instructions": ["Roast rice flour", "Melt jaggery", "Mix all ingredients", "Form into shapes", "Distribute at dansala"],
            "prep_time_minutes": 15,
            "cook_time_minutes": 15,
            "servings": 25,
            "difficulty": "Easy",
            "tags": ["vesak", "sweet", "simple", "dansala"],
            "cultural_notes": "Simple sweet for mass distribution",
            "authenticity_score": 0.90
        },
        
        # EID MUSLIM SPECIALTIES (6 recipes)
        {
            "id": "recipe_141",
            "name": "Wattalappam (Eid Special)",
            "name_sinhala": "වට්ටලප්පන් (ඊද්)",
            "name_tamil": "வாதளப்பான்",
            "category": "Dessert",
            "region": "Muslim",
            "description": "Rich coconut custard for Eid celebration",
            "ingredients": ["8 eggs", "500ml coconut milk", "300g jaggery", "1 tsp cardamom powder", "1/2 tsp nutmeg powder", "1/4 cup cashews", "1/4 cup raisins"],
            "instructions": ["Beat eggs well", "Melt jaggery and cool", "Mix eggs with jaggery", "Add coconut milk", "Add cardamom and nutmeg", "Add cashews and raisins", "Pour into mold", "Steam for 45-60 minutes", "Cool completely before serving", "Cut into diamond shapes"],
            "prep_time_minutes": 20,
            "cook_time_minutes": 60,
            "servings": 12,
            "difficulty": "Medium",
            "tags": ["eid", "muslim", "steamed", "rich"],
            "cultural_notes": "Essential Eid dessert, served to guests",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_142",
            "name": "Buriyani (Eid Feast)",
            "name_sinhala": "බුරියානි (ඊද්)",
            "name_tamil": "பிரியாணி",
            "category": "Rice Dish",
            "region": "Muslim",
            "description": "Fragrant layered rice with meat for Eid",
            "ingredients": ["1 kg chicken/mutton", "3 cups basmati rice", "3 onions", "1 cup yogurt", "2 tbsp ginger-garlic paste", "1 tbsp garam masala", "6 cloves", "4 cardamom", "2 cinnamon sticks", "Saffron", "Mint leaves", "5 tbsp ghee", "Salt"],
            "instructions": ["Marinate meat with yogurt and spices", "Fry onions until golden brown", "Cook rice 70% done", "Layer rice and meat in pot", "Sprinkle saffron and fried onions", "Add mint and ghee", "Cover and cook on low heat (dum) for 30 min", "Let rest 10 minutes", "Mix gently before serving", "Serve with raita and curry"],
            "prep_time_minutes": 40,
            "cook_time_minutes": 60,
            "servings": 8,
            "difficulty": "Hard",
            "tags": ["eid", "muslim", "rice", "festive"],
            "cultural_notes": "Main dish for Eid celebrations",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_143",
            "name": "Aasmi (Eid Sweet)",
            "name_sinhala": "ආස්මි (ඊද්)",
            "name_tamil": "ஆஸ்மி",
            "category": "Dessert",
            "region": "Muslim",
            "description": "Crispy swirled sweets in sugar syrup",
            "ingredients": ["1.5 cups rice flour", "1/2 cup wheat flour", "2 eggs", "1.5 cups sugar", "1 cup water", "1 tsp cardamom", "Food coloring", "Oil for frying"],
            "instructions": ["Make sugar syrup with cardamom", "Beat eggs", "Mix with flours and water", "Make smooth batter", "Divide and add colors", "Heat oil", "Drizzle batter in swirl patterns", "Fry until crispy", "Dip in sugar syrup", "Drain and serve"],
            "prep_time_minutes": 25,
            "cook_time_minutes": 35,
            "servings": 30,
            "difficulty": "Medium",
            "tags": ["eid", "muslim", "sweet", "colorful"],
            "cultural_notes": "Colorful Eid sweet, very popular",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_144",
            "name": "Bole (Eid Bread)",
            "name_sinhala": "බෝල් (ඊද්)",
            "name_tamil": "போல்",
            "category": "Bread",
            "region": "Muslim",
            "description": "Sweet bread for Eid breakfast",
            "ingredients": ["4 cups flour", "1 cup sugar", "1/2 cup ghee", "2 eggs", "1 cup coconut milk", "1 tbsp yeast", "1 tsp cardamom", "Sesame seeds"],
            "instructions": ["Activate yeast with warm coconut milk", "Mix flour, sugar, cardamom", "Add eggs and ghee", "Add yeast mixture", "Knead to soft dough", "Let rise for 2 hours", "Shape into buns", "Brush with egg", "Sprinkle sesame seeds", "Bake at 180°C for 20 minutes"],
            "prep_time_minutes": 30,
            "cook_time_minutes": 20,
            "servings": 15,
            "difficulty": "Medium",
            "tags": ["eid", "muslim", "bread", "sweet"],
            "cultural_notes": "Eid morning breakfast staple",
            "authenticity_score": 0.95
        },
        {
            "id": "recipe_145",
            "name": "Falooda (Eid Drink)",
            "name_sinhala": "ෆලූඩා (ඊද්)",
            "name_tamil": "பலூடா",
            "category": "Beverage",
            "region": "Muslim",
            "description": "Rose-flavored milk drink for Eid",
            "ingredients": ["3 cups milk", "6 tbsp rose syrup", "3 tbsp basil seeds (soaked)", "150g agar jelly, cubed", "Vanilla ice cream", "Cashews", "Almonds", "Ice cubes"],
            "instructions": ["Soak basil seeds 30 minutes", "Prepare and cube agar jelly", "In tall glasses, add rose syrup", "Add basil seeds", "Add jelly cubes", "Pour chilled milk", "Add ice", "Top with ice cream scoop", "Garnish with nuts", "Serve with spoon and straw"],
            "prep_time_minutes": 40,
            "cook_time_minutes": 10,
            "servings": 6,
            "difficulty": "Easy",
            "tags": ["eid", "muslim", "drink", "festive"],
            "cultural_notes": "Must-have Eid drink, very refreshing",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_146",
            "name": "Samosa (Eid Snack)",
            "name_sinhala": "සමෝසා (ඊද්)",
            "name_tamil": "சமோசா",
            "category": "Snack",
            "region": "Muslim",
            "description": "Crispy pastry triangles with spiced filling",
            "ingredients": ["For dough: 3 cups flour, water, salt, oil", "For filling: 500g beef, 2 onions, 2 potatoes, curry powder, chili, peas"],
            "instructions": ["Make dough with flour, salt, oil", "Rest 30 minutes", "Cook filling with meat and vegetables", "Season well", "Roll dough thin", "Cut into strips", "Form cone shape", "Fill with mixture", "Seal edges", "Deep fry until golden", "Serve hot with chutney"],
            "prep_time_minutes": 45,
            "cook_time_minutes": 25,
            "servings": 25,
            "difficulty": "Hard",
            "tags": ["eid", "muslim", "fried", "savory"],
            "cultural_notes": "Popular Eid snack, served to guests",
            "authenticity_score": 0.95
        },
        
        # CHRISTMAS BURGHER FOODS (6 recipes)
        {
            "id": "recipe_147",
            "name": "Christmas Cake (Burgher)",
            "name_sinhala": "ක්‍රිස්මස් කේක් (බර්ගර්)",
            "name_tamil": "கிறிஸ்துமஸ் கேக்",
            "category": "Dessert",
            "region": "Burgher",
            "description": "Rich fruit cake soaked in brandy",
            "ingredients": ["500g mixed dried fruits", "200ml brandy", "250g butter", "250g sugar", "5 eggs", "300g flour", "1 tsp baking powder", "1 tsp mixed spice", "1 tsp vanilla", "Treacle"],
            "instructions": ["Soak fruits in brandy for 1 week", "Cream butter and sugar", "Add eggs one by one", "Add vanilla and treacle", "Fold in flour and spices", "Add soaked fruits", "Pour into lined tin", "Bake at 150°C for 2-3 hours", "Cool and wrap in brandy-soaked cloth", "Store for 1 month before serving"],
            "prep_time_minutes": 40,
            "cook_time_minutes": 180,
            "servings": 20,
            "difficulty": "Hard",
            "tags": ["christmas", "burgher", "cake", "rich"],
            "cultural_notes": "Made 2 months before Christmas",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_148",
            "name": "Love Cake (Burgher Christmas)",
            "name_sinhala": "ලව් කේක්",
            "name_tamil": "லவ் கேக்",
            "category": "Dessert",
            "region": "Burgher",
            "description": "Semolina cashew cake with rose water",
            "ingredients": ["250g semolina", "250g cashews, ground", "250g sugar", "8 eggs", "250g butter", "2 tbsp honey", "1 tsp rose water", "1 tsp cardamom", "1 tsp nutmeg", "Pumpkin preserve (optional)"],
            "instructions": ["Roast semolina lightly", "Cream butter and sugar", "Separate eggs", "Beat yolks into butter mixture", "Add semolina and ground cashews", "Add honey, rose water, spices", "Beat egg whites stiff", "Fold into mixture", "Pour into greased tin", "Bake at 160°C for 45 minutes"],
            "prep_time_minutes": 30,
            "cook_time_minutes": 45,
            "servings": 16,
            "difficulty": "Hard",
            "tags": ["christmas", "burgher", "cake", "traditional"],
            "cultural_notes": "Iconic Burgher Christmas cake",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_149",
            "name": "Breudher (Dutch Cookies)",
            "name_sinhala": "බ්‍රූඩර්",
            "name_tamil": "ப்ரூடர்",
            "category": "Dessert",
            "region": "Burgher",
            "description": "Spiced butter cookies, Dutch heritage",
            "ingredients": ["500g flour", "250g butter", "200g sugar", "2 eggs", "1 tsp cinnamon", "1/2 tsp nutmeg", "1/2 tsp cardamom", "1/2 tsp cloves powder"],
            "instructions": ["Cream butter and sugar", "Add eggs", "Add spices", "Gradually add flour", "Form soft dough", "Roll thin", "Cut with cookie cutters", "Place on baking tray", "Bake at 180°C for 12-15 minutes", "Cool on wire rack"],
            "prep_time_minutes": 25,
            "cook_time_minutes": 15,
            "servings": 50,
            "difficulty": "Medium",
            "tags": ["christmas", "burgher", "cookies", "spiced"],
            "cultural_notes": "Dutch heritage Christmas cookie",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_150",
            "name": "Lamprais (Christmas Special)",
            "name_sinhala": "ලම්ප්‍රයිස් (නත්තල)",
            "name_tamil": "லம்ப்ரைஸ்",
            "category": "Rice Dish",
            "region": "Burgher",
            "description": "Dutch Burgher rice packet for Christmas",
            "ingredients": ["3 cups rice", "Chicken curry", "Beef curry", "Brinjal moju", "Seeni sambol", "Boiled eggs", "Prawn blachan", "Banana leaves", "Stock"],
            "instructions": ["Cook rice in meat stock", "Prepare all curries and sambols", "Cut banana leaves into squares", "Place rice in center", "Add all accompaniments", "Fold into neat packet", "Tie with string", "Bake at 180°C for 25 minutes", "Serve hot in packet"],
            "prep_time_minutes": 90,
            "cook_time_minutes": 50,
            "servings": 8,
            "difficulty": "Hard",
            "tags": ["christmas", "burgher", "rice", "elaborate"],
            "cultural_notes": "Grand Christmas lunch centerpiece",
            "authenticity_score": 1.0
        },
        {
            "id": "recipe_151",
            "name": "Bolo Fiado (Layer Cake)",
            "name_sinhala": "බොලෝ ෆියඩෝ",
            "name_tamil": "போலோ ஃபியடோ",
            "category": "Dessert",
            "region": "Burgher",
            "description": "Layered semolina cake, Burgher specialty",
            "ingredients": ["300g semolina", "300g sugar", "8 eggs, separated", "200g butter", "1 tsp cinnamon", "1/2 tsp nutmeg", "1/2 tsp cardamom", "Rose water", "Red food coloring"],
            "instructions": ["Beat egg yolks with sugar", "Add melted butter", "Add roasted semolina", "Add spices and rose water", "Beat egg whites stiff", "Fold in", "Divide batter in two", "Color one half pink", "Bake in layers alternating colors", "Cool and layer with jam"],
            "prep_time_minutes": 35,
            "cook_time_minutes": 40,
            "servings": 12,
            "difficulty": "Hard",
            "tags": ["christmas", "burgher", "layered", "colorful"],
            "cultural_notes": "Elaborate Christmas dessert",
            "authenticity_score": 0.95
        },
        {
            "id": "recipe_152",
            "name": "Ginger Beer (Christmas)",
            "name_sinhala": "ඉඟුරු බියර් (නත්තල)",
            "name_tamil": "இஞ்சி பீர்",
            "category": "Beverage",
            "region": "Burgher",
            "description": "Homemade ginger beer for Christmas",
            "ingredients": ["150g fresh ginger, crushed", "2.5 cups sugar", "3 liters water", "1 tsp cream of tartar", "1/2 tsp yeast", "Juice of 3 limes"],
            "instructions": ["Boil ginger in 1 liter water", "Strain ginger water", "Add sugar and stir to dissolve", "Add cream of tartar", "Add remaining water", "Cool to lukewarm", "Add yeast and lime juice", "Pour into bottles", "Leave at room temp 24-48 hours", "Refrigerate before serving"],
            "prep_time_minutes": 25,
            "cook_time_minutes": 15,
            "servings": 12,
            "difficulty": "Easy",
            "tags": ["christmas", "burgher", "beverage", "fermented"],
            "cultural_notes": "Traditional Christmas drink, non-alcoholic",
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
    
    print(f"OK Added {len(recipes)} Festival & Celebration recipes (IDs 128-152)")
    print(f"OK Total recipes now: {len(all_recipes)}")
    print(f"OK Saved to: {output_dir}")
    
    print("\n" + "="*70)
    print("FESTIVAL BREAKDOWN:")
    print("="*70)
    print("Sinhala New Year: 8 recipes (Kiribath, Kavum, Kokis, Aluwa, etc.)")
    print("Vesak/Poson: 5 recipes (Dansala, Temple offerings)")
    print("Muslim Eid: 6 recipes (Wattalappam, Buriyani, Aasmi, etc.)")
    print("Christmas Burgher: 6 recipes (Christmas Cake, Love Cake, Lamprais, etc.)")
    print("="*70)

if __name__ == "__main__":
    print("\n" + "="*70)
    print("BATCH 5: FESTIVAL & CELEBRATION FOODS")
    print("   Multicultural Sri Lankan Festivals")
    print("="*70 + "\n")
    recipes = generate_batch_5_festival_recipes()
    save_recipes(recipes)
    print("\nOK Batch 5 Complete! All festival foods added!")
    print("\nNext: Run ingredient_expander.py to extract all ingredients!")