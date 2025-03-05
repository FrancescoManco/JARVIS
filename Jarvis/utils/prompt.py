


def prompt_email_generation(email):
    generazione_email = f"""
    
I will provide you with a message written by a user. Your task is to generate a
 new versions of this message while maintaining the same tone, style, and personal characteristics.

 - Do not change the meaning of the message.
 - Keep the same length and structure.
 - If the message has a formal tone, maintain it. If it is informal or friendly, keep it that way.
 - If the user has typical expressions or phrases, try to reuse them.
 - If the message contains personal details (e.g., names, dates, specific references), 
   replace them with generic but coherent details.

 Now, generate a version of this message following the above rules.
{email}

"""
    return generazione_email



def prompt_email_generation_non_preferred(email):
    generazione_email = f"""
You will receive an email written by a user. Your task is to create a **generation prompt** that will instruct 
an AI model to generate emails **identical in tone, style, and structure** to the original email.  

- Ensure that the prompt captures the user's **writing style** (formal, informal, friendly, direct, etc.).  
- If the user uses specific phrases frequently, include them in the prompt.  
- Maintain the length and typical sentence structure.  

### Example input email:  
"Hey Anna, I finished the presentation! Let me know if you need any changes before the meeting. See you!"  

### Expected output (generation prompt):  
"Generate an email that is **casual and friendly**, similar to how the user writes. Keep it short and direct, 
using natural language. The email should sound like an informal conversation with a colleague or friend. 
Do not change the structure or main message."  

Now, generate a **generation prompt** based on the following email: {email}


"""
    return generazione_email

def genera_prompt(email):
    prompt=f"""
You will receive an email written by a user. Your task is to generate a **rejected email** that has the **opposite tone, 
style, and structure** compared to the original message.  

- If the original email is formal, make the rejected version **overly informal or casual**.  
- If the original email is concise and direct, make the rejected version **lengthy and indirect**.  
- Change sentence structures and avoid using the user's typical phrasing.  

### Example input email:  
"Hey Anna, I finished the presentation! Let me know if you need any changes before the meeting. See you!"  

### Expected output (rejected email):  
"Dear Ms. Anna,  
I am writing to inform you that I have completed the presentation as per your request. 
Please take the time to review it carefully, and do not hesitate to let me know if you require any modifications prior 
to the scheduled meeting. I look forward to your feedback.  
Best regards,  
[Your Name]"  

Now, generate a **rejected email** based on the following input:{email} 
"""
    return prompt