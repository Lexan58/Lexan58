# input() = A function that prompts the user to enter data
#           Returns the entered data as a string

name = input("What is your name?: ")
age = input("How old are you?: ")

# Condense form: age = int(input ("how old are you? "))
age = int(age)
age = age + 1

print(f"Hello {name}!")
print("happy birthday")
print(f"You are {age} years old")



