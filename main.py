import random


def greet_user():
    name = input("What is your name? ").strip()
    if not name:
        name = "Friend"
    print(f"Welcome, {name}! Welcome to the Simple Helper program.\n")


def simple_calculator():
    print("Simple Calc")
    print("Enter two numbers and an operator (+, -, *, /).\n")
    try:
        a = float(input("First number: "))
        b = float(input("Second number: "))
        op = input("Operator: ").strip()
        if op == "+":
            result = a + b
        elif op == "-":
            result = a - b
        elif op == "*":
            result = a * b
        elif op == "/":
            result = a / b
        else:
            print("Unknown operator. Please use +, -, *, or /.\n")
            return
        print(f"Result: {result}\n")
    except ValueError:
        print("Please enter valid numbers.\n")
    except ZeroDivisionError:
        print("Cannot divide by zero.\n")


def guess_number():
    print("Number Guessing Game")
    target = random.randint(1, 20)
    attempts = 0
    print("I'm thinking of a number between 1 and 20.")
    while attempts < 7:
        try:
            guess = int(input("Take a guess: "))
        except ValueError:
            print("Please enter a whole number.")
            continue
        attempts += 1
        if guess == target:
            print(f"Great job! You guessed it in {attempts} attempts.\n")
            return
        if guess < target:
            print("Too low. Try again.")
        else:
            print("Too high. Try again.")
    print(f"Nice try! The number was {target}.\n")


def main():
    greet_user()
    while True:
        print("Choose what you want to do:")
        print("1) Use the calculator")
        print("2) Play a guessing game")
        print("3) Exit")
        choice = input("Enter 1, 2, or 3: ").strip()
        print()
        if choice == "1":
            simple_calculator()
        elif choice == "2":
            guess_number()
        elif choice == "3":
            print("Goodbye! Have a great day.")
            break
        else:
            print("Please choose 1, 2, or 3.\n")


if __name__ == "__main__":
    main()