from openai import OpenAI
from dotenv import load_dotenv
import dspy


load_dotenv()
client = OpenAI()

gpt4o = dspy.LM("openai/gpt-4o", temperature=0)
dspy.configure(lm=gpt4o)

def ai(system_prompt="You are a helpful assistant", user_prompt="Hello"):
    response = client.chat.completions.create(
        # model="deepseek-chat",
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        stream=False,
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    response = ai()
    print(response)
