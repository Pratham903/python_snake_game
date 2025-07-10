import random

# Generate 5 random coordinates for snake food
food_positions = [(random.randint(0, 20), random.randint(0, 20)) for _ in range(5)]
print('Food positions:', food_positions)

# Generate a random snake length
snake_length = random.randint(3, 10)
print('Snake length:', snake_length)

# Randomly choose a direction
direction = random.choice(['UP', 'DOWN', 'LEFT', 'RIGHT'])
print('Direction:', direction)