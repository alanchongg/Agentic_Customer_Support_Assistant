import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from func import *
from mail_handler import *

load_dotenv()

def get_response(new_msg):
    client = OpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=os.environ["HF_TOKEN"],
    )
    
    message=[{
                "role": "system",
                "content": "You are a friendly customer support assistant for a TCG store."
                "Your task is to draft a email response to a customer's inquiry."
                "Keep your response concise and informative, addressing the customer's question directly and try to end the conversation in your response. Do not suggest extra information that is not relevant to the customer's inquiry."
                "Should you need the store information, the Store information are as follow: the store is caleld TCG hope, located at 123 pika street, operating hours are 10am to 8pm Monday to Friday. There is strictly no refund policy, but customers can exchange their cards within 7 days of purchase."
                "In your reply include greetings, main body and sign off"
            },
            {
                "role": "user",
                "content": new_msg
            }
        ]

    completion = client.chat.completions.create(
        model="meta-llama/Llama-3.3-70B-Instruct:groq",
        messages=message,
        tools=tools,
        tool_choice="auto",
    )

    response_message = completion.choices[0].message
    tool_calls = response_message.tool_calls

    if tool_calls:
        message.append(response_message)

        for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = tool_call.function.arguments
                function_args = json.loads(function_args)

                if function_name == "get_inventory":
                    item_name = function_args.get("item")
                    inventory_result = get_inventory(item_name)
                    tool_call.result = inventory_result

                    message.append(
                        {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": inventory_result,
                        }
                    )

    reply = client.chat.completions.create(
        model="meta-llama/Llama-3.3-70B-Instruct:groq",
        messages=message,
    )

    return reply.choices[0].message.content