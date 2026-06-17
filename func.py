import pandas as pd
import os

tools=[
    {   
        "type": "function",
        "function": {
            "name": "get_inventory",
            "description": "Find availability and price using a specific item name",
            "parameters": {
                "type": "object",
                "properties": {
                    "item": {
                        "type": "string",
                        "description": "Name of item to check in the inventory, e.g. one piece eb-03, pokemon abyss eye",
                    }
                },
                "required": ["item"],
            },
        },
    }
]

# read inventory
file_path = "inventory.xlsx"
if not os.path.exists(file_path):
    raise FileNotFoundError(f"Inventory file not found: {file_path}")
df = pd.read_excel(file_path)

def get_inventory(item_name: str):
    res=df.loc[df['Item'].str.contains(item_name,case=False, na=False)]
    return res.to_json(orient="records")