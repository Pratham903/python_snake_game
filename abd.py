import random

# Generate a list of 10 random floats between 0 and 1
random_floats = [random.random() for _ in range(10)]
print('Random floats:', random_floats)

# Shuffle the list
random.shuffle(random_floats)
print('Shuffled floats:', random_floats)

# Get the average value
avg = sum(random_floats) / len(random_floats)
print('Average:', avg)