from app import app
from database import db
from models import User, Recipe
from werkzeug.security import generate_password_hash

def add_global_recipes():
    with app.app_context():
        # Create users from new countries with authentic native names
        new_users = [
            {'username': 'YukiTanaka', 'email': 'yuki@flavorhub.com', 'country': 'Japan'},
            {'username': 'PierreDubois', 'email': 'pierre@flavorhub.com', 'country': 'France'},
            {'username': 'MariaSantos', 'email': 'maria@flavorhub.com', 'country': 'Brazil'},
            {'username': 'AhmedKhalil', 'email': 'ahmed@flavorhub.com', 'country': 'Egypt'},
            {'username': 'LiWei', 'email': 'liwei@flavorhub.com', 'country': 'China'},
            {'username': 'OlgaPetrova', 'email': 'olga@flavorhub.com', 'country': 'Russia'},
            {'username': 'DiegoGarcia', 'email': 'diego@flavorhub.com', 'country': 'Spain'},
            {'username': 'KwameAsante', 'email': 'kwame@flavorhub.com', 'country': 'Ghana'},
            {'username': 'SophiaKowalski', 'email': 'sophia@flavorhub.com', 'country': 'Poland'},
            {'username': 'IsabellaRomano', 'email': 'isabella@flavorhub.com', 'country': 'Argentina'},
            {'username': 'HassanMohamed', 'email': 'hassan@flavorhub.com', 'country': 'Somalia'},
            {'username': 'NurhayatiSukarno', 'email': 'nurhayati@flavorhub.com', 'country': 'Indonesia'},
            {'username': 'KofiMensah', 'email': 'kofi@flavorhub.com', 'country': 'Ivory Coast'},
            {'username': 'AnastasiaVolkov', 'email': 'anastasia@flavorhub.com', 'country': 'Ukraine'},
            {'username': 'RajeshPatel', 'email': 'rajesh@flavorhub.com', 'country': 'Pakistan'},
        ]
        
        users = {}
        for user_data in new_users:
            existing = User.query.filter_by(username=user_data['username']).first()
            if not existing:
                user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    password_hash=generate_password_hash('password123')
                )
                db.session.add(user)
                db.session.commit()
                users[user_data['country']] = user
                print(f"Created user: {user.username} from {user_data['country']}")
            else:
                users[user_data['country']] = existing
                print(f"User {user_data['username']} already exists")
        
        new_recipes = [
            {
                'title': 'Sushi Rolls',
                'description': 'Fresh Japanese sushi with vinegared rice, nori, and fresh fish',
                'ingredients': '2 cups sushi rice\n3 cups water\n1/4 cup rice vinegar\n2 tbsp sugar\n1 tsp salt\nNori sheets\nFresh salmon\nCucumber\nAvocado\nSoy sauce\nWasabi\nPickled ginger',
                'instructions': '1. Cook sushi rice\n2. Mix vinegar, sugar, salt\n3. Cool rice with vinegar mixture\n4. Place nori on bamboo mat\n5. Spread rice on nori\n6. Add fish and vegetables\n7. Roll tightly\n8. Slice into pieces\n9. Serve with soy sauce and wasabi',
                'prep_time': 30,
                'cook_time': 20,
                'servings': 4,
                'country': 'Japan',
                'image_url': 'https://images.unsplash.com/photo-1579584425555-c3ce17fd4351?w=600',
                'user_id': users['Japan'].id
            },
            {
                'title': 'Coq au Vin',
                'description': 'Classic French braised chicken in red wine with mushrooms and pearl onions',
                'ingredients': '1 whole chicken, cut up\n750ml red wine\n200g bacon\n250g mushrooms\n12 pearl onions\n3 cloves garlic\n2 carrots\n2 tbsp flour\nBouquet garni\nButter\nSalt and pepper',
                'instructions': '1. Brown bacon in pot\n2. Brown chicken pieces\n3. Add vegetables\n4. Sprinkle with flour\n5. Add wine and bouquet garni\n6. Simmer 45 minutes\n7. Add mushrooms\n8. Cook 15 more minutes\n9. Serve with crusty bread',
                'prep_time': 20,
                'cook_time': 65,
                'servings': 4,
                'country': 'France',
                'image_url': 'https://images.unsplash.com/photo-1598103442097-8b74394b95c6?w=600',
                'user_id': users['France'].id
            },
            {
                'title': 'Feijoada',
                'description': 'Brazilian black bean stew with pork, the national dish of Brazil',
                'ingredients': '500g black beans\n300g pork ribs\n200g bacon\n200g sausage\n1 onion\n4 cloves garlic\n2 bay leaves\nOrange slices\nRice\nCollard greens\nFarofa',
                'instructions': '1. Soak beans overnight\n2. Cook beans with bay leaves\n3. Brown all meats\n4. Add meats to beans\n5. Simmer 2 hours\n6. Sauté garlic and onion\n7. Add to stew\n8. Serve with rice, greens, farofa\n9. Garnish with orange slices',
                'prep_time': 720,
                'cook_time': 150,
                'servings': 8,
                'country': 'Brazil',
                'image_url': 'https://images.unsplash.com/photo-1623855244183-c5e8f29c6c4d?w=600',
                'user_id': users['Brazil'].id
            },
            {
                'title': 'Koshari',
                'description': 'Egyptian street food with rice, lentils, pasta, and spicy tomato sauce',
                'ingredients': '1 cup rice\n1 cup lentils\n1 cup small pasta\n2 onions, fried\n400g tomato sauce\n3 cloves garlic\n2 tsp cumin\n1 tsp coriander\nChili flakes\nVinegar\nChickpeas',
                'instructions': '1. Cook rice, lentils, pasta separately\n2. Fry onions until crispy\n3. Make tomato sauce with garlic and spices\n4. Layer rice, lentils, pasta\n5. Top with chickpeas\n6. Pour tomato sauce\n7. Add fried onions\n8. Serve with vinegar-chili sauce',
                'prep_time': 15,
                'cook_time': 40,
                'servings': 6,
                'country': 'Egypt',
                'image_url': 'https://images.unsplash.com/photo-1585937421612-70e008356f33?w=600',
                'user_id': users['Egypt'].id
            },
            {
                'title': 'Kung Pao Chicken',
                'description': 'Spicy Sichuan stir-fry with chicken, peanuts, and dried chilies',
                'ingredients': '500g chicken breast\n1/2 cup peanuts\n10 dried chilies\n3 cloves garlic\n1 inch ginger\n3 tbsp soy sauce\n2 tbsp rice vinegar\n1 tbsp sugar\nCornstarch\nSichuan peppercorns\nGreen onions',
                'instructions': '1. Cube chicken, marinate with cornstarch\n2. Toast peanuts and set aside\n3. Mix sauce ingredients\n4. Heat wok very hot\n5. Stir-fry chicken\n6. Add chilies and peppercorns\n7. Add garlic and ginger\n8. Pour in sauce\n9. Toss with peanuts\n10. Garnish with green onions',
                'prep_time': 20,
                'cook_time': 10,
                'servings': 4,
                'country': 'China',
                'image_url': 'https://images.unsplash.com/photo-1585032226651-759b368d7246?w=600',
                'user_id': users['China'].id
            },
            {
                'title': 'Beef Stroganoff',
                'description': 'Russian comfort food with tender beef in creamy mushroom sauce',
                'ingredients': '600g beef strips\n300g mushrooms\n1 onion\n2 cloves garlic\n1 cup sour cream\n1 cup beef broth\n2 tbsp flour\nButter\nDijon mustard\nPaprika\nEgg noodles',
                'instructions': '1. Season beef with salt and paprika\n2. Brown beef in butter\n3. Remove and set aside\n4. Sauté onions and mushrooms\n5. Add garlic\n6. Sprinkle flour\n7. Add broth and mustard\n8. Return beef to pan\n9. Stir in sour cream\n10. Serve over egg noodles',
                'prep_time': 15,
                'cook_time': 25,
                'servings': 4,
                'country': 'Russia',
                'image_url': 'https://images.unsplash.com/photo-1600891964092-4316c288032e?w=600',
                'user_id': users['Russia'].id
            },
            {
                'title': 'Paella Valenciana',
                'description': 'Spanish rice dish with chicken, rabbit, and vegetables from Valencia',
                'ingredients': '2 cups bomba rice\n500g chicken\n300g rabbit\n200g green beans\n1 cup lima beans\n4 tomatoes\nSaffron\nPaprika\n4 cups chicken stock\nOlive oil\nRosemary',
                'instructions': '1. Heat paella pan with olive oil\n2. Brown chicken and rabbit\n3. Add green beans and lima beans\n4. Add grated tomato\n5. Season with paprika\n6. Add rice and spread evenly\n7. Pour hot stock with saffron\n8. Cook without stirring 20 minutes\n9. Let rest 5 minutes\n10. Serve with lemon wedges',
                'prep_time': 20,
                'cook_time': 45,
                'servings': 6,
                'country': 'Spain',
                'image_url': 'https://images.unsplash.com/photo-1534080564583-6be75777b70a?w=600',
                'user_id': users['Spain'].id
            },
            {
                'title': 'Jollof Rice with Plantains',
                'description': 'Ghanaian version of the beloved West African rice dish',
                'ingredients': '3 cups rice\n400g tomato paste\n4 tomatoes\n2 onions\n3 tbsp curry powder\nThyme\nBay leaves\nChicken stock\nScotch bonnet\nRipe plantains\nOil',
                'instructions': '1. Blend tomatoes and onions\n2. Fry tomato paste until oil separates\n3. Add blended mixture\n4. Cook 20 minutes\n5. Add spices and stock\n6. Add rice\n7. Cover and cook 30 minutes\n8. Fry plantain slices\n9. Serve rice with plantains',
                'prep_time': 30,
                'cook_time': 55,
                'servings': 6,
                'country': 'Ghana',
                'image_url': 'https://images.unsplash.com/photo-1604329760661-e71dc83f8f26?w=600',
                'user_id': users['Ghana'].id
            },
            {
                'title': 'Pierogi',
                'description': 'Polish dumplings filled with potato and cheese, pan-fried with onions',
                'ingredients': '3 cups flour\n1 egg\n1 cup water\n4 potatoes\n200g cheese\n2 onions\nButter\nSour cream\nSalt',
                'instructions': '1. Make dough with flour, egg, water\n2. Rest 30 minutes\n3. Boil and mash potatoes\n4. Mix with cheese\n5. Roll dough thin\n6. Cut circles\n7. Fill with potato mixture\n8. Seal edges\n9. Boil until they float\n10. Fry with onions in butter\n11. Serve with sour cream',
                'prep_time': 60,
                'cook_time': 30,
                'servings': 6,
                'country': 'Poland',
                'image_url': 'https://images.unsplash.com/photo-1626200419199-391ae4be7a41?w=600',
                'user_id': users['Poland'].id
            },
            {
                'title': 'Empanadas',
                'description': 'Argentine baked pastries filled with beef, olives, and hard-boiled eggs',
                'ingredients': '500g ground beef\n2 onions\n2 hard-boiled eggs\n1/2 cup olives\n1 tsp cumin\n1 tsp paprika\nEmpanada dough\nEgg wash',
                'instructions': '1. Sauté onions until soft\n2. Add beef and spices\n3. Cook until browned\n4. Cool mixture\n5. Add chopped eggs and olives\n6. Roll out dough\n7. Cut circles\n8. Fill with mixture\n9. Fold and crimp edges\n10. Brush with egg wash\n11. Bake at 375°F for 25 minutes',
                'prep_time': 40,
                'cook_time': 25,
                'servings': 12,
                'country': 'Argentina',
                'image_url': 'https://images.unsplash.com/photo-1599974789516-e36e5d2f1a8d?w=600',
                'user_id': users['Argentina'].id
            },
            {
                'title': 'Bariis Iskukaris',
                'description': 'Somali spiced rice with lamb, raisins, and caramelized onions',
                'ingredients': '2 cups basmati rice\n500g lamb\n2 onions\n1/4 cup raisins\n4 cloves\n4 cardamom pods\n1 cinnamon stick\nCumin\nTurmeric\nYogurt\nCoriander',
                'instructions': '1. Marinate lamb in yogurt and spices\n2. Caramelize onions\n3. Brown lamb\n4. Add whole spices\n5. Add rice and toast\n6. Pour in stock\n7. Add raisins\n8. Cover and cook 20 minutes\n9. Garnish with fried onions and coriander',
                'prep_time': 30,
                'cook_time': 50,
                'servings': 6,
                'country': 'Somalia',
                'image_url': 'https://images.unsplash.com/photo-1596797038530-2c107229654b?w=600',
                'user_id': users['Somalia'].id
            },
            {
                'title': 'Nasi Goreng',
                'description': 'Indonesian fried rice with sweet soy sauce, topped with fried egg',
                'ingredients': '4 cups cooked rice\n3 eggs\n200g chicken\n3 cloves garlic\n2 shallots\n2 chilies\nKecap manis\nShrimp paste\nFish sauce\nVegetables\nCucumber\nTomato',
                'instructions': '1. Beat 2 eggs, make thin omelet\n2. Slice omelet into strips\n3. Blend garlic, shallots, chilies\n4. Fry paste with shrimp paste\n5. Add chicken\n6. Add rice and break up\n7. Season with kecap manis\n8. Add vegetables\n9. Fry remaining eggs\n10. Serve rice topped with fried egg',
                'prep_time': 20,
                'cook_time': 15,
                'servings': 4,
                'country': 'Indonesia',
                'image_url': 'https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=600',
                'user_id': users['Indonesia'].id
            },
            {
                'title': 'Kedjenou',
                'description': 'Ivorian slow-cooked chicken stew with vegetables, no added water',
                'ingredients': '1 whole chicken\n3 tomatoes\n2 onions\n2 eggplants\n3 cloves garlic\n1 inch ginger\n2 scotch bonnets\nThyme\nBay leaves\nPalm oil',
                'instructions': '1. Cut chicken into pieces\n2. Chop all vegetables\n3. Layer chicken and vegetables in pot\n4. Add spices and chilies\n5. Drizzle with palm oil\n6. Cover tightly\n7. Cook on low heat 1.5 hours\n8. Shake pot occasionally, do not stir\n9. Serve with attiéké or rice',
                'prep_time': 20,
                'cook_time': 90,
                'servings': 4,
                'country': 'Ivory Coast',
                'image_url': 'https://images.unsplash.com/photo-1598103442097-8b74394b95c6?w=600',
                'user_id': users['Ivory Coast'].id
            },
            {
                'title': 'Borscht',
                'description': 'Ukrainian beet soup, served hot or cold with sour cream',
                'ingredients': '4 beets\n2 potatoes\n1 carrot\n1 onion\n2 cloves garlic\n400g cabbage\n400g tomatoes\n6 cups stock\nBay leaves\nDill\nSour cream\nVinegar',
                'instructions': '1. Grate beets and carrot\n2. Dice potatoes and cabbage\n3. Sauté onion and garlic\n4. Add beets and carrot\n5. Add tomatoes\n6. Pour in stock\n7. Add potatoes and cabbage\n8. Add bay leaves\n9. Simmer 30 minutes\n10. Add vinegar and dill\n11. Serve with sour cream',
                'prep_time': 20,
                'cook_time': 45,
                'servings': 6,
                'country': 'Ukraine',
                'image_url': 'https://images.unsplash.com/photo-1604908815453-e9d1b0a6e4f7?w=600',
                'user_id': users['Ukraine'].id
            },
            {
                'title': 'Nihari',
                'description': 'Pakistani slow-cooked beef stew with aromatic spices, eaten with naan',
                'ingredients': '1kg beef shank\n2 onions\n1/4 cup ghee\n2 tbsp nihari masala\n1 tbsp ginger-garlic paste\n2 tsp red chili\n1 tsp turmeric\nFlour\nGaram masala\nGinger julienne\nCoriander\nLemon',
                'instructions': '1. Brown onions in ghee\n2. Add ginger-garlic paste\n3. Add beef and spices\n4. Cover with water\n5. Simmer 3-4 hours until tender\n6. Make paste with flour and water\n7. Add to thicken gravy\n8. Garnish with ginger, coriander\n9. Serve with naan and lemon',
                'prep_time': 20,
                'cook_time': 240,
                'servings': 6,
                'country': 'Pakistan',
                'image_url': 'https://images.unsplash.com/photo-1585937421612-70e008356f33?w=600',
                'user_id': users['Pakistan'].id
            },
        ]
        
        for recipe_data in new_recipes:
            existing = Recipe.query.filter_by(title=recipe_data['title']).first()
            if not existing:
                recipe = Recipe(**recipe_data)
                db.session.add(recipe)
        
        db.session.commit()
        print(f"\nSuccessfully added {len(new_recipes)} new recipes from 15 countries!")
        print("New countries added: Japan, France, Brazil, Egypt, China, Russia, Spain,")
        print("Ghana, Poland, Argentina, Somalia, Indonesia, Ivory Coast, Ukraine, Pakistan")

if __name__ == '__main__':
    add_global_recipes()
