# collection = single "variable" used to store multiple values
#     List   = [] ordered and changeable. Duplicates OK
#     Set    = {} unordered and inmmutable, but Add/remove OK. NO duplicates
#     Tuple  = () ordered and unchangeable. Duplicates OK. FASTER

fruits = ["apple", "orange", "banana", "coconut"]
# print(dir(fruits))
# print(help(fruits))
# print(len(fruits))
# print("apple" in fruits)

# fruits[0] = "pineapple"
# print(fruits[0])

# print(fruit[:3])

#for x in fruits:
#    print(x)

# fruits.append("pineapple")
# fruits.remove("apple")
# fruits.insert(0, "pinneaple")
# fruits.sort()
# fruits.reverse()
# fruits.clear()
# print(fruits.index("apple"))
# print(fruits.count("apple"))

for fruit in fruits:
    print(fruit)