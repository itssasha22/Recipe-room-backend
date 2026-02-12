from app import app
from database import db
from models import User, Recipe
from werkzeug.security import generate_password_hash

def seed_recipes():
    with app.app_context():
        # Clear existing data to start fresh
        Recipe.query.delete()
        User.query.delete()
        db.session.commit()
        
        # Create users from different countries with authentic local names
        users_data = [
            {'username': 'WanjiruKamau', 'email': 'wanjiru@reciperoom.com', 'country': 'Kenya'},
            {'username': 'AbebeTesfaye', 'email': 'abebe@reciperoom.com', 'country': 'Ethiopia'},
            {'username': 'AdaoraOkafor', 'email': 'adaora@reciperoom.com', 'country': 'Nigeria'},
            {'username': 'GiovanniRossi', 'email': 'giovanni@reciperoom.com', 'country': 'Italy'},
            {'username': 'SomchaiPatel', 'email': 'somchai@reciperoom.com', 'country': 'Thailand'},
            {'username': 'PriyaSharma', 'email': 'priya@reciperoom.com', 'country': 'India'},
            {'username': 'CarlosHernandez', 'email': 'carlos@reciperoom.com', 'country': 'Mexico'},
            {'username': 'FatimaKhoury', 'email': 'fatima@reciperoom.com', 'country': 'Lebanon'},
            {'username': 'ThandoMokoena', 'email': 'thando@reciperoom.com', 'country': 'South Africa'},
            {'username': 'AminaBenali', 'email': 'amina@reciperoom.com', 'country': 'Morocco'},
        ]
        
        users = {}
        for user_data in users_data:
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                password_hash=generate_password_hash('password123')  # Just for demo purposes
            )
            db.session.add(user)
            db.session.commit()
            users[user_data['country']] = user
            print(f"Created user: {user.username} from {user_data['country']}")
        
        recipes_data = [
            # EAST AFRICAN RECIPES
            {
                'title': 'Ugali with Sukuma Wiki (Kenyan Staple)',
                'description': 'A hearty traditional Kenyan meal featuring stiff maize porridge served with sautéed collard greens. This is comfort food at its finest, eaten daily by millions across East Africa.',
                'ingredients': '''2 cups maize flour (cornmeal)
4 cups water
1 bunch collard greens (sukuma wiki), chopped
2 tomatoes, diced
1 onion, finely chopped
3 cloves garlic, minced
2 tablespoons cooking oil
Salt to taste
1 teaspoon royco (optional)''',
                'instructions': '''For the Ugali:
1. Bring 4 cups of water to a rolling boil in a heavy-bottomed pot
2. Reduce heat to medium and slowly add 1 cup of maize flour while stirring continuously with a wooden spoon to avoid lumps
3. Keep stirring vigorously for about 3 minutes until the mixture thickens
4. Gradually add the remaining flour, stirring constantly in a folding motion
5. Lower the heat and continue stirring for 8-10 minutes until the ugali pulls away from the sides of the pot and becomes firm
6. Press down with the wooden spoon to compress it, then shape into a dome
7. Transfer to a serving plate and cover with a clean cloth to keep warm

For the Sukuma Wiki:
1. Heat oil in a large pan over medium heat
2. Add chopped onions and sauté until golden brown (about 5 minutes)
3. Add minced garlic and cook for 1 minute until fragrant
4. Toss in the diced tomatoes and cook until they break down into a soft pulp (5-7 minutes)
5. Add the chopped collard greens and stir well to coat with the tomato mixture
6. Season with salt and royco if using
7. Cook for 10-15 minutes, stirring occasionally, until the greens are tender but still vibrant
8. If it gets too dry, add a splash of water

Serve the ugali alongside the sukuma wiki with optional nyama choma (grilled meat) on the side.''',
                'prep_time': 10,
                'cook_time': 25,
                'servings': 4,
                'country': 'Kenya',
                'image_url': 'https://images.unsplash.com/photo-1604329760661-e71dc83f8f26?w=600',
                'user_id': users['Kenya'].id
            },
            {
                'title': 'Pilau (Spiced Rice)',
                'description': 'Aromatic and flavorful rice dish popular along the Swahili coast. The blend of spices creates a rich, complex flavor that makes every bite memorable.',
                'ingredients': '''2 cups basmati rice
500g beef or goat meat, cubed
1 large onion, sliced
4 cloves garlic, minced
1-inch ginger, grated
3 tomatoes, chopped
4 cups beef stock
3 tablespoons pilau masala
1 teaspoon cumin seeds
4 cloves
1 cinnamon stick
3 cardamom pods
2 bay leaves
1/4 cup cooking oil
Salt to taste
Fresh coriander for garnish''',
                'instructions': '''1. Rinse the basmati rice in cold water until water runs clear, then soak for 20 minutes and drain
2. Heat oil in a large heavy-bottomed pot over medium-high heat
3. Add cumin seeds, cloves, cardamom, cinnamon stick, and bay leaves - let them sizzle for 30 seconds
4. Add sliced onions and fry until deep golden brown (about 10 minutes) - this is crucial for color and flavor
5. Stir in minced garlic and grated ginger, cook for 2 minutes
6. Add the cubed meat and brown on all sides (about 8 minutes)
7. Mix in the pilau masala, coating the meat thoroughly
8. Add chopped tomatoes and cook until they soften and release their juices (5 minutes)
9. Pour in 1 cup of beef stock, cover, and simmer for 30 minutes until meat is tender
10. Add the drained rice and stir gently to combine with the meat mixture
11. Pour in the remaining 3 cups of hot beef stock and season with salt
12. Bring to a boil, then reduce heat to low, cover tightly with a lid and aluminum foil
13. Cook undisturbed for 20 minutes - resist the urge to peek!
14. Turn off heat and let it rest covered for 10 minutes
15. Fluff gently with a fork and garnish with fresh coriander
16. Serve hot with kachumbari (tomato-onion salad) and a squeeze of lemon''',
                'prep_time': 30,
                'cook_time': 70,
                'servings': 6,
                'country': 'Kenya',
                'image_url': 'https://images.unsplash.com/photo-1596797038530-2c107229654b?w=600',
                'user_id': users['Kenya'].id
            },
            {
                'title': 'Chapati (East African Flatbread)',
                'description': 'Soft, layered flatbread that\'s a staple in East African homes. The flaky layers and buttery taste make it perfect for scooping up stews.',
                'ingredients': '''3 cups all-purpose flour
1 cup warm water
2 tablespoons sugar
1 teaspoon salt
3 tablespoons vegetable oil
Extra oil for cooking''',
                'instructions': '''1. In a large bowl, combine flour, sugar, and salt
2. Make a well in the center and add the oil
3. Gradually add warm water, mixing with your hand until a soft dough forms
4. Knead on a floured surface for 10 minutes until smooth and elastic
5. Divide dough into 8 equal balls
6. Let them rest covered with a damp cloth for 30 minutes
7. Roll each ball into a thin circle (about 8 inches diameter)
8. Brush the surface lightly with oil
9. Make a cut from the center to the edge
10. Roll the dough into a cone shape, then flatten the cone to form a round disc
11. Let rest for 10 minutes
12. Roll out again into a circle about 1/4 inch thick
13. Heat a skillet or tawa over medium heat
14. Cook each chapati for 1-2 minutes per side, brushing with oil
15. Press gently with a spatula to help it puff up
16. Stack cooked chapatis and cover with a kitchen towel to keep soft''',
                'prep_time': 45,
                'cook_time': 30,
                'servings': 8,
                'country': 'Kenya',
                'image_url': 'https://images.unsplash.com/photo-1626074353765-517a681e40be?w=600',
                'user_id': users['Kenya'].id
            },
            {
                'title': 'Nyama Choma (Grilled Meat)',
                'description': 'Kenya\'s national dish - succulent grilled meat that\'s smoky, flavorful, and best enjoyed with friends. Usually served with kachumbari and ugali.',
                'ingredients': '''1.5 kg goat or beef ribs
2 tablespoons coarse salt
1 tablespoon black pepper
2 teaspoons paprika
3 cloves garlic, minced
Juice of 2 lemons
2 tablespoons vegetable oil''',
                'instructions': '''1. Cut the meat into manageable pieces, about 3-4 inches long
2. In a bowl, mix salt, pepper, paprika, minced garlic, lemon juice, and oil
3. Rub this mixture thoroughly over all the meat pieces
4. Let marinate for at least 2 hours (overnight is even better)
5. Prepare your charcoal grill - let the coals burn until they\'re glowing red with white ash
6. Place the meat on the grill about 6 inches above the coals
7. Grill for 10-15 minutes on each side, turning frequently
8. The meat should develop a nice char while remaining juicy inside
9. Total cooking time is about 30-40 minutes depending on thickness
10. Sprinkle with additional salt while grilling
11. Let rest for 5 minutes before serving
12. Serve hot with fresh kachumbari (diced tomatoes, onions, and coriander with lemon juice)''',
                'prep_time': 130,
                'cook_time': 40,
                'servings': 6,
                'country': 'Kenya',
                'image_url': 'https://images.unsplash.com/photo-1529692236671-f1f6cf9683ba?w=600',
                'user_id': users['Kenya'].id
            },
            {
                'title': 'Mandazi (East African Donuts)',
                'description': 'Sweet, fluffy fried bread often enjoyed with chai in the morning or as an afternoon snack. Slightly spiced with cardamom.',
                'ingredients': '''3 cups all-purpose flour
1/2 cup sugar
2 teaspoons instant yeast
1 teaspoon cardamom powder
1/2 teaspoon salt
1 egg
1 cup warm coconut milk
2 tablespoons melted butter
Oil for deep frying''',
                'instructions': '''1. In a large bowl, mix flour, sugar, yeast, cardamom, and salt
2. In another bowl, whisk together egg, warm coconut milk, and melted butter
3. Make a well in the flour mixture and pour in the wet ingredients
4. Mix until a soft dough forms
5. Knead for 8-10 minutes until smooth and elastic
6. Place in a greased bowl, cover with plastic wrap, and let rise for 1 hour until doubled
7. Punch down the dough and divide into two portions
8. Roll each portion to about 1/2 inch thickness
9. Cut into triangles or diamond shapes
10. Cover and let rest for 15 minutes
11. Heat oil to 350°F (175°C) in a deep pot
12. Fry mandazi in batches, turning once, until golden brown (about 3-4 minutes total)
13. Drain on paper towels
14. Best served warm with masala chai''',
                'prep_time': 90,
                'cook_time': 20,
                'servings': 12,
                'country': 'Kenya',
                'image_url': 'https://images.unsplash.com/photo-1586985289688-ca3cf47d3e6e?w=600',
                'user_id': users['Kenya'].id
            },
            
            # ETHIOPIAN/EAST AFRICAN
            {
                'title': 'Injera with Doro Wat (Ethiopian)',
                'description': 'Spongy sourdough flatbread served with spicy chicken stew. The national dish of Ethiopia, full of complex flavors from berbere spice.',
                'ingredients': '''For Injera:
2 cups teff flour
3 cups water
1/2 teaspoon salt

For Doro Wat:
1 whole chicken, cut into pieces
3 large onions, finely chopped
1/4 cup berbere spice
6 cloves garlic, minced
2-inch ginger, grated
1/4 cup niter kibbeh (Ethiopian spiced butter)
1 cup chicken stock
4 hard-boiled eggs
Salt to taste
Juice of 1 lemon''',
                'instructions': '''For Injera (start 2-3 days ahead):
1. Mix teff flour and water in a large bowl
2. Cover loosely and let ferment at room temperature for 2-3 days until bubbly and sour
3. Add salt and thin with water if needed (consistency of pancake batter)
4. Heat a non-stick pan over medium heat
5. Pour a ladleful of batter in a circular motion from outside to center
6. Cover and cook for 2-3 minutes until holes form on surface
7. Do not flip - injera is cooked on one side only
8. Remove and stack on a plate

For Doro Wat:
1. Cook chopped onions in a dry pan over medium heat for 15 minutes, stirring constantly
2. Add niter kibbeh and cook for 5 more minutes
3. Stir in berbere spice, garlic, and ginger
4. Cook for 3 minutes, stirring constantly
5. Add chicken pieces and turn to coat in the spice mixture
6. Pour in chicken stock and bring to a boil
7. Reduce heat and simmer covered for 45 minutes
8. Add hard-boiled eggs (poke holes with fork)
9. Simmer for 15 more minutes
10. Finish with lemon juice
11. Serve on top of injera''',
                'prep_time': 3000,
                'cook_time': 90,
                'servings': 6,
                'country': 'Ethiopia',
                'image_url': 'https://images.unsplash.com/photo-1604909052743-94e838986d24?w=600',
                'user_id': users['Ethiopia'].id
            },
            
            # WEST AFRICAN
            {
                'title': 'Jollof Rice (West African)',
                'description': 'The most famous West African dish - aromatic rice cooked in a rich tomato sauce. Every country has their own version!',
                'ingredients': '''3 cups long-grain parboiled rice
400g can tomato paste
5 large tomatoes, blended
2 red bell peppers, blended
2 onions (1 chopped, 1 blended)
1/4 cup vegetable oil
3 cups chicken stock
2 tablespoons curry powder
2 teaspoons thyme
2 bay leaves
3 stock cubes
2 scotch bonnet peppers (optional)
Salt to taste''',
                'instructions': '''1. Rinse rice until water runs clear, then soak for 30 minutes
2. Heat oil in a large pot over medium heat
3. Fry the chopped onions until translucent
4. Add tomato paste and fry for 5 minutes, stirring constantly
5. Pour in the blended tomato, pepper, and onion mixture
6. Cook for 20 minutes until reduced and oil floats on top
7. Add curry powder, thyme, bay leaves, and stock cubes
8. Season with salt and add scotch bonnet (whole for mild heat)
9. Pour in chicken stock and bring to a boil
10. Add the drained rice and stir well
11. Once boiling, reduce heat to very low
12. Cover tightly with aluminum foil and lid
13. Cook for 30 minutes without opening
14. Turn off heat and let steam for 10 more minutes
15. Fluff with a fork - rice should be tender with a slight smoky bottom
16. Serve with fried plantains and coleslaw''',
                'prep_time': 40,
                'cook_time': 60,
                'servings': 8,
                'country': 'Nigeria',
                'image_url': 'https://images.unsplash.com/photo-1596797038530-2c107229654b?w=600',
                'user_id': users['Nigeria'].id
            },
            {
                'title': 'Egusi Soup (Nigerian)',
                'description': 'Rich, hearty soup made with ground melon seeds. A Nigerian favorite served with fufu or pounded yam.',
                'ingredients': '''2 cups ground egusi (melon seeds)
500g assorted meat (beef, goat)
300g stockfish (soaked)
2 cups spinach or bitter leaf
1/2 cup palm oil
2 onions, chopped
3 scotch bonnet peppers
2 teaspoons crayfish powder
3 stock cubes
Salt to taste
Water as needed''',
                'instructions': '''1. Season and cook assorted meat with 1 onion until tender (about 45 minutes)
2. Add stockfish and cook for 15 more minutes
3. Remove meat and stockfish, strain and reserve the stock
4. Heat palm oil in a large pot
5. Add remaining chopped onion and fry until soft
6. Add ground egusi seeds and stir continuously for 5 minutes
7. Gradually add the reserved stock while stirring to avoid lumps
8. Add blended scotch bonnet peppers
9. Simmer for 20 minutes, stirring occasionally
10. Add the cooked meat and stockfish
11. Season with crayfish powder, stock cubes, and salt
12. Add washed spinach or bitter leaf
13. Cook for 10 more minutes
14. Adjust seasoning and consistency
15. Serve hot with your choice of swallow (fufu, eba, pounded yam)''',
                'prep_time': 20,
                'cook_time': 90,
                'servings': 6,
                'country': 'Nigeria',
                'image_url': 'https://images.unsplash.com/photo-1547592166-23ac45744acd?w=600',
                'user_id': users['Nigeria'].id
            },
            
            # ITALIAN
            {
                'title': 'Spaghetti Carbonara (Italian)',
                'description': 'Classic Roman pasta with crispy guanciale, eggs, and pecorino. Creamy without cream!',
                'ingredients': '''400g spaghetti
150g guanciale or pancetta, diced
4 large egg yolks
1 whole egg
100g Pecorino Romano, finely grated
Black pepper, freshly ground
Salt for pasta water''',
                'instructions': '''1. Bring a large pot of salted water to boil
2. In a cold pan, add diced guanciale
3. Turn heat to medium and cook until crispy (8-10 minutes)
4. In a bowl, whisk together egg yolks, whole egg, and half the pecorino
5. Add generous black pepper
6. Cook spaghetti until al dente (usually 1 minute less than package says)
7. Reserve 1 cup pasta water before draining
8. Turn off heat under guanciale pan
9. Add hot drained pasta to the guanciale pan
10. Toss well to coat pasta with the rendered fat
11. Remove pan from heat completely
12. Add egg mixture and toss quickly
13. Add pasta water gradually while tossing to create creamy sauce
14. Keep moving the pasta - you don\'t want scrambled eggs!
15. Add remaining pecorino and toss
16. Serve immediately with extra pecorino and black pepper''',
                'prep_time': 10,
                'cook_time': 15,
                'servings': 4,
                'country': 'Italy',
                'image_url': 'https://images.unsplash.com/photo-1612874742237-6526221588e3?w=600',
                'user_id': users['Italy'].id
            },
            {
                'title': 'Margherita Pizza (Italian)',
                'description': 'The queen of pizzas - simple yet perfect with fresh mozzarella, basil, and tomato sauce.',
                'ingredients': '''For Dough:
500g tipo 00 flour
325ml warm water
10g salt
7g active dry yeast
2 tablespoons olive oil

For Topping:
400g can San Marzano tomatoes
250g fresh mozzarella
Fresh basil leaves
Extra virgin olive oil
Sea salt''',
                'instructions': '''For Dough (start 24 hours ahead):
1. Dissolve yeast in warm water with a pinch of sugar
2. Let stand for 5 minutes until foamy
3. Mix flour and salt in a large bowl
4. Add yeast water and olive oil
5. Mix until shaggy dough forms
6. Knead for 10 minutes until smooth and elastic
7. Place in oiled bowl, cover, refrigerate for 24 hours

For Pizza:
1. Remove dough from fridge 2 hours before using
2. Preheat oven to maximum (500°F/260°C) with pizza stone inside
3. Crush tomatoes by hand with salt
4. Divide dough into 3 balls
5. On floured surface, stretch each ball into 10-inch circle
6. Keep edges slightly thicker for crust
7. Spread thin layer of crushed tomatoes
8. Tear mozzarella and scatter on top
9. Drizzle with olive oil
10. Slide onto hot pizza stone
11. Bake for 8-10 minutes until crust is golden and cheese bubbles
12. Remove and immediately top with fresh basil
13. Drizzle with more olive oil
14. Let rest 2 minutes before slicing''',
                'prep_time': 1460,
                'cook_time': 10,
                'servings': 3,
                'country': 'Italy',
                'image_url': 'https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=600',
                'user_id': users['Italy'].id
            },
            
            # ASIAN
            {
                'title': 'Pad Thai (Thai)',
                'description': 'Sweet, sour, and savory rice noodles with the perfect balance of flavors. A Thai street food classic.',
                'ingredients': '''200g rice noodles
200g shrimp, peeled
2 eggs
3 tablespoons fish sauce
2 tablespoons tamarind paste
2 tablespoons palm sugar
3 cloves garlic, minced
2 shallots, sliced
100g firm tofu, cubed
3 tablespoons vegetable oil
1 cup bean sprouts
3 spring onions, cut into 2-inch pieces
2 tablespoons roasted peanuts, crushed
Lime wedges
Dried chili flakes''',
                'instructions': '''1. Soak rice noodles in room temperature water for 30 minutes, then drain
2. Make sauce by mixing fish sauce, tamarind paste, and palm sugar - set aside
3. Heat wok or large pan over high heat
4. Add 1 tablespoon oil and scramble eggs, breaking into small pieces
5. Remove eggs and set aside
6. Add 2 tablespoons oil, garlic, and shallots - stir-fry for 30 seconds
7. Add shrimp and tofu, cook until shrimp turns pink (3 minutes)
8. Push everything to the side of the wok
9. Add drained noodles to the empty space
10. Pour sauce over noodles and toss for 2-3 minutes
11. Add scrambled eggs back in
12. Toss in bean sprouts and spring onions
13. Stir-fry for 1 more minute
14. Serve immediately topped with crushed peanuts
15. Garnish with lime wedges and chili flakes on the side''',
                'prep_time': 35,
                'cook_time': 10,
                'servings': 2,
                'country': 'Thailand',
                'image_url': 'https://images.unsplash.com/photo-1559314809-0d155014e29e?w=600',
                'user_id': users['Thailand'].id
            },
            {
                'title': 'Chicken Biryani (Indian)',
                'description': 'Aromatic layered rice dish with tender chicken, infused with saffron and whole spices. A celebration on a plate!',
                'ingredients': '''500g basmati rice
750g chicken, cut into pieces
1 cup yogurt
2 onions, sliced
1/2 cup ghee
4 cloves garlic, minced
2-inch ginger, grated
2 tomatoes, chopped
2 teaspoons biryani masala
1 teaspoon turmeric
1 teaspoon red chili powder
1/2 cup milk
Pinch of saffron
4 green cardamom
4 cloves
2 bay leaves
1 cinnamon stick
Fresh mint and coriander
2 green chilies''',
                'instructions': '''1. Soak rice for 30 minutes, then boil with whole spices until 70% cooked, drain
2. Marinate chicken with yogurt, half the spices, ginger-garlic paste for 30 minutes
3. Heat ghee in a heavy pot and deep fry onions until dark brown, remove and set aside
4. In same ghee, add bay leaves, cardamom, cloves, and cinnamon
5. Add marinated chicken and cook for 15 minutes until nearly done
6. Soak saffron in warm milk
7. Layer 1: Spread half the rice over chicken
8. Sprinkle half the fried onions, mint, and coriander
9. Drizzle half the saffron milk
10. Layer 2: Add remaining rice
11. Top with remaining onions, herbs, and saffron milk
12. Dot with ghee
13. Cover with tight-fitting lid, use dough to seal edges
14. Cook on high heat for 5 minutes, then low heat for 30 minutes
15. Turn off heat, let rest 10 minutes without opening
16. Gently mix before serving with raita''',
                'prep_time': 60,
                'cook_time': 60,
                'servings': 6,
                'country': 'India',
                'image_url': 'https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=600',
                'user_id': users['India'].id
            },
            
            # MEXICAN
            {
                'title': 'Tacos al Pastor (Mexican)',
                'description': 'Marinated pork tacos with pineapple, inspired by Lebanese shawarma. A Mexico City street food icon.',
                'ingredients': '''1kg pork shoulder, thinly sliced
3 dried guajillo chilies
2 dried ancho chilies
1/2 pineapple, chopped (plus slices for grilling)
1 onion
4 cloves garlic
2 tablespoons achiote paste
1/4 cup white vinegar
1 tablespoon cumin
1 teaspoon oregano
Salt and pepper
Corn tortillas
Fresh coriander
Diced onion
Lime wedges
Salsa verde''',
                'instructions': '''1. Toast dried chilies in a dry pan for 2 minutes
2. Soak in hot water for 20 minutes, then drain
3. Blend chilies with chopped pineapple, onion, garlic, achiote, vinegar, cumin, and oregano
4. Marinate pork slices in this mixture for at least 4 hours (overnight is best)
5. If you have a trompo (vertical spit), stack meat with pineapple slices between layers
6. Otherwise, heat a large griddle or grill pan over high heat
7. Cook marinated pork in batches, about 3 minutes per side
8. Grill pineapple slices until caramelized
9. Chop cooked pork and pineapple into small pieces
10. Warm corn tortillas on the griddle
11. Fill each tortilla with pork and pineapple
12. Top with chopped onion, fresh coriander, and a squeeze of lime
13. Serve with salsa verde on the side
14. Traditionally served on small double-layered tortillas''',
                'prep_time': 270,
                'cook_time': 20,
                'servings': 6,
                'country': 'Mexico',
                'image_url': 'https://images.unsplash.com/photo-1551504734-5ee1c4a1479b?w=600',
                'user_id': users['Mexico'].id
            },
            
            # MIDDLE EASTERN
            {
                'title': 'Shawarma (Middle Eastern)',
                'description': 'Spiced meat wrapped in warm pita with tahini sauce. A Middle Eastern street food loved worldwide.',
                'ingredients': '''750g chicken thighs, sliced
1/4 cup olive oil
Juice of 2 lemons
6 cloves garlic, minced
2 teaspoons cumin
2 teaspoons paprika
1 teaspoon turmeric
1/2 teaspoon cinnamon
1/4 teaspoon cayenne
Salt and pepper
Pita bread
Tahini sauce
Lettuce, tomatoes, cucumbers
Pickles
Sumac''',
                'instructions': '''1. Mix olive oil, lemon juice, garlic, cumin, paprika, turmeric, cinnamon, cayenne, salt, and pepper
2. Marinate chicken slices for at least 2 hours
3. Heat a large skillet or griddle over high heat
4. Cook chicken in batches, don\'t overcrowd, 4-5 minutes per side until charred
5. While chicken cooks, warm pita bread
6. Make tahini sauce: mix tahini with lemon juice, garlic, water until smooth and pourable
7. Slice cooked chicken into thin strips
8. Lay out pita bread
9. Spread tahini sauce on one side
10. Add lettuce, tomatoes, cucumbers
11. Pile on the chicken strips
12. Add pickles and sprinkle with sumac
13. Roll tightly, wrapping bottom in foil if desired
14. Serve immediately with extra tahini sauce and hot sauce on the side''',
                'prep_time': 130,
                'cook_time': 15,
                'servings': 4,
                'country': 'Lebanon',
                'image_url': 'https://images.unsplash.com/photo-1529006557810-274b9b2fc783?w=600',
                'user_id': users['Lebanon'].id
            },
            
            # SOUTH AFRICAN
            {
                'title': 'Bobotie (South African)',
                'description': 'Spiced minced meat baked with an egg topping. Cape Malay cuisine at its finest - sweet, savory, and aromatic.',
                'ingredients': '''750g ground beef
2 onions, chopped
2 cloves garlic, minced
2 slices white bread
1 cup milk
2 tablespoons curry powder
1 tablespoon turmeric
2 tablespoons chutney
2 tablespoons apricot jam
1/4 cup raisins
1/4 cup slivered almonds
2 tablespoons vinegar
3 eggs
6 bay leaves
Salt and pepper
2 tablespoons oil''',
                'instructions': '''1. Soak bread in half the milk, then squeeze out excess and mash
2. Preheat oven to 350°F (180°C)
3. Heat oil in a large pan and sauté onions until soft
4. Add garlic and cook for 1 minute
5. Add ground beef and brown, breaking up lumps (10 minutes)
6. Stir in curry powder, turmeric, salt, and pepper
7. Add mashed bread, chutney, jam, raisins, almonds, and vinegar
8. Cook for 5 minutes, stirring well
9. Transfer mixture to a greased baking dish and spread evenly
10. Tuck bay leaves into the meat mixture
11. Bake for 30 minutes
12. Beat 2 eggs with remaining milk
13. Pour egg mixture over the meat
14. Place remaining bay leaves on top for decoration
15. Bake for another 25 minutes until egg topping is set and golden
16. Let rest for 10 minutes before serving
17. Serve with yellow rice and sambals''',
                'prep_time': 20,
                'cook_time': 60,
                'servings': 6,
                'country': 'South Africa',
                'image_url': 'https://images.unsplash.com/photo-1606491956689-2ea866880c84?w=600',
                'user_id': users['South Africa'].id
            },
            
            # MOROCCAN
            {
                'title': 'Chicken Tagine (Moroccan)',
                'description': 'Slow-cooked Moroccan stew with preserved lemons and olives. The terracotta tagine creates impossibly tender, aromatic chicken.',
                'ingredients': '''1 whole chicken, cut into pieces
2 onions, grated
4 cloves garlic, minced
1-inch ginger, grated
2 teaspoons cumin
2 teaspoons paprika
1 teaspoon turmeric
1/2 teaspoon cinnamon
Pinch of saffron
1/4 cup olive oil
2 preserved lemons, quartered
1 cup green olives
1/2 cup fresh coriander, chopped
1/2 cup fresh parsley, chopped
2 cups chicken stock
Salt and pepper''',
                'instructions': '''1. Rub chicken pieces with salt, pepper, cumin, paprika, turmeric, and cinnamon
2. Let marinate for 30 minutes
3. Heat olive oil in tagine or heavy pot over medium heat
4. Add grated onions, garlic, and ginger
5. Cook until onions are soft and translucent (10 minutes)
6. Add chicken pieces and brown on all sides
7. Add saffron threads, half the coriander, and half the parsley
8. Pour in chicken stock
9. Bring to a boil, then reduce to low heat
10. Cover and simmer for 45 minutes
11. Add preserved lemons and olives
12. Continue cooking for 15 more minutes
13. The sauce should reduce and thicken
14. Adjust seasoning with salt and pepper
15. Garnish with remaining fresh coriander and parsley
16. Serve hot with warm bread or couscous for soaking up the sauce''',
                'prep_time': 40,
                'cook_time': 75,
                'servings': 4,
                'country': 'Morocco',
                'image_url': 'https://images.unsplash.com/photo-1609501676725-7186f017a4b7?w=600',
                'user_id': users['Morocco'].id
            }
        ]
        
        for recipe_data in recipes_data:
            recipe = Recipe(**recipe_data)
            db.session.add(recipe)
        
        db.session.commit()
        print(f"Successfully added {len(recipes_data)} diverse recipes!")
        print("Recipes include:")
        print("- 6 East African recipes (Kenyan staples)")
        print("- 1 Ethiopian recipe")
        print("- 2 West African recipes (Nigerian)")
        print("- 2 Italian classics")
        print("- 2 Asian favorites")
        print("- 1 Mexican street food")
        print("- 1 Middle Eastern wrap")
        print("- 1 South African specialty")
        print("- 1 Moroccan slow-cooked dish")

if __name__ == '__main__':
    seed_recipes()
