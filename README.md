# Autonomous Root Cause Analysis (RCA) Agent for E-Commerce

An autonomous agent designed to diagnose sudden drops in conversion rates across high-dimensional e-commerce datasets and produce executive-ready root cause briefs.

---

## 1. Problem & User Value

* **Target User:** Chief Data & Analytics Officers (CDAOs), Heads of Insights, and senior analytics managers overseeing high-volume e-commerce platforms.
* **The Bottleneck:** When conversion rate drops, dashboards signal *that* an issue exists, but do not isolate *why*. Diagnosing root causes requires human analysts to slice multi-dimensional tabular data across millions of rows (by Pincode, Platform, Category, Promo Code, etc.). This manual process takes hours, leading to significant revenue leakage.
* **Why Generic LLMs Fail:** Standard LLMs cannot calculate aggregations across tabular data. Feeding raw CSV text to a baseline prompt results in hallucinations and vague guesses.
* **The Agentic Solution:** This solution pairs an LLM with a dedicated calculation tool (`slice_ecommerce_data`) using Pandas. The agent autonomously formulates hypotheses, groups dimensions iteratively, inspects conversion rate math, and synthesizes its findings into a structured Executive Brief.

---

## 2. Reproduction Guide

Follow these steps to reproduce both the baseline and agent workflows from a clean environment.

### Environment Setup
```bash
# Clone the repository and enter the directory
git clone https://github.com/vinalreddycb/micro1-rca-agent
cd micro1-rca-agent

# Create and activate a clean virtual environment
python3 -m venv venv
source venv/bin/activate

# Install required dependencies
pip install openai pandas python-dotenv
```

### Configure Environment Variables
```bash
# Create a .env file in the project root directory:
OPENAI_API_KEY="your-openai-api-key-here"
```

### Project Structure
```bash
micro1-rca-agent/
├── data/
│   ├── scenario_01.csv ... scenario_10.csv
├── src/
│   ├── baseline.py
│   └── agent.py
├── run_evaluations.py
├── evaluation_results.txt
├── .env
├── README.md
└── requirements.txt
```

### Execution Commands

#### Run Baseline on a Single Scenario:
```bash
python src/baseline.py data/scenario_01.csv
```
Expected Output: A generic explanation lacking exact segment math.

#### Run Autonomous Agent on a Single Scenario:
```bash
python src/agent.py data/scenario_01.csv
```
Expected Output: Dynamic terminal logs showing tool calls (e.g., [Agent is using tool: Grouping by ['Promo_Code']]) followed by a structured Executive Brief.

#### Run the Full 10-Scenario Evaluation Suite:
```bash
python run_evaluations.py
```
Expected Output: Executes baseline and agent across all 10 scenarios and outputs results into evaluation_results.txt.


### Operational Metrics
+ Environment Versions: Python 3.10+, Pandas >= 2.0, OpenAI SDK >= 1.0.0.

+ Model: gpt-4o-mini (temperature = 0.0).

+ Approximate Runtime: ~2 seconds per scenario (~20–30 seconds for all 10 scenarios).

+ Approximate Cost: < $0.005 per scenario run.

---

## 3. Evaluation & Measured Improvement

### 10-Case Evaluation Matrix
*Primary Metric:* **Root Cause Accuracy** (Accurate identification of the failing segment and correct calculation of the associated conversion rate).

