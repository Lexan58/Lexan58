# conditional expression = A one-line shortcut for the if-else statment (ternary operator)
#                          Print or assign one of two values based on a condition
#                          X if condition else Y

num = 5
a = 6
b = 7
age = 25
temperature = 30
user_role = "admin"

#print("Positive" if num > 0 else "Negative")
#result = "EVEN" if num % 2 == 0 else "ODD"
#print(result) 
#max_num = a if a > b else b
#min_num = a if a < b else b
#print(min_num) 
#status = "Adult" if age >= 18 else "child"
#weather = "HOT" if temperature > 20 else "COLD"
#print(weather)
access_level = "Full Access" if user_role == "admin" else "Limited access"

print(access_level)