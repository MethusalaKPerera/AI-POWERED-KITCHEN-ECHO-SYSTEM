import os

os.makedirs('data/sri_lankan_recipes', exist_ok=True)

recipes = {
    'chicken_curry.txt': """Sri Lankan Chicken Curry

Ingredients:
- 1 kg chicken pieces
- 2 large onions, sliced
- 4 cloves garlic, minced
- 1 inch ginger, minced
- 2 green chilies, sliced
- 1 cup coconut milk
- 2 tablespoons curry powder
- 1 teaspoon turmeric powder
- 1 teaspoon chili powder
- 1 sprig curry leaves
- 2 tablespoons oil
- Salt to taste

Instructions:
Heat oil and sauté onions until golden. Add garlic, ginger, chilies. Add spices. Add chicken and coconut milk. Simmer 40 minutes. Serve with rice.""",

    'dhal_curry.txt': """Sri Lankan Dhal Curry

Ingredients:
- 1 cup red lentils
- 1 onion, chopped
- 2 cloves garlic
- 1 teaspoon turmeric powder
- 1 sprig curry leaves
- 1 cup coconut milk

Instructions:
Boil lentils with turmeric. Temper curry leaves. Add onions and garlic. Mix with lentils and coconut milk. Simmer 10 minutes.""",

    'kottu_roti.txt': """Kottu Roti

Ingredients:
- 4 roti flatbread, chopped
- 200g chicken
- 2 eggs
- 1 onion, sliced
- 2 green chilies
- 2 tablespoons curry powder

Instructions:
Cook chicken with curry powder. Scramble eggs. Sauté onions and chilies. Add chicken, eggs, and roti. Mix well. Serve hot."""
}

for filename, content in recipes.items():
    with open(f'data/sri_lankan_recipes/{filename}', 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Created: {filename}")

print(f"\n🎉 Created {len(recipes)} recipes!")