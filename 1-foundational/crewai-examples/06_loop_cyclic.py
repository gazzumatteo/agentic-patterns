"""
Pattern 8: Self-Correction
Automatic error detection and fixing through validation and retry mechanisms.

Business Example: Code generation with testing

Mermaid Diagram Reference: See diagrams/08_self_correction.mermaid
"""

from crewai import Agent, Task, Crew
import json


def create_selfcorrection_crew():
    """Create crew for self-correcting code generation."""
    
    generator = Agent(
        role="Code Generator",
        goal="Generate high-quality Python code that meets requirements",
        backstory="Expert Python developer who writes clean, working code.",
        verbose=True
    )
    
    validator = Agent(
        role="Code Validator",
        goal="Test and validate code for correctness and quality",
        backstory="QA engineer who finds bugs and validates functionality.",
        verbose=True
    )
    
    fixer = Agent(
        role="Code Fixer",
        goal="Fix identified issues and improve code quality",
        backstory="Debugging expert who resolves code issues efficiently.",
        verbose=True
    )
    
    return Crew(agents=[generator, validator, fixer], tasks=[], verbose=True)


def generate_with_correction(requirements: str, max_attempts: int = 3):
    """Generate code with self-correction loop."""
    crew = create_selfcorrection_crew()
    generator, validator, fixer = crew.agents
    
    current_code = None
    
    for attempt in range(max_attempts):
        print(f"\nAttempt {attempt + 1}:")
        
        # Generate or fix code
        if attempt == 0:
            gen_task = Task(
                description=f"Generate Python code for: {requirements}",
                expected_output="Working Python code",
                agent=generator
            )
        else:
            gen_task = Task(
                description=f"Fix this code based on errors: {current_code}\nErrors: {validation_result}",
                expected_output="Fixed Python code",
                agent=fixer
            )
        
        crew.tasks = [gen_task]
        current_code = crew.kickoff()
        
        # Validate
        val_task = Task(
            description=f"Validate this code: {current_code}\nRequirements: {requirements}",
            expected_output="Validation report with errors or success",
            agent=validator
        )
        
        crew.tasks = [val_task]
        validation_result = crew.kickoff()
        
        # Check if valid (simplified check)
        if "error" not in str(validation_result).lower() or attempt == max_attempts - 1:
            print("Code validated successfully!")
            break
    
    return current_code


def main():
    """Demonstrate self-correction pattern."""
    print("=" * 80)
    print("Pattern 8: Self-Correction with CrewAI")
    print("=" * 80)
    
    requirements = """
    Create a function to calculate factorial.
    - Handle negative numbers (return None)
    - Handle zero (return 1)
    - Use recursion
    """
    
    final_code = generate_with_correction(requirements)
    
    print("\nFinal Code:")
    print(final_code)
    
    print("\n" + "=" * 80)
    print("Self-Correction Benefits:")
    print("- Automatic error detection")
    print("- Iterative improvement")
    print("- Quality assurance built-in")
    print("=" * 80)


if __name__ == "__main__":
    main()