| Scenario | Anomaly Type | Baseline (`gpt-4o-mini`) | Agent (`gpt-4o-mini` + Tool) | Outcome |
| :--- | :--- | :--- | :--- | :--- |
| **01** | Promo Code Failure | **Failed:** Guessed "lack of offers / UX issues" | **Passed:** Isolated `DIWALI50` (118,200 sessions, 0 orders, CR: 0.0000) | Accuracy Gain |
| **02** | Category Drop | **Failed:** Guessed "marketing / site performance" | **Passed:** Isolated `Winter Wear` (303,900 sessions, 1,339 orders, CR: 0.0044) | Accuracy Gain |
| **03** | Platform Outage | **Failed:** Guessed "user experience / product appeal" | **Passed:** Isolated `Android_v13` (146,089 sessions, 2,696 orders, CR: 0.0185) | Accuracy Gain |
| **04** | Inventory Stockout | **Partial:** Noted "Out_of_Stock" text without math | **Passed:** Calculated exact `Out_of_Stock` drop (121,473 sessions, 0 orders, CR: 0.0000) | Mathematical Proof |
| **05** | Regional Pincode Outage | **Failed:** Guessed "poor user experience / marketing" | **Passed:** Isolated Pincodes `560102` & `560103` (82,773 total sessions, 0 orders) | Accuracy Gain |
| **06** | Hardware Category Drop | **Failed:** Guessed "customer decision-making" | **Passed:** Isolated `Laptops` (4,538,165 sessions, 2,340 orders, CR: 0.0005) | Accuracy Gain |
| **07** | OS Version Failure | **Failed:** Guessed "marketing effectiveness" | **Passed:** Isolated `iOS_v17.2` (79,044 sessions, 0 orders, CR: 0.0000) | Accuracy Gain |
| **08** | Specific Geo Pincode Drop | **Failed:** Guessed "pricing or user experience" | **Passed:** Isolated Pincode `751001` (45,513 sessions, 748 orders, CR: 0.0164) | Accuracy Gain |
| **09** | Multi-Dimensional Segment Drop | **Failed:** Guessed "marketing / user experience" | **Passed:** Multi-dimensionally grouped `Category` x `Platform` to isolate `FMCG_Groceries` drop | Advanced Reasoning |
| **10** | Payment Method Failure | **Failed:** Guessed "pricing strategies" | **Passed:** Isolated `Wallet` payment type (105,994 sessions, 2,084 orders, CR: 0.0197) | Accuracy Gain |

### Analysis of the Challenging Case (Scenario 09)
In Scenario 09, the conversion drop was distributed across multi-dimensional intersections rather than a single column.
+ Baseline Behavior: Provided high-level commentary about sessions and conversion rates without identifying the affected category.

+ Agent Behavior: After initial single-dimension groupings (Pincode, Region, Category), the agent recognized a systemic drop in FMCG_Groceries and automatically began cross-referencing dimensions: ['Category', 'Platform'], ['Category', 'Payment_Type'], ['Category', 'Promo_Code'], and ['Category', 'Inventory_Status']. It confirmed the anomaly was widespread across all platforms for that specific product category.

---

## 4. Improvement Changelog

| Stage | What Was Tried & Why | Evidence | Decision / Learning |
| :--- | :--- | :--- | :--- |
| **Baseline** | Prompted standard LLM with raw CSV string to diagnose metric drops. | Model generated generic hypotheses without exact mathematical evidence. | Established starting point: LLMs cannot perform reliable multidimensional math over raw text. |
| **Iteration 1** | Equipped agent with Python tool (`slice_ecommerce_data`) to perform dynamic Pandas grouping. | Free tier APIs hit `429 RESOURCE_EXHAUSTED` and `503 UNAVAILABLE` under rapid tool firing. | Throttling with `time.sleep()` prevented RPM limits, but highlighted the need for stable paid-tier infrastructure. |
| **Iteration 2** | Agent began guessing non-existent dataset columns (`City`, `Browser`, `Payment_Gateway`). | Tool execution threw Pandas `KeyError` exceptions, causing the agent to stall. | Added strict schema guardrails directly into the system prompt, restricting slicing to valid dimensions. |
| **Final Solution** | Migrated to `gpt-4o-mini` with strict schema guardrails and dynamic command-line file routing. | Successfully diagnosed 10/10 scenarios, including multi-dimensional anomalies in under 2 seconds per file. | **Kept.** Robust tool calling combined with strict input constraints produces accurate analytical results. |

---

## 5. Agent Trajectories

Below are representative execution trajectories demonstrating how the agent reasons, invokes tools, receives data payloads, and synthesizes findings.

