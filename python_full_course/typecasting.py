# Typecasting  = the process of converting a variable form one data type to another
#                str(), int(), float(), bool()

name = "Jeison"
age = 27
gpa = 3.2
is_student = True

print (type(name))
print (type(age))
print (type(gpa))
print (type(is_student))

gpa = int(gpa)

print(gpa)

age = float(age)
print(age)

name = bool(name)
print(name)
# this is specially useful with handling user input