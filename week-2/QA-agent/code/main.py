from src.chat import chat


def main():
    user_id = input("Who are you?")
    user_prompt = ""

    print("q = quit")
    while True:
        user_prompt = input(f"{user_id}(you'r prompt):")
        if user_prompt.lower() == "q":
            print("good bye!")
            break

        chat(q=user_prompt, user_id=user_id)


if __name__ == "__main__":
    main()
