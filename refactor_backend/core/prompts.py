# prompts.py

# prompts.py

GENERATE_TEST_PROMPT = """
You are an Expert QA Engineer. I will give you a piece of legacy Python code.
Your goal is to write a comprehensive `pytest` unit test suite that captures the CURRENT behavior of this code.

CRITICAL RULES:
1. The code you are testing will be saved in a file named `main_module.py`.
2. You MUST use this exact import line: `from main_module import *`
3. Do NOT invent new module names like 'your_module' or 'legacy_code'.
4. If the code implicitly returns `None`, assert `None`. Do not assume it raises errors.

Legacy Code:
{code}

Output ONLY the Python code for the tests.
"""

REFACTOR_CODE_PROMPT = """
You are a Senior Python Architect. Refactor the following legacy code to be modern, clean, and efficient.
Follow these rules:
1. Add Type Hints.
2. Follow PEP-8 styling.
3. Improve variable names.
4. DO NOT change the logic or behavior. The output must be identical to the original.

Legacy Code:
{code}

Output ONLY the Python code. Do not use markdown blocks.
"""

FIX_CODE_PROMPT = """
You are a Debugging Expert. You refactored some code, but the regression tests failed.
You need to fix the refactored code so it passes the tests.

Original Legacy Code:
{legacy_code}

Your Refactored Code (that failed):
{refactored_code}

The Test Failure Output:
{error_message}

Return the FIXED refactored code only. Do not explain.
"""