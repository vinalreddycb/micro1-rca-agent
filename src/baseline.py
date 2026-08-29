import sys
import os
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv

# Load the secure API key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def run_baseline(csv_path):
    print(f"Running baseline on {csv_path}...")
    df = pd.read_csv(csv_path)
    csv_text = df.to_csv(index=False)
    
    prompt = f"""
    You are a data analyst. Look at the following e-commerce data.
    The overall Conversion Rate (Orders / Sessions) has dropped significantly.
    Identify the mathematical root cause of the drop. Answer in 2-3 sentences.
    
    Data:
    {csv_text}
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )
    
    print("\nBaseline Response:")
    print(response.choices[0].message.content)
    print("-" * 50)

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "data/scenario_01.csv"
    run_baseline(target)
