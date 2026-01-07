import os
import subprocess
import tempfile
from groq import Groq  # CHANGED: Import Groq instead of OpenAI
from dotenv import load_dotenv
from core.prompts import GENERATE_TEST_PROMPT, REFACTOR_CODE_PROMPT, FIX_CODE_PROMPT
from colorama import Fore, Style

load_dotenv()

# CHANGED: Initialize Groq Client
# Make sure your .env file has GROQ_API_KEY=gsk_...
client = Groq(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

class RefactoringAgent:
    # UPDATED LINE BELOW:
    def __init__(self, model="llama-3.3-70b-versatile"): 
        self.model = model

    def _call_llm(self, system_prompt, user_content):
        """Helper to call Groq API"""
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=0 
        )
        content = response.choices[0].message.content
        # Clean up markdown formatting
        content = content.replace("```python", "").replace("```", "").strip()
        return content

    def run_tests(self, code_str, test_str):
        """
        Saves code and tests to temp files and runs pytest.
        Returns: (success: bool, output: str)
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            # 1. Write the code file
            code_path = os.path.join(tmpdir, "main_module.py")
            with open(code_path, "w") as f:
                f.write(code_str)

            # 2. Write the test file
            test_path = os.path.join(tmpdir, "test_main.py")
            # Inject import to ensure test can see the main module
            final_test_str = "import sys\nimport os\nsys.path.append(os.getcwd())\nfrom main_module import *\n" + test_str
            with open(test_path, "w") as f:
                f.write(final_test_str)

            # 3. Run Pytest
            print(f"{Fore.CYAN}Running Tests...{Style.RESET_ALL}")
            result = subprocess.run(
                ["pytest", test_path],
                capture_output=True,
                text=True
            )
            
            return result.returncode == 0, result.stdout + result.stderr

    def process(self, legacy_code):
        print(f"{Fore.YELLOW}STEP 1: Generating Regression Tests...{Style.RESET_ALL}")
        test_code = self._call_llm(GENERATE_TEST_PROMPT, legacy_code)
        
        # Verify the tests actually pass on the OLD code first
        passed, output = self.run_tests(legacy_code, test_code)
        if not passed:
            print(f"{Fore.RED}CRITICAL: Generated tests fail on original code. Aborting.{Style.RESET_ALL}")
            print(output)
            return None

        print(f"{Fore.GREEN}Tests Verified against Legacy Code.{Style.RESET_ALL}")

        print(f"{Fore.YELLOW}STEP 2: Refactoring Code...{Style.RESET_ALL}")
        new_code = self._call_llm(REFACTOR_CODE_PROMPT, legacy_code)

        # Iterative Healing Loop
        max_retries = 3
        for attempt in range(max_retries):
            print(f"{Fore.YELLOW}STEP 3 (Attempt {attempt+1}): Verifying Refactor...{Style.RESET_ALL}")
            passed, output = self.run_tests(new_code, test_code)

            if passed:
                print(f"{Fore.GREEN}SUCCESS! Code refactored and verified.{Style.RESET_ALL}")
                return new_code
            else:
                print(f"{Fore.RED}Test Failed. Healing code...{Style.RESET_ALL}")
                error_context = f"Legacy Code:\n{legacy_code}\n\nRefactored Code:\n{new_code}\n\nError:\n{output}"
                new_code = self._call_llm(FIX_CODE_PROMPT.format(
                    legacy_code=legacy_code,
                    refactored_code=new_code,
                    error_message=output
                ), "")
        
        print(f"{Fore.RED}Failed to refactor successfully after {max_retries} retries.{Style.RESET_ALL}")
        return None

if __name__ == "__main__":
# Example "Bad" Code
    messy_code = """
def calc(a,b,op):
    if op == 'add': return a+b
    if op == 'sub': return a-b
    if op == 'mul': return a*b
    if op == 'div':
        if b==0: return "Error"
        return a/b
    # Implicitly returns None here if op is invalid
    """
    
    agent = RefactoringAgent()
    final_code = agent.process(messy_code)
    
    if final_code:
        print("\n=== FINAL REFACTORED CODE ===\n")
        print(final_code)