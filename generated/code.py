Here's the Python code implementing the two user stories, adhering to the Gherkin acceptance criteria.

This solution simulates the backend logic of a hospital patient registration system. It uses in-memory dictionaries to store patient data and generates unique IDs. The functions return dictionaries indicating `status` (success/error), `message`, and relevant `data` (like patient IDs, error details, or retained form data), mimicking an API response that a frontend application would consume.

```python
import datetime
import uuid

# --- Helper for generating unique Patient IDs ---
class PatientIdGenerator:
    """
    Generates unique patient IDs in the format P-YYYY-NNNN,
    resetting the sequence number annually.
    """
    def __init__(self):
        self._counter = 0
        self._last_year = datetime.date.today().year

    def generate_id(self):
        current_year = datetime.date.today().year
        if current_year != self._last_year:
            self._counter = 0  # Reset counter for a new year
            self._last_year = current_year

        self._counter += 1
        return f"P-{current_year}-{self._counter:04d}"

# --- HospitalRegistry System Class ---
class HospitalRegistry:
    """
    Manages patient registration and emergency contact information.
    Simulates a backend service with in-memory storage.
    """
    def __init__(self):
        self.patients = {}  # Stores patient records, keyed by patient_id
        self._id_generator = PatientIdGenerator()

    # --- Private Helper: Validate Patient Registration Details ---
    def _validate_patient_details(self, details: dict) -> dict:
        """
        Validates the input dictionary for new patient registration.
        Returns a dictionary of errors, or an empty dictionary if valid.
        """
        errors = {}
        required_fields = {
            "first_name": "First Name",
            "last_name": "Last Name",
            "date_of_birth": "Date of Birth",
            "gender": "Gender",
            "phone_number": "Phone Number",
            "address_line_1": "Address Line 1",
            "city": "City",
            "state": "State",
            "zip_code": "Zip Code",
            "admission_date": "Admission Date",
            "chief_complaint": "Chief Complaint"
        }

        for field, display_name in required_fields.items():
            if not details.get(field):
                errors[field] = f"{display_name} is required"

        # Specific date format validation (YYYY-MM-DD)
        date_fields = {"date_of_birth": "Date of Birth", "admission_date": "Admission Date"}
        for field, display_name in date_fields.items():
            date_str = details.get(field)
            if date_str and field not in errors: # Only validate format if field is present and not already marked as missing
                try:
                    datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                except ValueError:
                    errors[field] = f"{display_name} must be in YYYY-MM-DD format"
        
        # Simple gender validation (if provided)
        gender = details.get("gender")
        if gender and gender.lower() not in ["male", "female", "other", "prefer not to say"] and "gender" not in errors:
            errors["gender"] = "Invalid gender. Must be Male, Female, Other, or Prefer not to say."

        return errors

    # --- User Story 1: Register New Patient ---
    def register_new_patient(self, details: dict) -> dict:
        """
        Registers a new patient with their essential demographic and contact information.
        Returns a dictionary with status, message, and either patient_id/patient_data or errors.
        """
        validation_errors = self._validate_patient_details(details)

        if validation_errors:
            return {
                "status": "error",
                "message": "Failed to register patient due to missing or invalid information.",
                "errors": validation_errors,
                "data": details # Return the original data for form re-population
            }

        patient_id = self._id_generator.generate_id()
        new_patient = {
            "patient_id": patient_id,
            "first_name": details["first_name"],
            "last_name": details["last_name"],
            "date_of_birth": details["date_of_birth"],
            "gender": details["gender"],
            "phone_number": details["phone_number"],
            "address_line_1": details["address_line_1"],
            "city": details["city"],
            "state": details["state"],
            "zip_code": details["zip_code"],
            "admission_date": details["admission_date"],
            "chief_complaint": details["chief_complaint"],
            "emergency_contacts": [] # Initialize with an empty list for contacts
        }

        self.patients[patient_id] = new_patient
        full_name = f"{new_patient['first_name']} {new_patient['last_name']}"

        return {
            "status": "success",
            "message": f"Patient {full_name} registered successfully with ID {patient_id}",
            "patient_id": patient_id,
            "patient_data": new_patient,
            "clear_form": True # Signal for UI to clear fields
        }

    # --- Private Helper: Validate Emergency Contact Details ---
    def _validate_emergency_contact_details(self, details: dict) -> dict:
        """
        Validates the input dictionary for emergency contact details.
        Returns a dictionary of errors, or an empty dictionary if valid.
        """
        errors = {}
        required_fields = {
            "contact_name": "Contact Name",
            "relationship": "Relationship",
            "phone_number": "Phone Number"
        }

        for field, display_name in required_fields.items():
            if not details.get(field):
                errors[field] = f"{display_name} is required"
        
        # Basic email format validation (optional field, so only if provided)
        email = details.get("email_address")
        if email and "@" not in email and "email_address" not in errors:
            errors["email_address"] = "Invalid email address format"

        return errors

    # --- User Story 2: Add Patient Emergency Contact ---
    def add_emergency_contact(self, patient_id: str, contact_details: dict) -> dict:
        """
        Records emergency contact information for a registered patient.
        Returns a dictionary with status, message, and either updated patient data or errors.
        """
        if patient_id not in self.patients:
            return {
                "status": "error",
                "message": f"Patient with ID {patient_id} not found. Cannot add emergency contact.",
                "errors": {"patient_id": "Patient not found"},
                "data": contact_details
            }

        validation_errors = self._validate_emergency_contact_details(contact_details)

        if validation_errors:
            return {
                "status": "error",
                "message": "Failed to add emergency contact due to missing or invalid information.",
                "errors": validation_errors,
                "data": contact_details # Return the original data for form re-population
            }

        patient = self.patients[patient_id]
        new_contact = {
            "contact_id": str(uuid.uuid4()), # Unique ID for the contact itself
            "patient_id": patient_id,
            "contact_name": contact_details["contact_name"],
            "relationship": contact_details["relationship"],
            "phone_number": contact_details["phone_number"],
            "email_address": contact_details.get("email_address", "") # Optional field
        }

        patient["emergency_contacts"].append(new_contact)
        
        patient_full_name = f"{patient['first_name']} {patient['last_name']}"

        return {
            "status": "success",
            "message": f"Emergency contact for {patient_full_name} ({patient_id}) added successfully.",
            "patient_id": patient_id,
            "contact_data": new_contact,
            "patient_data_with_contacts": patient # For UI to update the list of contacts
        }

    # --- Public Helper: Retrieve Patient Data (useful for testing and other features) ---
    def get_patient(self, patient_id: str) -> dict or None:
        """Retrieves a patient's full record by their ID."""
        return self.patients.get(patient_id)

# --- Simulation of User Interaction and Testing (Equivalent to running automated tests) ---
if __name__ == "__main__":
    registry = HospitalRegistry()
    print("--- Simulating User Stories ---")

    # --- User Story 1: Register New Patient - Core Demographics ---
    print("\n--- Scenario: Successful New Patient Registration ---")
    patient_details_full = {
        "first_name": "John",
        "last_name": "Doe",
        "date_of_birth": "1990-05-15",
        "gender": "Male",
        "phone_number": "555-123-4567",
        "address_line_1": "123 Main St",
        "city": "Anytown",
        "state": "NY",
        "zip_code": "12345",
        "admission_date": "2023-10-26",
        "chief_complaint": "Fever and cough"
    }
    print(f"  Attempting to register: {patient_details_full['first_name']} {patient_details_full['last_name']}")
    result_success = registry.register_new_patient(patient_details_full)

    # Validate results based on Acceptance Criteria
    assert result_success["status"] == "success"
    initial_patient_id = result_success["patient_id"]
    print(f"  Result: {result_success['message']}")
    print(f"  Generated Patient ID: {initial_patient_id}")
    assert initial_patient_id.startswith(f"P-{datetime.date.today().year}-")

    saved_patient = registry.get_patient(initial_patient_id)
    assert saved_patient is not None
    print(f"  Patient data saved to system. Full name: {saved_patient['first_name']} {saved_patient['last_name']}")
    assert result_success["clear_form"] is True
    print("  Form fields should clear (UI signal received).")
    print("  Scenario PASSED: Successful New Patient Registration")

    print("\n--- Scenario: Attempt to Register Patient with Missing Required Information ---")
    patient_details_missing = {
        "first_name": "Jane",
        "last_name": "Smith",
        # "date_of_birth": deliberately missing
        "gender": "Female",
        "phone_number": "555-000-1111",
        "address_line_1": "456 Oak Ave",
        "city": "Othertown",
        "state": "CA",
        "zip_code": "98765",
        "admission_date": "2023-10-27",
        "chief_complaint": "Headache"
    }
    print(f"  Attempting to register with missing DOB for: {patient_details_missing['first_name']} {patient_details_missing['last_name']}")
    result_missing = registry.register_new_patient(patient_details_missing)

    # Validate results based on Acceptance Criteria
    assert result_missing["status"] == "error"
    print(f"  Result: {result_missing['message']}")
    assert "date_of_birth" in result_missing["errors"]
    print(f"  Error message: '{result_missing['errors']['date_of_birth']}'")
    assert result_missing["errors"]["date_of_birth"] == "Date of Birth is required"
    
    assert registry.get_patient("P-9999-9999") is None # Confirm no patient with invalid ID was created
    # Check that the next patient ID in sequence was NOT used by this failed attempt
    next_possible_id_after_john_doe = f"P-{datetime.date.today().year}-{registry._id_generator._counter+1:04d}"
    assert registry.get_patient(next_possible_id_after_john_doe) is None 
    print("  Patient not registered in the system.")
    
    assert result_missing["data"]["first_name"] == "Jane"
    assert "date_of_birth" not in result_missing["data"] # Missing field
    print("  Previously entered information retained in form data.")
    print("  Scenario PASSED: Attempt to Register Patient with Missing Required Information")

    # --- User Story 2: Add Patient Emergency Contact ---
    print("\n--- Scenario: Successfully Adding a Single Emergency Contact ---")
    # Using the previously registered patient (John Doe)
    print(f"  Using registered patient with ID: {initial_patient_id}")
    assert registry.get_patient(initial_patient_id) is not None

    emergency_contact_full = {
        "contact_name": "Jane Doe",
        "relationship": "Spouse",
        "phone_number": "555-987-6543",
        "email_address": "jane.doe@example.com"
    }
    print(f"  Attempting to add emergency contact: {emergency_contact_full['contact_name']}")
    result_ec_success = registry.add_emergency_contact(initial_patient_id, emergency_contact_full)

    # Validate results based on Acceptance Criteria
    assert result_ec_success["status"] == "success"
    print(f"  Result: {result_ec_success['message']}")
    
    updated_patient = registry.get_patient(initial_patient_id)
    assert len(updated_patient["emergency_contacts"]) == 1
    added_contact = updated_patient["emergency_contacts"][0]
    print(f"  Emergency contact '{added_contact['contact_name']}' saved and associated.")
    assert added_contact["contact_name"] == "Jane Doe"
    assert added_contact["relationship"] == "Spouse"
    assert added_contact["phone_number"] == "555-987-6543"
    assert added_contact["email_address"] == "jane.doe@example.com"
    
    assert result_ec_success["contact_data"] == added_contact
    assert len(result_ec_success["patient_data_with_contacts"]["emergency_contacts"]) == 1
    print("  New contact data returned for display in patient's list.")
    print("  Scenario PASSED: Successfully Adding a Single Emergency Contact")

    print("\n--- Scenario: Attempt to Add Emergency Contact with Missing Required Information ---")
    # Using the same registered patient (John Doe)
    print(f"  Using registered patient with ID: {initial_patient_id}")

    emergency_contact_missing = {
        "contact_name": "Alice Wonderland",
        # "relationship": deliberately missing
        # "phone_number": deliberately missing
        "email_address": "alice@example.com" # Optional field, so won't cause error by itself
    }
    print(f"  Attempting to add emergency contact with missing details for: {emergency_contact_missing['contact_name']}")
    result_ec_missing = registry.add_emergency_contact(initial_patient_id, emergency_contact_missing)

    # Validate results based on Acceptance Criteria
    assert result_ec_missing["status"] == "error"
    print(f"  Result: {result_ec_missing['message']}")
    
    assert "relationship" in result_ec_missing["errors"]
    print(f"  Error message: '{result_ec_missing['errors']['relationship']}'")
    assert result_ec_missing["errors"]["relationship"] == "Relationship is required"
    
    assert "phone_number" in result_ec_missing["errors"]
    print(f"  Error message: '{result_ec_missing['errors']['phone_number']}'")
    assert result_ec_missing["errors"]["phone_number"] == "Phone Number is required"

    current_patient_contacts = registry.get_patient(initial_patient_id)["emergency_contacts"]
    assert len(current_patient_contacts) == 1 # Only Jane Doe should be there
    assert not any(c["contact_name"] == "Alice Wonderland" for c in current_patient_contacts)
    print("  Emergency contact not saved.")
    
    assert result_ec_missing["data"]["contact_name"] == "Alice Wonderland"
    print("  Entered contact name retained in form data.")
    print("  Scenario PASSED: Attempt to Add Emergency Contact with Missing Required Information")

    print("\n--- All Simulated Scenarios Completed ---")
```