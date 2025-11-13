Great! As a senior developer, I understand the need for robust, well-structured, and testable code that directly addresses the user stories and their acceptance criteria. I'll implement a backend logic simulation using Python classes, focusing on data validation and state management, as this forms the core business logic.

I'll create:
1.  A `BankAccountApplication` class to manage the overall application state and flow.
2.  Data models (`PersonalDetailsData`, `DocumentData`) to encapsulate input for each step.
3.  Validation logic to enforce mandatory fields, data formats, file types, and file sizes.
4.  A simulation of "secure storage" and "navigation."

```python
import re
from datetime import datetime, date

# --- Constants and Configurations ---
MAX_FILE_SIZE_MB = 5
ACCEPTED_DOCUMENT_TYPES = ['image/jpeg', 'image/png', 'application/pdf']

# --- Helper Functions and Classes (for validation) ---

class ValidationResult:
    """A class to encapsulate validation outcomes."""
    def __init__(self, is_valid: bool = True, errors: dict = None):
        self.is_valid = is_valid
        self.errors = errors if errors is not None else {}

    def add_error(self, field: str, message: str):
        """Adds an error message for a specific field."""
        if field not in self.errors:
            self.errors[field] = []
        self.errors[field].append(message)
        self.is_valid = False

    def __bool__(self):
        return self.is_valid

    def __repr__(self):
        return f"ValidationResult(is_valid={self.is_valid}, errors={self.errors})"

class Validator:
    """Centralized validation utility."""

    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Checks for a basic email format."""
        # A more robust regex might be needed for production
        return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

    @staticmethod
    def is_future_date(dt_str: str, date_format: str = "%Y-%m-%d") -> bool:
        """Checks if a given date string represents a future date."""
        try:
            input_date = datetime.strptime(dt_str, date_format).date()
            return input_date > date.today()
        except ValueError:
            return True # Treat invalid format as future/invalid for safety

    @staticmethod
    def is_valid_phone(phone_number: str) -> bool:
        """Checks for a basic phone number format (digits, optional +, spaces, hyphens)."""
        # This is a very permissive regex. A real app would need country-specific validation.
        return re.match(r"^\+?[\d\s-]{7,15}$", phone_number) is not None

# --- Data Models ---

class PersonalDetailsData:
    """
    Represents the personal details submitted by the potential customer.
    Includes validation logic for its fields.
    """
    def __init__(self, full_name: str, date_of_birth: str, residential_address: str, email: str, phone_number: str):
        self.full_name = full_name
        self.date_of_birth = date_of_birth
        self.residential_address = residential_address
        self.email = email
        self.phone_number = phone_number

    def validate(self) -> ValidationResult:
        """Validates all personal details fields according to business rules."""
        result = ValidationResult()

        # Mandatory fields
        if not self.full_name:
            result.add_error("full_name", "Full Name is mandatory.")
        if not self.date_of_birth:
            result.add_error("date_of_birth", "Date of Birth is mandatory.")
        if not self.residential_address:
            result.add_error("residential_address", "Residential Address is mandatory.")
        if not self.email:
            result.add_error("email", "Email is mandatory.")
        if not self.phone_number:
            result.add_error("phone_number", "Phone Number is mandatory.")

        # Format validations (only if field is not already missing)
        if self.date_of_birth and not result.errors.get("date_of_birth"):
            try:
                # Assuming YYYY-MM-DD format for input
                datetime.strptime(self.date_of_birth, "%Y-%m-%d")
                if Validator.is_future_date(self.date_of_birth):
                    result.add_error("date_of_birth", "Date of birth cannot be in the future.")
            except ValueError:
                result.add_error("date_of_birth", "Invalid date of birth format. Please use YYYY-MM-DD.")

        if self.email and not result.errors.get("email"):
            if not Validator.is_valid_email(self.email):
                result.add_error("email", "Please enter a valid email address.")

        if self.phone_number and not result.errors.get("phone_number"):
            if not Validator.is_valid_phone(self.phone_number):
                result.add_error("phone_number", "Please enter a valid phone number.")

        return result

    def to_dict(self):
        return {
            "full_name": self.full_name,
            "date_of_birth": self.date_of_birth,
            "residential_address": self.residential_address,
            "email": self.email,
            "phone_number": self.phone_number,
        }

class DocumentData:
    """
    Represents an uploaded document with its details.
    """
    def __init__(self, filename: str, content_type: str, size_bytes: int, content=None):
        self.filename = filename
        self.content_type = content_type # e.g., 'image/jpeg', 'application/pdf'
        self.size_bytes = size_bytes
        self.content = content # In a real app, this would be a path or a stream reference

    def validate(self, field_name: str) -> ValidationResult:
        """Validates a single document against type and size limits."""
        result = ValidationResult()

        if self.content_type not in ACCEPTED_DOCUMENT_TYPES:
            result.add_error(field_name,
                             f"File type '{self.content_type}' is not allowed. Accepted types: {', '.join(t.split('/')[1] for t in ACCEPTED_DOCUMENT_TYPES)}.")

        if self.size_bytes > (MAX_FILE_SIZE_MB * 1024 * 1024):
            result.add_error(field_name,
                             f"File exceeds the maximum size limit of {MAX_FILE_SIZE_MB}MB.")
        return result

    def to_dict(self):
        return {
            "filename": self.filename,
            "content_type": self.content_type,
            "size_bytes": self.size_bytes,
        }

# --- Main Application Logic ---

class BankAccountApplication:
    """
    Manages the state and business logic for the bank account application process.
    """
    def __init__(self):
        self._current_step = "personal_details"
        self._personal_details_data: PersonalDetailsData = None
        self._primary_id_document: DocumentData = None
        self._proof_of_address_document: DocumentData = None

        # Simulate secure storage for processing later
        self._secure_storage = {
            "personal_details": {},
            "documents": {}
        }
        print("Bank account application initialized.")

    @property
    def current_step(self) -> str:
        return self._current_step

    @property
    def application_data(self) -> dict:
        return {
            "current_step": self.current_step,
            "personal_details": self._personal_details_data.to_dict() if self._personal_details_data else {},
            "primary_id": self._primary_id_document.to_dict() if self._primary_id_document else {},
            "proof_of_address": self._proof_of_address_document.to_dict() if self._proof_of_address_document else {},
            "secure_storage_snapshot": self._secure_storage # For demonstration
        }

    def _securely_store_data(self, key: str, data: dict):
        """Simulates secure storage of data."""
        # In a real application, this would involve database writes, encryption, etc.
        self._secure_storage[key] = data
        print(f"DEBUG: Data for '{key}' securely stored: {data}")

    def submit_personal_details(self, full_name: str, date_of_birth: str, residential_address: str, email: str, phone_number: str) -> dict:
        """
        Processes the submission of personal details.
        Returns a dictionary indicating success/failure and relevant messages/data.
        """
        if self._current_step != "personal_details":
            return {"success": False, "errors": {"application_flow": f"Currently on step: {self._current_step}. Cannot submit personal details."}}

        print(f"\nAttempting to submit personal details...")
        details = PersonalDetailsData(full_name, date_of_birth, residential_address, email, phone_number)
        validation_result = details.validate()

        if validation_result.is_valid:
            self._personal_details_data = details
            self._securely_store_data("personal_details", details.to_dict())
            self._current_step = "id_verification"
            print("INFO: Personal details successfully submitted.")
            return {
                "success": True,
                "message": "Personal details successfully submitted.",
                "next_step": self._current_step
            }
        else:
            print("ERROR: Personal details validation failed.")
            return {
                "success": False,
                "errors": validation_result.errors,
                "current_step": self._current_step # Remain on this page
            }

    def upload_identity_documents(self, primary_id_file_data: dict, proof_of_address_file_data: dict) -> dict:
        """
        Processes the upload of identity documents.
        `primary_id_file_data` and `proof_of_address_file_data` should be dictionaries like:
        {'filename': 'passport.jpg', 'content_type': 'image/jpeg', 'size_bytes': 1234567}
        """
        if self._current_step != "id_verification":
            return {"success": False, "errors": {"application_flow": f"Currently on step: {self._current_step}. Cannot upload documents."}}
        if not self._personal_details_data:
             return {"success": False, "errors": {"application_flow": "Personal details must be completed first."}}


        print(f"\nAttempting to upload identity documents...")
        primary_id = DocumentData(**primary_id_file_data)
        proof_of_address = DocumentData(**proof_of_address_file_data)

        combined_validation_result = ValidationResult()

        primary_id_validation = primary_id.validate("primary_id_document")
        if not primary_id_validation.is_valid:
            combined_validation_result.errors.update(primary_id_validation.errors)
            combined_validation_result.is_valid = False

        proof_of_address_validation = proof_of_address.validate("proof_of_address_document")
        if not proof_of_address_validation.is_valid:
            combined_validation_result.errors.update(proof_of_address_validation.errors)
            combined_validation_result.is_valid = False

        if combined_validation_result.is_valid:
            self._primary_id_document = primary_id
            self._proof_of_address_document = proof_of_address
            self._securely_store_data("documents", {
                "primary_id": primary_id.to_dict(),
                "proof_of_address": proof_of_address.to_dict()
            })
            self._current_step = "review_and_submit"
            print("INFO: Identity documents successfully uploaded.")
            return {
                "success": True,
                "message": "Documents uploaded successfully. Proceeding to review.",
                "next_step": self._current_step
            }
        else:
            print("ERROR: Document upload validation failed.")
            return {
                "success": False,
                "errors": combined_validation_result.errors,
                "current_step": self._current_step # Remain on this page
            }


# --- Simulation of User Interactions / Gherkin Scenarios ---

def run_scenario(scenario_name: str, app: BankAccountApplication, func_call, expected_output_check):
    print(f"\n--- Running Scenario: {scenario_name} ---")
    response = func_call()
    assert expected_output_check(response), f"Assertion failed for '{scenario_name}'. Response: {response}"
    print(f"--- Scenario '{scenario_name}' PASSED ---\n")
    return response

if __name__ == "__main__":
    app = BankAccountApplication()

    # User Story 1: Submit Personal Details

    # Scenario: Successful submission of all mandatory personal details
    run_scenario(
        "US1: Successful submission of all mandatory personal details",
        app,
        lambda: app.submit_personal_details(
            full_name="Alice Wonderland",
            date_of_birth="1990-01-15",
            residential_address="123 Rabbit Hole, Wonderland, WN1 2AB",
            email="alice@wonderland.com",
            phone_number="+447123456789"
        ),
        lambda res: res["success"] and res["next_step"] == "id_verification"
    )
    print(f"Current Application Step: {app.current_step}")
    assert app.current_step == "id_verification"


    # Re-initialize app for independent scenario testing (or design scenarios to follow each other)
    app_us1_missing = BankAccountApplication()

    # Scenario: Attempt to submit with missing mandatory fields
    run_scenario(
        "US1: Attempt to submit with missing mandatory fields",
        app_us1_missing,
        lambda: app_us1_missing.submit_personal_details(
            full_name="Bob The Builder",
            date_of_birth="1985-05-20",
            residential_address="", # Missing Residential Address
            email="bob@builder.com",
            phone_number="+15551234567"
        ),
        lambda res: not res["success"] and "residential_address" in res["errors"] and res["current_step"] == "personal_details"
    )
    assert app_us1_missing.current_step == "personal_details"


    app_us1_invalid = BankAccountApplication()

    # Scenario: Attempt to submit with invalid data format
    run_scenario(
        "US1: Attempt to submit with invalid data format",
        app_us1_invalid,
        lambda: app_us1_invalid.submit_personal_details(
            full_name="Charlie Chaplin",
            date_of_birth="2050-12-25", # Future date
            residential_address="456 Silent Film St, Hollywood, CA 90028",
            email="charlie.com", # Invalid email format
            phone_number="not-a-phone" # Invalid phone format
        ),
        lambda res: (not res["success"] and
                     "date_of_birth" in res["errors"] and
                     "email" in res["errors"] and
                     "phone_number" in res["errors"] and
                     "Date of birth cannot be in the future." in res["errors"]["date_of_birth"] and
                     "Please enter a valid email address." in res["errors"]["email"] and
                     "Please enter a valid phone number." in res["errors"]["phone_number"] and
                     res["current_step"] == "personal_details")
    )
    assert app_us1_invalid.current_step == "personal_details"


    # User Story 2: Upload Identity Documents

    # Scenario: Successful upload of required identity documents
    # First, complete personal details to get to the correct step
    app_us2_success = BankAccountApplication()
    app_us2_success.submit_personal_details(
        full_name="Diana Prince",
        date_of_birth="1980-08-08",
        residential_address="Themyscira Embassy, Washington D.C.",
        email="diana@amazon.com",
        phone_number="+12025550100"
    )
    assert app_us2_success.current_step == "id_verification"

    run_scenario(
        "US2: Successful upload of required identity documents",
        app_us2_success,
        lambda: app_us2_success.upload_identity_documents(
            primary_id_file_data={'filename': 'passport.jpg', 'content_type': 'image/jpeg', 'size_bytes': 1 * 1024 * 1024}, # 1MB
            proof_of_address_file_data={'filename': 'utility_bill.pdf', 'content_type': 'application/pdf', 'size_bytes': 500 * 1024} # 0.5MB
        ),
        lambda res: res["success"] and res["next_step"] == "review_and_submit"
    )
    print(f"Current Application Step: {app_us2_success.current_step}")
    assert app_us2_success.current_step == "review_and_submit"

    # Scenario: Attempt to upload an unsupported file type
    app_us2_unsupported = BankAccountApplication()
    app_us2_unsupported.submit_personal_details( # Complete first step
        full_name="Eve Harrington", date_of_birth="1975-03-10",
        residential_address="Backstage Alley, New York, NY",
        email="eve@theatre.com", phone_number="+12125550200"
    )
    assert app_us2_unsupported.current_step == "id_verification"

    run_scenario(
        "US2: Attempt to upload an unsupported file type",
        app_us2_unsupported,
        lambda: app_us2_unsupported.upload_identity_documents(
            primary_id_file_data={'filename': 'passport.docx', 'content_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'size_bytes': 1 * 1024 * 1024}, # DOCX file
            proof_of_address_file_data={'filename': 'utility_bill.pdf', 'content_type': 'application/pdf', 'size_bytes': 500 * 1024}
        ),
        lambda res: (not res["success"] and
                     "primary_id_document" in res["errors"] and
                     "File type 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' is not allowed" in res["errors"]["primary_id_document"][0] and
                     res["current_step"] == "id_verification")
    )
    assert app_us2_unsupported.current_step == "id_verification" # Should remain on this step

    # Scenario: Attempt to upload a file exceeding the size limit
    app_us2_oversized = BankAccountApplication()
    app_us2_oversized.submit_personal_details( # Complete first step
        full_name="Frank Underwood", date_of_birth="1960-11-05",
        residential_address="1600 Pennsylvania Ave, Washington D.C.",
        email="frank@whitehouse.com", phone_number="+12024561414"
    )
    assert app_us2_oversized.current_step == "id_verification"

    run_scenario(
        "US2: Attempt to upload a file exceeding the size limit",
        app_us2_oversized,
        lambda: app_us2_oversized.upload_identity_documents(
            primary_id_file_data={'filename': 'oversized_passport.jpg', 'content_type': 'image/jpeg', 'size_bytes': 6 * 1024 * 1024}, # 6MB
            proof_of_address_file_data={'filename': 'utility_bill.pdf', 'content_type': 'application/pdf', 'size_bytes': 500 * 1024}
        ),
        lambda res: (not res["success"] and
                     "primary_id_document" in res["errors"] and
                     f"File exceeds the maximum size limit of {MAX_FILE_SIZE_MB}MB." in res["errors"]["primary_id_document"][0] and
                     res["current_step"] == "id_verification")
    )
    assert app_us2_oversized.current_step == "id_verification" # Should remain on this step

    print("\nAll implemented scenarios have passed!")
```

