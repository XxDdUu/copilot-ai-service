from langchain_core.tools import tool

@tool
def send_email(recipient: str, subject: str, body: str) -> str:
    """
    Send an email to a recipient with a subject and body.
    Use this tool when the user explicitly asks to email or notify someone.
    
    Args:
        recipient (str): The email address of the recipient.
        subject (str): The subject line of the email.
        body (str): The main content/body of the email.
    """
    try:
        # Mock email execution
        print(f"\n--- MOCK EMAIL SENT ---")
        print(f"To: {recipient}")
        print(f"Subject: {subject}")
        print(f"Body:\n{body}")
        print(f"-----------------------\n")
        return f"Mock email successfully sent to {recipient} with subject '{subject}'."
    except Exception as e:
        return f"Error sending email: {str(e)}"
