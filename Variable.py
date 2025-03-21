# Variable = A cointainer for a value (string, integer, float, boolear)
#            A variable behaves as if it was the value it contains

# Strings = A series of characters, they can include number that we treat them like characters
first_name = "bro"
food = "pizza"
email = "bro123@fake.com"

print(first_name)

print (f"Hello {first_name}")
print (f"You like {food}")
print (f"Your email is: {email}")

# Integers = A whole number - " " is for characters - amount of ppl
age = 25
quantity = 3
num_of_students = 30

print(f"You are {age} years old")
print(f"You are buying {quantity} items")
print(f"Your class has {num_of_students} students")

# Float meaning floating pointing number - Float contains decimal portion (.99 for example)
# gpa = grade per average
price = 10.99
gpa = 3.2
distance = 5.5

print(f"The price is ${price}")
print(f"Your gpa is {gpa}")
print(f"Your ran {distance} km")

# Booleans either true or false - First letter ist capital (Mayus)

is_student = True

print(f"Are you a student?: {is_student} ")  #Example

if is_student:
    print("You are a student")
else:
    print("You are NOT a student")

is_student = False

print(f"Are you a student?: {is_student} ")  #Example

if is_student:
    print("You are a student")
else:
    print("You are NOT a student")

for_sale = True

if for_sale:
    print("That item is for a sale")
else:
    print("That item is NOT available")

for_sale = False

if for_sale:
    print("That item is for a sale")
else:
    print("That item is NOT available")

is_online = True

if is_online:
    print("You are online")
else:
    print("Your are offline")

is_online = False

if is_online:
    print("You are online")
else:
    print("Your are offline")