### Explanation and Design Choices:

1.  **`BankAccountApplication` Class:**
    *   This is the central orchestrator, simulating the backend state of a user's application.
    *   `_current_step`: Tracks the user's progress through the application (`"personal_details"`, `"id_verification"`, `"review_and_submit"`).
    *   `_personal_details_data`, `_primary_id_document`, `_proof_of_address_document`: Store the validated data for each step.
    *   `_secure_storage`: A dictionary simulating a secure data store. In a real application, this would interact with a database, cloud storage, or an encryption service. The `_securely_store_data` method is a placeholder.
    *   Methods like `submit_personal_details` and `upload_identity_documents` encapsulate the business logic for each user story, including pre-condition checks (e.g., `_current_step`), validation, data storage, and state transitions.

2.  **`PersonalDetailsData` Class:**
    *   A simple data class to hold personal information.
    *   `validate()` method: Implements all the validation rules for personal details:
        *   **Mandatory fields:** Checks if fields are empty.
        *   **Date of Birth:** Verifies format (YYYY-MM-DD assumed) and ensures it's not in the future.
        *   **Email:** Uses a basic regex for format validation.
        *   **Phone Number:** Uses a basic regex for format validation.
    *   Returns a `ValidationResult` object, which makes it easy to collect multiple errors.

