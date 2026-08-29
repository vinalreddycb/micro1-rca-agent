import subprocess

print("Starting the 10-Case Evaluation Batch...")
print("This will take about 60-90 seconds. Please wait...\n")

with open("evaluation_results.txt", "w") as f:
    for i in range(1, 11):
        file_name = f"data/scenario_{i:02d}.csv"
        
        # Write the headers to the text file
        f.write(f"\n{'='*60}\n")
        f.write(f"SCENARIO {i:02d}: {file_name}\n")
        f.write(f"{'='*60}\n\n")
        
        print(f"Processing Scenario {i:02d}...")
        
        # Run Baseline
        f.write("--- BASELINE SCRIPT ---\n")
        base_result = subprocess.run(["python", "src/baseline.py", file_name], capture_output=True, text=True)
        f.write(base_result.stdout)
        f.write("\n")
        
        # Run Agent
        f.write("--- AGENT SCRIPT ---\n")
        agent_result = subprocess.run(["python", "src/agent.py", file_name], capture_output=True, text=True)
        f.write(agent_result.stdout)
        f.write("\n")

print("\nEvaluation complete! Open 'evaluation_results.txt' to view all the outputs.")