import random

# Generate a list of 5 random numbers between 1 and 50
nums = [random.randint(1, 50) for _ in range(5)]

# Print the list of random numbers
print('Random numbers:', nums)

# Print the maximum value from the list of random numbers
print('Max:', max(nums))