3.  **`DocumentData` Class:**
    *   A simple data class to hold file information (filename, content type, size).
    *   `validate()` method: Checks against configured `ACCEPTED_DOCUMENT_TYPES` and `MAX_FILE_SIZE_MB`.
    *   `content` field is a placeholder; in a real web app, this might be a file stream or a temporary file path.

4.  **`ValidationResult` and `Validator` Classes:**
    *   **`ValidationResult`**: A dedicated class to aggregate validation errors. It allows adding multiple error messages per field and provides a `is_valid` flag for convenience. Its `__bool__` method makes it usable directly in `if` statements.
    *   **`Validator`**: A static utility class for common, reusable validation functions (e.g., `is_valid_email`, `is_future_date`, `is_valid_phone`). This keeps the validation logic modular and potentially reusable across different parts of a larger system.

5.  **Simulation of Scenarios (`if __name__ == "__main__":`)**
    *   Each Gherkin scenario is translated into a series of Python calls to the `BankAccountApplication` methods.
    *   The `run_scenario` helper function prints clear delimiters for each test and uses `assert` statements to verify that the application's response matches the acceptance criteria (e.g., `success: True`, correct `next_step`, specific error messages).
    *   For scenarios requiring an initial state (like "Upload Identity Documents" requiring "Personal Details" to be complete), previous steps are simulated first.
    *   New `BankAccountApplication` instances are created for independent scenario testing to ensure no state bleed between tests, which is good practice.

This code provides a solid backend foundation for the user stories, focusing on the core business logic, data modeling, and validation as specified by the acceptance criteria. It's designed to be modular and testable, reflecting senior developer best practices.