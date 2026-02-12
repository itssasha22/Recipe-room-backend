from app import app, db
from models import User, Recipe
from datetime import datetime

def seed_data():
    with app.app_context():
        # Check if users exist, create if not
        user1 = User.query.filter_by(email='test2@example.com').first()
        if not user1:
            user1 = User(username='testuser2', email='test2@example.com')
            user1.set_password('test123')
            db.session.add(user1)
        
        user2 = User.query.filter_by(email='mary@example.com').first()
        if not user2:
            user2 = User(username='chef_mary', email='mary@example.com')
            user2.set_password('test123')
            db.session.add(user2)
        
        db.session.commit()
        
        # Create sample recipes
        recipes = [
            Recipe(
                title='Caesar Salad',
                description='A classic Caesar salad with crispy romaine lettuce',
                ingredients='Romaine lettuce, Parmesan cheese, Croutons, Caesar dressing',
                instructions='1. Wash and chop romaine lettuce\n2. Add croutons and parmesan\n3. Toss with Caesar dressing',
                image_url='https://images.unsplash.com/photo-1546793665-c74683f339c1?w=400',
                prep_time=15,
                cook_time=0,
                servings=4,
                country='Italy',
                user_id=user1.id
            ),
            Recipe(
                title='Spaghetti Carbonara',
                description='Traditional Italian pasta with creamy egg sauce',
                ingredients='Spaghetti, Eggs, Pancetta, Parmesan, Black pepper',
                instructions='1. Cook spaghetti\n2. Fry pancetta\n3. Mix eggs and cheese\n4. Combine all ingredients',
                image_url='https://images.unsplash.com/photo-1612874742237-6526221588e3?w=400',
                prep_time=10,
                cook_time=20,
                servings=4,
                country='Italy',
                user_id=user1.id
            ),
            Recipe(
                title='Nyama Choma',
                description='Traditional Kenyan grilled meat',
                ingredients='Goat meat, Salt, Oil',
                instructions='1. Season meat with salt\n2. Grill over charcoal\n3. Serve with ugali',
                image_url='https://images.unsplash.com/photo-1544025162-d76694265947?w=400',
                prep_time=15,
                cook_time=60,
                servings=6,
                country='Kenya',
                user_id=user2.id
            ),
            Recipe(
                title='Beef Burger',
                description='Juicy beef burger with all the fixings',
                ingredients='Ground beef, Burger buns, Lettuce, Tomato, Cheese, Onions',
                instructions='1. Form beef patties\n2. Grill patties\n3. Toast buns\n4. Assemble burger',
                image_url='https://images.unsplash.com/photo-1568901346375-23ac9450c58c?w=400',
                prep_time=15,
                cook_time=20,
                servings=4,
                country='USA',
                user_id=user2.id
            ),
            Recipe(
                title='Chicken Fried Rice',
                description='Quick and easy Asian-style fried rice',
                ingredients='Rice, Chicken, Eggs, Soy sauce, Vegetables, Garlic, Ginger',
                instructions='1. Cook rice\n2. Stir-fry chicken\n3. Add vegetables\n4. Mix in rice and soy sauce',
                image_url='https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=400',
                prep_time=20,
                cook_time=15,
                servings=4,
                country='China',
                user_id=user1.id
            ),
            Recipe(
                title='Margherita Pizza',
                description='Classic Italian pizza with fresh mozzarella',
                ingredients='Pizza dough, Tomato sauce, Mozzarella, Basil, Olive oil',
                instructions='1. Roll out dough\n2. Spread tomato sauce\n3. Add mozzarella\n4. Bake at 450°F\n5. Top with fresh basil',
                image_url='https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=400',
                prep_time=20,
                cook_time=20,
                servings=4,
                country='Italy',
                user_id=user2.id
            ),
            Recipe(
                title='Chicken Tacos',
                description='Authentic Mexican street tacos',
                ingredients='Chicken breast, Tortillas, Cilantro, Onions, Lime, Salsa',
                instructions='1. Season and grill chicken\n2. Dice chicken\n3. Warm tortillas\n4. Assemble tacos with toppings',
                image_url='https://images.unsplash.com/photo-1565299585323-38d6b0865b47?w=400',
                prep_time=15,
                cook_time=20,
                servings=4,
                country='Mexico',
                user_id=user1.id
            ),
            Recipe(
                title='Samosas',
                description='Crispy fried pastries with spiced potato filling',
                ingredients='Flour, Potatoes, Peas, Spices, Oil',
                instructions='1. Make dough\n2. Prepare potato filling\n3. Form samosas\n4. Deep fry until golden',
                image_url='https://images.unsplash.com/photo-1601050690597-df0568f70950?w=400',
                prep_time=40,
                cook_time=20,
                servings=8,
                country='Kenya',
                user_id=user2.id
            )
        ]
        
        db.session.add_all(recipes)
        db.session.commit()
        
        print(f"✅ Created {len(recipes)} sample recipes!")
        print(f"✅ Test users: test2@example.com / test123, mary@example.com / test123")

if __name__ == '__main__':
    seed_data()
