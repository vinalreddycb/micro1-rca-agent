import sys
import os
import json
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv

# Load the secure API key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Global variable to track the active file during batch processing
ACTIVE_CSV = ""

# 1. Define the Tool
def slice_ecommerce_data(dimensions: list) -> str:
    print(f"\n[Agent is using tool: Grouping by {dimensions}]")
    try:
        # Dynamically read the file passed from the command line
        df = pd.read_csv(ACTIVE_CSV)
        grouped = df.groupby(dimensions)[['Sessions', 'Orders']].sum().reset_index()
        grouped['Conversion_Rate'] = (grouped['Orders'] / grouped['Sessions']).round(4)
        grouped = grouped.sort_values(by='Conversion_Rate', ascending=True)
        return grouped.head(10).to_string(index=False)
    except Exception as e:
        return f"Error executing tool: {str(e)}"

# 2. Set up the Agent Loop
def run_agent(csv_path):
    global ACTIVE_CSV
    ACTIVE_CSV = csv_path
    
    print(f"Starting RCA Agent analysis on {csv_path}...\n")
    
    system_instruction = """
    You are an autonomous Root Cause Analysis (RCA) agent reporting to the CDAO.
    A major e-commerce Conversion Rate drop has occurred.
    
    CRITICAL GUARDRAILS:
    1. ONLY use the following exact dimensions in your tool calls:
       ['Pincode', 'Region', 'Category', 'Platform', 'Payment_Type', 'Promo_Code', 'Inventory_Status']
    2. Group by 1, 2, or 3 dimensions simultaneously (e.g., ['Platform', 'Payment_Type']).
    3. Once you find the exact segment where Orders dropped to near zero, STOP calling the tool.
    
    Output your final text response using the Executive Brief Framework:
    - OBSERVATION: The macro drop.
    - ROOT CAUSE: The exact segment driving the drop.
    - EVIDENCE: Cite the specific Orders and Sessions from your tool usage.
    """
    
    tools = [{
        "type": "function",
        "function": {
            "name": "slice_ecommerce_data",
            "description": "Groups data by specific dimensions and calculates the Conversion Rate.",
            "parameters": {
                "type": "object",
                "properties": {
                    "dimensions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of column names to group by."
                    }
                },
                "required": ["dimensions"]
            }
        }
    }]
    
    messages = [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": f"Analyze the dataset located at '{csv_path}'. Find the root cause of the conversion drop."}
    ]
    
    for _ in range(10): 
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools,
            temperature=0.0
        )
        
        message = response.choices[0].message
        messages.append(message)
        
        if message.tool_calls:
            for tool_call in message.tool_calls:
                args = json.loads(tool_call.function.arguments)
                tool_result = slice_ecommerce_data(args.get("dimensions", []))
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result
                })
        else:
            print("\nFinal Executive Brief:")
            print(message.content)
            print("-" * 50)
            break

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "data/scenario_01.csv"
    run_agent(target)