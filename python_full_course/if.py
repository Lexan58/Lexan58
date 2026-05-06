# if = Do some code If some condition is True
#      Else do something else
#      

age = int(input("Enter yout age: "))


if age >=100:
    print("You are too old to sign up")
elif age >= 18:
    print("You are now signed up!")
elif age < 0:
    print("You haven't been born yet")
else: 
    print("You must be 18+ to signed up!")