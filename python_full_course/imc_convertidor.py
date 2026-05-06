try:
    weight = float(input("Enter your weight: "))
    height = float(input("Enter your height: "))
    
    index = weight / (height ** 2)
    if index <= 18.5:
        print("Underweight")
    elif index <= 25.0:
        print("Normal")
    elif index <= 30.0:
        print("Overweight")
    else:
        print("Obese")

except ValueError:
    print("Invalid input. Weight and height should be numbers.")
except ZeroDivisionError:
    print("Height cannot be zero.")
    
try:
    age = float(input("Enter your age: "))
    if age < 5:
        print("You're too young to use this BMI")
    elif age < 18:
        print("You're a Young")
    elif age < 70:
        print("You're an adult")
    else:
        print("You're too old to use this BMI")
except ValueError:
        print("Invalid input. Age should be a number.") 

