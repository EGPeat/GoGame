def p(input):
    print(input)
size=None
p("Please enter in the size you wish to have your Go Board as.\n Please type (9) for a 9x9, (13) for a 13x13, or (17) for 17x17:")

while True:
    try:
        size=int(input())
        

        break
    except ValueError:
        p("It seems you entered something that isn't a int. Please try again")


p(f"You have choosen a {size}x{size} board.")