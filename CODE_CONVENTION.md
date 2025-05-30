# Artificial Intelligence Coding Conventions and Guidelines

### Objective:

We are adopting the concept of code ownership to enhance code quality and ensure responsibility across the team. To fully implement this, we must establish a robust and well-maintained codebase. The following rules are mandatory and must be followed when fixing or implementing code. These guidelines apply to both individual code changes and the entire file, ensuring consistency across the team.

---

## 1\. Code Sectioning for Readability

Given the complexity and scale of the platform, clear sectioning is crucial for readability and maintainability. Ensure the code is segmented into logical sections.

**Code Grouping Template:**

```
# *************** IMPORTS: PYTHON LIBRARIES ***************
import os
import sys
import pandas as pd
import numpy as np

# *************** IMPORTS: FRAMEWORK ***************
from langchain.tools import tool
from langchain.agents import AgentExecutor, create_openai_tools_agent

# *************** IMPORTS: MODELS *************** 
# Schema definitions or data model files essential to the module.
from models.llms import LLMModels

# *************** IMPORTS: TOOLS *************** 
# Utility tools or functions aiding operations.
from utils import data_loader, file_writer

# *************** IMPORTS: VALIDATORS *************** 
# Validation functions for input and output handling.
from validators import input_validator

# *************** IMPORTS: HELPERS *************** 
# Helper functions separated from the main logic for reuse and clarity.
from helpers import text_cleaner, result_formatter

# *************** CONFIGURATION AND ENVIRONMENT *************** 
# Environment-specific configurations or setup logic.
load_config(os.getenv('ENVIRONMENT'))

# *************** DATA PROCESSING *************** 
# ***************Data preparation, cleaning, or transformation prior to main operations.
def preprocess_data(raw_data):
    ...

# *************** MAIN *************** 
# The primary logic or entry point of the module.
if __name__ == "__main__":
    main_function()
```

---

## 2\. In-Code Documentation Rules

### a. Section Headers

Use consistent section headers:

```python
# ***************
```

### b. Function Documentation

Document functions using Python docstrings:

```python
#*************** <Simple explanation of a function>
def process_data(data: pd.DataFrame) -> pd.DataFrame:
    """
    <summary of the function>
    Args:
        text_input (str): <input data expectation>
        field_names (list): <field name expectation>
    Returns:
        dict[list] : <return expectation>
    """
    pass
```

### c. START and END Comments

Segment complex functions:

```
def analyze_data():
    # *************** START: Data Validation ***************
    if data.empty:
        raise ValueError("DataFrame is empty.")
    # *************** END: Data Validation ***************

    # *************** START: Data Processing ***************
    processed = process_data(data)
    # *************** END: Data Processing ***************
```

---

### d. Model-Specific Code Convention for OpenAI Integration

Clear and thorough documentation is essential, especially when handling third-party integrations like OpenAI’s API. Below are specific documentation practices to adopt when integrating OpenAI models:

```python
# *************** OPENAI API INTERACTIONS ***************
# Code responsible for interacting with OpenAI's models and processing the responses
```

**IMPORTANT NOTES**
When you are working in any AI code and notice that in-code documentation does not exist yet or not implemented as this guideline, you are responsible for updating the entire file with proper inline comments for each field. This ensures that our code base is fully documented and adheres to our standards.

---

## 3\. Naming Conventions

Follow these naming conventions to ensure consistency across the codebase. And please use meaningful names that represent the operation

* **Local Variables:** snake_case
* **Global Variables:** SCREAMING_SNACK_CASE
* **Functions:** snake_case
* **Modules:** snake_case
* **Classes:** PascalCase
* **Exceptions:** PascalCase
* **Decorators:** snake_case
* **Object:** camelCase

---

## 4\. Validation Rules

Validation is required for all inputs and outputs. Ensure that all incoming and outgoing data is properly validated to avoid errors and ensure data integrity.

* Always add validation for all inputs and outputs.
* Check if the request payload exists and if the format is correct.
* Check if the response payload exists and if the format is correct.
* Use try-except for error handling.
* Validation is important after generating an AI response.
* Ensure the type of data and required fields are generated correctly.




