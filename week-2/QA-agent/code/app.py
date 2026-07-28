from src.chat import chat
from config import get_settings

import os


def main():
    settings = get_settings()
    print(settings.GROQ_API_KEY)  # TODO, it prints none, fix it
    user_id = input("Who are you? ")
    user_prompt = ""

    if settings.USE_PROXY:
        os.environ["http_proxy"] = settings.PROXY_LINK
        os.environ["https_proxy"] = settings.PROXY_LINK

    print("q = quit")
    while True:
        user_prompt = input(f"{user_id} (you'r prompt): ")
        if user_prompt.lower() == "q":
            print("good bye!")
            break

        chat(q=user_prompt, user_id=user_id)


if __name__ == "__main__":
    main()
