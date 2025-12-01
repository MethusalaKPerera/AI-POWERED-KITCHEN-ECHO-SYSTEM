import pandas as pd
import random
import os

# ------------------------------------------------------------
# REAL ITEMS FOR EACH CATEGORY (20 per category)
# ------------------------------------------------------------

ITEM_MAP = {
    "dairy": [
        "milk","yogurt","cheese","butter","cream","paneer","whipped_cream",
        "sour_cream","buttermilk","milkshake","ghee","ice_cream","feta",
        "mozzarella","cheddar","condensed_milk","cream_cheese","yogurt_drink",
        "milk_powder","chocolate_milk"
    ],
    "meat": [
        "chicken_breast","chicken_thigh","minced_beef","beef_steak","pork_chop",
        "bacon","sausage","turkey","lamb","deli_meat","ham","beef_strips",
        "chicken_wings","ground_pork","mutton","hotdog","chicken_gizzard",
        "chicken_liver","salami","beef_roast"
    ],
    "fish": [
        "salmon","tuna","prawns","crabs","lobster","squid","mussels","clams",
        "oysters","sardines","mackerel","anchovy","cuttlefish","trout",
        "tilapia","catfish","herring","fish_fillet","roe","scallops"
    ],
    "fruit": [
        "apple","banana","orange","grapes","mango","pineapple","kiwi",
        "strawberry","blueberry","watermelon","papaya","coconut","lemon",
        "avocado","pear","pomegranate","guava","plum","peach","lychee"
    ],
    "vegetable": [
        "tomato","onion","carrot","potato","lettuce","cabbage","spinach",
        "broccoli","cauliflower","cucumber","beans","ginger","garlic",
        "sweet_potato","beetroot","pumpkin","corn","leeks","mushroom",
        "bell_pepper"
    ],
    "grain": [
        "rice","bread","pasta","oats","flour","noodles","tortillas","cereal",
        "crackers","barley","quinoa","millet","couscous","porridge_mix",
        "rice_cakes","chapati","bun_rotti","string_hoppers","short_eats",
        "wheat_bread"
    ],
    "snack": [
        "biscuits","chips","chocolate","popcorn","cake_rusk","energy_bar",
        "wafers","doughnut","muffin","jelly_cup","marshmallow","candy","cookie",
        "brownie","pudding","nachos","crisps","trail_mix","sesame_snaps",
        "cheese_balls"
    ],
    "beverage": [
        "juice","soda","milk_drink","iced_tea","coffee_drink","coconut_water",
        "energy_drink","vitamin_water","smoothie","kefir","kombucha","syrup",
        "lemonade","almond_milk","soy_milk","chocolate_drink","milkshake",
        "fruit_punch","herbal_tea","yogurt_drink"
    ],
    "frozen": [
        "frozen_pizza","frozen_veggies","frozen_meatballs","frozen_chips",
        "frozen_paratha","frozen_rotti","frozen_dumplings","frozen_sausages",
        "frozen_chicken","frozen_fish","frozen_icecream","frozen_buns",
        "frozen_hashbrowns","frozen_nuggets","frozen_paneer","frozen_patties",
        "frozen_veg_mix","frozen_cutlets","frozen_faluda","frozen_dessert"
    ],
    "bakery": [
        "bun","cake","croissant","muffin","doughnut","pastry","bread_roll",
        "sandwich","cupcake","danish_pastry","brownie","shortbread",
        "cream_bun","biscuit_roll","fruit_bread","bagel","scone","garlic_bread",
        "cinnamon_roll","puffs"
    ]
}

# ------------------------------------------------------------
# LOAD REAL DATASET
# ------------------------------------------------------------

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "food_expiry_tracker.csv")
df = pd.read_csv(DATA_PATH)

# ------------------------------------------------------------
# ADD NEW COLUMN: item_name
# ------------------------------------------------------------

item_names = []

for _, row in df.iterrows():
    category = None

    # detect category from one-hot columns
    for cat in ITEM_MAP.keys():
        col = f"item_{cat}"
        if col in df.columns and row[col] == 1:
            category = cat
            break

    if category is None:
        item_names.append("unknown")
        continue

    # Random real item from this category
    selected_item = random.choice(ITEM_MAP[category])
    item_names.append(selected_item)

df["item_name"] = item_names

# ------------------------------------------------------------
# SAVE AUGMENTED DATASET
# ------------------------------------------------------------

OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "food_expiry_tracker_items.csv")
df.to_csv(OUT_PATH, index=False)

print("✅ Augmented dataset created!")
print("📌 Saved to:", OUT_PATH)