### Trajectory A: Single-Dimension Isolation (Scenario 01)

```text
USER PROMPT: Analyze the dataset located at 'data/scenario_01.csv'. Find the root cause of the conversion drop.

SYSTEM INSTRUCTION: Autonomous RCA agent reporting to CDAO. Restrict tools to allowed schema.

[STEP 1 - Tool Call]
Agent calls: slice_ecommerce_data(dimensions=['Pincode'])
Tool Output: Slices for pincodes showing baseline CR ~0.043

[STEP 2 - Tool Call]
Agent calls: slice_ecommerce_data(dimensions=['Region'])
Tool Output: Slices for regions showing normal conversion distribution

[STEP 3 - Tool Call]
Agent calls: slice_ecommerce_data(dimensions=['Category'])
Tool Output: Category CRs all hover between 0.040 and 0.046

[STEP 4 - Tool Call]
Agent calls: slice_ecommerce_data(dimensions=['Promo_Code'])
Tool Output:
Promo_Code  Sessions  Orders  Conversion_Rate
  DIWALI50    118200       0           0.0000
 WELCOME20     59819    2626           0.0439
    SAVE10     58410    2588           0.0443

[STEP 5 - Final Synthesis]
Agent recognizes 0.0000 CR with high session volume and halts tool calls.

FINAL EXECUTIVE BRIEF:
- OBSERVATION: Significant drop in overall conversion rate across the e-commerce platform.
- ROOT CAUSE: Segment with promo code "DIWALI50" resulted in zero orders.
- EVIDENCE: Promo code "DIWALI50" had 118,200 sessions and 0 orders (CR: 0.0000) vs "WELCOME20" with 2,626 orders (CR: 0.0439).
```

### Trajectory B: Cross-Dimensional Expansion (Scenario 09)

```text
USER PROMPT: Analyze the dataset located at 'data/scenario_09.csv'. Find the root cause of the conversion drop.

[STEP 1 to 3 - Single Dimension Sweeps]
Agent calls: slice_ecommerce_data(dimensions=['Pincode'])
Agent calls: slice_ecommerce_data(dimensions=['Region'])
Agent calls: slice_ecommerce_data(dimensions=['Category'])
Tool Output: FMCG_Groceries shows abnormally depressed CR (0.0080) compared to other categories (~0.045).

[STEP 4 to 7 - Multi-Dimensional Cross-Referencing]
Agent calls: slice_ecommerce_data(dimensions=['Category', 'Platform'])
Agent calls: slice_ecommerce_data(dimensions=['Category', 'Payment_Type'])
Agent calls: slice_ecommerce_data(dimensions=['Category', 'Promo_Code'])
Tool Output:
FMCG_Groceries shows 204 orders / 25,500 sessions on Android_v12, 408 / 51,000 on Android_v13, 340 / 42,500 on Web.

[STEP 8 - Final Synthesis]
Agent synthesizes cross-dimensional breakdown across all platforms.

FINAL EXECUTIVE BRIEF:
- OBSERVATION: Drop in overall platform conversion rate, concentrated in FMCG_Groceries.
- ROOT CAUSE: FMCG_Groceries category failure across all operating platforms and payment types.
- EVIDENCE: FMCG_Groceries conversion rate dropped to 0.008 across platforms (Android_v12: 204/25,500; Android_v13: 408/51,000; Web: 340/42,500).
```

---

## 6. Hot Take & Failure Modes
+ Primary Failure Mode: Unbounded Schema Hallucination. When agents are equipped with open-ended data slicing functions without explicit schema boundaries, they project external domain assumptions onto the dataset (e.g., attempting to group by Browser, City, or Device when those columns do not exist). This leads to KeyError loops and execution stalls.

+ The Hot Take: An agentic analysis workflow is only as dependable as its schema constraints. Equipping an LLM with powerful data execution tools without strict column and type guardrails leads to erratic tool loops. Restricting the agent's action space through deterministic schema parameters transforms an unpredictable model into a production-grade analytical engine.
