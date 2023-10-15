import icecream as ic
def p(input):
    print(input)
def pt(input):
    print(type(input))

def StartGameDefault(size=9):
    p(f"You have choosen a {size}x{size} board.")
    return size

def StartGame():
    size=None
    p("Please enter in the size you wish to have your Go Board as.\n Please type (9) for a 9x9, (13) for a 13x13, or (17) for 17x17:")

    while True:
        try:
            size=int(input())
            if size not in [9,13,17]:
                raise SyntaxError

            break
        except ValueError:
            p("It seems you entered something that isn't a int. Please try again")
        except SyntaxError:
            p("It seems you entered a number that isn't 9, 13, 17. Please try again")


    p(f"You have choosen a {size}x{size} board.")
    return size

