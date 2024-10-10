import os
import streamlit as st
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(
    api_key="155e34e001894415abb5e773da4d0a6e",  # Replace with your actual API key
    base_url="https://api.aimlapi.com",
)

# Create a Streamlit app
st.title("Chat with NutriCo")

# Initialize session state for user details and conversation history
if "user_details" not in st.session_state:
    st.session_state.user_details = {
        "name": None,
        "age": None,
        "gender": None,
        "dietary_preferences": None
    }
if "conversation" not in st.session_state:
    st.session_state.conversation = []

# Chat message area
chat_container = st.container()

# Function to check if user details are fully collected
def user_details_collected():
    return all(st.session_state.user_details.values())

# Function to get missing user detail prompt
def get_missing_detail_prompt():
    if not st.session_state.user_details["name"]:
        return "What is your name?"
    elif not st.session_state.user_details["age"]:
        return "How old are you?"
    elif not st.session_state.user_details["gender"]:
        return "What is your gender?"
    elif not st.session_state.user_details["dietary_preferences"]:
        return "Do you have any dietary preferences?"
    else:
        return "Thank you for providing your details. How can I assist you with your nutrition today?"

# Check if conversation is empty and display welcome message
if len(st.session_state.conversation) == 0:
    st.session_state.conversation.append({"role": "assistant", "content": "Welcome to NutriCo! I'm happy to assist you with your nutrition needs. To get started, could you please provide some details about yourself?"})

# Create a form for user input
with st.form("chat_form", clear_on_submit=True):
    user_message = st.text_input("You:")
    submit_button = st.form_submit_button("Send")

# Handle user input
if submit_button and user_message:
    # Append user message to conversation
    st.session_state.conversation.append({"role": "user", "content": user_message})

    # Check if we need to collect user details
    if not user_details_collected():
        missing_detail = get_missing_detail_prompt()
        # Update the respective user detail based on the missing detail prompt
        if missing_detail == "What is your name?":
            st.session_state.user_details["name"] = user_message
        elif missing_detail == "How old are you?":
            st.session_state.user_details["age"] = user_message
        elif missing_detail == "What is your gender?":
            st.session_state.user_details["gender"] = user_message
        elif missing_detail == "Do you have any dietary preferences?":
            st.session_state.user_details["dietary_preferences"] = user_message

        # Generate the next question to ask
        next_question = get_missing_detail_prompt()
        if next_question:
            assistant_message = next_question
        else:
            assistant_message = "Thank you for providing your details. How can I assist you with your nutrition today?"

    else:
        try:
            # Create a chat completion request
            response = client.chat.completions.create(
                model="o1-mini",
                messages=[
                    {"role": "assistant", "content": f"You are NutriCo, a friendly and helpful nutrition assistant. The user details are: Name - {st.session_state.user_details['name']}, Age - {st.session_state.user_details['age']}, Gender - {st.session_state.user_details['gender']}, Dietary Preferences - {st.session_state.user_details['dietary_preferences']}."},
                    *[
                        {"role": message["role"], "content": message["content"]}
                        for message in st.session_state.conversation
                    ],
                    {"role": "user", "content": user_message},
                ],
                max_tokens=1500,  # Increase max_tokens to allow for longer responses
            )

            # Get the chatbot response
            if response and response.choices:
                assistant_message = response.choices[0].message.content
                print("Assistant response:", assistant_message)  # Debugging print statement
                print("Response choices:", response.choices)  # Additional debugging print statement
            else:
                assistant_message = "Sorry, I'm having trouble responding. Please try again!"
        except Exception as e:
            print("Error:", e)  # Debugging print statement
            assistant_message = "Sorry, I'm having trouble responding. Please try again!"

    # Append chatbot response to conversation
    st.session_state.conversation.append({"role": "assistant", "content": assistant_message})

# Display conversation
for message in st.session_state.conversation:
    if message["role"] == "assistant":
        chat_container.markdown(f"""
            <div style="display: flex; align-items: flex-start; margin-bottom: 10px;">
                <div style="margin-right: 10px;">
                    <img src="https://cdn-icons-png.flaticon.com/512/3154/3154724.png" width="40" height="40" style="filter: invert(98%) sepia(129%) saturate(2476%) hue-rotate(1115deg) brightness(103%) contrast(103%);">
                </div>
                <div style="background-color: #333; padding: 10px; border-radius: 10px; color: #fff; flex-grow: 1;">
                    {message['content']}
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        chat_container.markdown(f"""
            <div style="display: flex; align-items: flex-start; margin-bottom: 10px;">
                <div style="margin-right: 10px;">
                    <img src="https://cdn-icons-png.flaticon.com/512/1077/1077063.png" width="40" height="40" style="filter: invert(18%) sepia(19%) saturate(2476%) hue-rotate(115deg) brightness(103%) contrast(103%);">
                </div>
                <div style="background-color: #444; padding: 10px; border-radius: 10px; color: #fff; flex-grow: 1;">
                    {message['content']}
                </div>
            </div>
        """, unsafe_allow_html=True)
