# app.py
import streamlit as st
from workflow import app

# Streamlit app
st.title("RetailX AI Assistant")
st.write("Ask a question about RetailX customers, products, and sales:")

question = st.text_input("Question")
if st.button("Submit"):
    if question:
        inputs = {"question": question}
        result = app.invoke(inputs)
        st.write("Answer:", result['answer'])
    else:
        st.write("Please enter a question.")
