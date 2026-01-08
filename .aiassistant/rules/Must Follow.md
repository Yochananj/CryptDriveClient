---
apply: always
---

1. High-Relevance Context Gathering:
   Analyze the prompt to identify and read the primary file, its imports, and any other files that may be relevant to the prompt.

2. Surgical Code Modifications:
   Unless requested to write a full feature, provide targeted diffs or logical blocks. Instead of a strict three-line limit, ensure snippets represent a single logical unit (e.g., one complete function, one conditional block, or one set of imports). This maintains readability while preventing "code dumps."

3. Precision Mapping:
   Always identify code locations using file names and line numbers (or unique function/class identifiers). Ensure the user knows exactly where the change belongs without needing to search.

4. Root-Cause Rationalization (The "Layered Why"):
   Instead of a rigid "Why? Why? Why?" loop, use a Logic Chain:
    
   - Observation: State the behavior.
    
   - Mechanism: Explain the technical reason for this behavior.
    
   - Resolution: Explain why the proposed fix addresses the mechanism.
    
   - Avoid philosophy; focus on technical causality.

5. Evidence-Based Diagnosis:
   Do not assert the cause of an error without citing direct evidence (e.g., a specific line of code, a stack trace, or a log entry). If the cause is not explicitly visible in the provided context, categorize the response as a hypothesis rather than a fact.

6. Explicit Uncertainty Labeling:
   Continue to prefix non-evidenced statements with "SPECULATION:". Additionally, if multiple possibilities exist, rank them by Probability (e.g., "Most Likely," "Potential Alternative").