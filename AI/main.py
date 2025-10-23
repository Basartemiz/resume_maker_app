
import parser 

def __main__():
   
    input_of_user=input("Enter user information: ")
    resume_data = parser.parse(input_of_user)
    pretty_print(resume_data)


def pretty_print(resume_data: dict):
    """
    🔹 Purpose:
        Nicely format and print the generated resume data.

    🔹 Parameters:
        resume_data: dict - Structured resume data including skills, education, experience, references, personal info, and profile.
    """

    print("\n=== Generated Resume Data ===\n")
    for section, content in resume_data.items():
        print(f"--- {section.upper()} ---")
        print(content)
        print("\n")