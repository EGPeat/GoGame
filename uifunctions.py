import PySimpleGUI as sg


def p(input):
    print(input)


def pt(input):
    print(type(input))


def StartGame():
    info = "Please enter in the size you wish to have your Go Board as.\nPlease type (9) for a 9x9, (13) for a 13x13, or (17) for 17x17:"

    while True:
        try:
            size = sg.popup_get_text(info, title="Please Enter Text", font=('Arial Bold', 15))
            size = int(size)
            if size not in [9, 13, 17]:
                raise SyntaxError

            break
        except ValueError:
            info = "It seems you entered something that isn't a int. Please try again"
        except SyntaxError:
            info = "It seems you entered a number that isn't 9, 13, 17. Please try again"

    p(f"You have choosen a {size}x{size} board.")
    return size


def inputVal(maxSize=16, valType=int, options=False):

    while True:
        try:
            if not options:
                info = valType(input())
                if isinstance(info, str) and (len(info) > maxSize):
                    raise IndexError
                elif isinstance(info, int) and (info > maxSize):
                    raise IndexError
                return info
            else:
                info = input()
                if info.isnumeric():
                    info = int(info)
                    if info > maxSize:
                        raise IndexError
                    return info
                elif isinstance(info, str) and (len(info) > maxSize):
                    raise IndexError
                return info

        except ValueError:
            info = f"It seems you entered something that isn't a {valType}. Please try again"
        except IndexError:
            info = "you put in something that is a larger int than is allowed, or a longer string than is allowed"
