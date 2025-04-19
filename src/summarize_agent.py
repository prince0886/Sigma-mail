import os
import json
from dotenv import load_dotenv
from typing import Optional
from openai import OpenAI

# Load environment variables
load_dotenv()

MODEL = "deepseek/deepseek-chat-v3-0324:free"
SYSTEM_PROMPT = """
You are an email summarization assistant. Your task is to generate concise, accurate summaries of emails.

### Instructions:
- Extract key information, including the main topic, important details, and deadlines.
- Identify any action items or requests mentioned in the email.
- Provide a clear, 2-3 sentence summary that captures the essence of the email.
- Include the sender's name at the beginning of the summary.

### **Output Format:**
```json
{
    "summary": "Concise summary of the email content.",
}
```

### Example:
Input:
Dear John,
Please find attached the meeting agenda for the upcoming team meeting.
The meeting is scheduled for Friday at 3 PM.
If you have any questions or need to make any changes, please let me know.

Output:
```json
{
    "summary": "Meeting Reminder: Please find attached the meeting agenda for the upcoming team meeting. The meeting is scheduled for Friday at 3 PM. If you have any questions or need to make any changes, please let me know.", 
}
```
"""


class EmailSummarizer:
    def __init__(self):
        """Initialize the email summarizer with an API key and model."""
        self.api_key = os.getenv("OPENROUTER_API_KEY")

        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is missing. Please set it in your environment variables.")
        
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
        )

    def summarize(self, email_content: str) -> str:
        """Summarize the given email content."""
        if not email_content.strip():
            return "No content to summarize."

        try:
            completion = self.client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": email_content}
                ],
                # temperature=0.3
            )
            
            response = completion.choices[0].message.content
            json_str = response.strip()
        
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0].strip()
            
            # Debug the JSON string
            # print(f"JSON string to parse: {json_str}")
            
            processed_data = json.loads(json_str)
            summary = processed_data.get("summary", "")
            if not summary:
                return json.dumps({"error": "Summary not found in the response."})
            return summary
            
        except Exception as e:
            return json.dumps({"error": f"Error summarizing email: {e}"})

# Example usage
if __name__ == "__main__":
    frm = "Alice Johnson"
    subject = "Team Meeting Rescheduled"  
    email_content = """
    Hi Team, 
    The weekly team meeting has been rescheduled to Friday at 3 PM instead of Thursday. Please update your calendars accordingly. Let me know if you have any scheduling conflicts.  
    """

    summarizer = EmailSummarizer()
    summary = summarizer.summarize(email_content)
    print(summary)
