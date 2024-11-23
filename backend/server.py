from flask import Flask, request, jsonify
import openai
import re
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)
# openai.api_key = API_KEY

openai.api_key = ""


def generate_collaboration_prompt(user_message, current_code, chat_history=None):
    prompt = f"""
    You are a helpful coding assistant collaborating with a user to create or refine code. Your responses should be clear, informative, and help the user achieve their goals efficiently.

    Here is the current context:

    Current Code:
    """
    if current_code:
        prompt += f"""
    ```python
    {current_code}
    ```
    """
    else:
        prompt += "No current code provided."

    prompt += f"""

    User Message:
    {user_message}

    Please respond in the following structured format:
    1. Explanation:
       - Explain your reasoning and any assumptions in simple, clear language.
    2. Code Section:
       ```python
       # Provide the complete updated or new code here with minimal comments, only for key points.
       ```
    If you have suggestions for best practices or additional improvements, include them in the Explanation.
    """
    return prompt


def parse_response(response):
    # Split response into Explanation and Code Section based on structured format
    explanation = ""
    code_section = ""

    explanation_match = re.search(r'1\..*?Explanation:\s*-\s*(.*?)(?=2\..*?Code Section:)', response, re.DOTALL)
    # code_section_match = re.search(r'2\..*?Code Section:\s*```python\n(.*?)\n```', response, re.DOTALL)
    code_section_match = re.search(r'2\..*?Code Section:\s*```python\n(.*?)```', response, re.DOTALL | re.MULTILINE)
    
    if explanation_match:
        explanation = explanation_match.group(1).strip()
    if code_section_match:
        code_section = code_section_match.group(1).strip()

    return explanation, code_section

@app.route('/hello', methods=['GET'])
def hello_world():
    return "Hello, World!"

@app.route('/api/code-collaboration', methods=['POST'])
def code_collaboration():
    data = request.get_json() or {}
    current_code = data.get('current_code', '')
    user_message = data.get('user_message', '')

    prompt = generate_collaboration_prompt(user_message, current_code)

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        response_text = response.choices[0].message.content
        print('response text', response_text)
        explanation, code_section = parse_response(response_text)
        return jsonify({"response_text": response_text, "user_message": user_message, "explanation": explanation, "code_section": code_section})
    except Exception as e:
        print(f"error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/quick-action', methods=['POST'])
def quick_action():
    data = request.get_json() or {}
    action = data.get('action')
    current_code = data.get('current_code', '')

    # prompt for different quick actions
    action_messages = {
        'summarize': "Summarize the following code, highlighting its main functionality and important details in a concise manner.",
        'explain': "Explain the following code in detail, including the purpose of each part and why it is implemented this way.",
        'debug': "Debug the following code, identify any potential issues, and suggest fixes. Provide the complete updated version of the code, ensuring all necessary changes are applied.",
        'optimize': "Optimize the following code for better performance. Provide the complete optimized version of the code, ensuring all necessary changes are included."
    }

    if action not in action_messages:
        return jsonify({"error": "Invalid action"}), 400

    user_message = action_messages[action]
    prompt = generate_collaboration_prompt(user_message, current_code)

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        response_text = response.choices[0].message.content
        print('response text', response_text)
        explanation, code_section = parse_response(response_text)
        return jsonify({"response_text": response_text, "user_message": user_message, "explanation": explanation, "code_section": code_section})
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/api/reset', methods=['POST'])
def reset_code():
    return jsonify({"result": ""})


if __name__ == '__main__':
    app.run(debug=True)
