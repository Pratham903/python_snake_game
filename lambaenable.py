import random
import string

# Generate a random string
def random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Create a list of random strings
strings = [random_string(8) for _ in range(5)]
print('Random strings:', strings)

# Generate a random matrix
matrix = [[random.randint(1, 100) for _ in range(3)] for _ in range(3)]
print('Random matrix:')
for row in matrix:
    print(row)

# Find the sum of each row
row_sums = [sum(row) for row in matrix]
print('Row sums:', row_sums)

# Find the max value in the matrix
max_val = max(max(row) for row in matrix)
print('Max value in matrix:', max_val)