```python
def validate_request(url: str, course_id: str) -> bool:
    if not url or not is_url(url):
        raise ValueError("Invalid URL provided.")
    if not course_id:
        raise ValueError("Course ID is required.")
    return True
```

---

## 5\. Code Redundancy and Helper Functions

* Identify and eliminate code redundancy by creating helper functions for repeated logic.
* If the same logic is used multiple times, extract it into a helper function for reusability.
* If you face difficulties, you can always seek assistance, such as using tools like GPT for pointers.
* Apply the **Single Responsibility Principle (SRP)** to simplify functions.

```python
# helpers.py
def format_date(date_str: str) -> str:
    return datetime.strptime(date_str, "%Y-%m-%d").strftime("%d-%m-%Y")
```

---

## 6\. Error Handling

* Implement clear and meaningful error messages.
* Use custom exception classes when necessary.

```
class DataProcessingError(Exception):
    pass

def process_data(data):
    try:
        # Processing logic
        pass
    except Exception as e:
        raise DataProcessingError(f"Processing failed: {e}")
```

---

## 7\. SOLID Principles Implementation

* **Single Responsibility Principle**: Each module/class should have one purpose.
* **Open/Closed Principle**: Code should be open for extension but closed for modification.
* **Liskov Substitution Principle**: Subclasses must be substitutable for their base classes.
* **Interface Segregation Principle**: Avoid forcing classes to implement unused methods.
* **Dependency Inversion Principle**: Depend on abstractions, not concrete implementations.

```
class DataLoader(ABC):
    @abstractmethod
    def load(self):
        pass

class CSVLoader(DataLoader):
    def load(self):
        # Load CSV data
        pass
```

---

## 8\. Fail Fast Principle

* Detect issues early with input validation and assertions.
* Avoid silent failures.

```python
def fetch_data(api_url: str) -> dict:
    assert api_url.startswith("http"), "Invalid URL. Must start with http or https."
    response = requests.get(api_url)
    response.raise_for_status()
    return response.json()
```

---

## 9\. Code Review Protocols

When conducting code reviews, reviewers must enforce the rules outlined above. These conventions should be adhered to starting from the **first review** to prevent production from being affected by code inconsistencies or errors.

### Proof for Pull Requests (PR):

Developers must provide proof that the rules have been followed before requesting a PR review. This proof should be in the form of:

* A checklist indicating compliance with the rules.
* A video demonstrating the changes and adherence to the guidelines.

---

## 10\. Urgent Fixes

In the case of urgent or issues need to resolved ASAP, you may push the code fix first but must ensure compliance with the rules outlined above on the **same day**. Clearance from **Santika**, **Bayu**, or higher authority is required for urgent pushes.

---

## 11\. Distinction Between Helper Functions and Utilities

When developing or refactoring code, it is essential to differentiate between **Helper Functions** and **Utilities**. Each serves a unique purpose and should be used in the correct context for maintainability and clarity.

| **Aspect** | **Helper Functions** | **Utilities** |
| --- | --- | --- |
| **Definition** | Small, specialized functions for specific tasks | General-purpose functions used for various contexts |
| **Scope** | Module-specific | Project-wide |
| **Examples** | Format dates for one feature | Logging, data validation |
| **Organization** | In the same file/module | In `/utils/` or `/validators/` folder |

### Guidelines for Using Helper Functions:

* Helper functions should be created when dealing with module-specific tasks or repetitive operations confined to a specific context.
* These functions should remain within the same module or file they are used in to maintain clarity and simplicity.

### Guidelines for Using Utilities:

* Utilities are general functions that apply to many parts of the application.
* They should be placed in a centralized utility file, making them easily reusable and importable across different modules.
* Use utilities for operations that are common across different modules, such as validation, logging, or string manipulation.

---

By following these conventions, we ensure that our codebase remains clean, maintainable, and scalable, which benefits both individual developers and the team as a whole. These guidelines foster a strong sense of code ownership and contribute to the overall quality of the platform.