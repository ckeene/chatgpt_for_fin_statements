import streamlit as st
import openai
import requests
import os
import pandas as pd
# Read api keys from file named apikey.py of form OPENAI_API_KEY = "your key"
from apikey import OPENAI_API_KEY, FMP_API_KEY

openai.api_key = OPENAI_API_KEY

def get_jsonparsed_data(url):
    try:
        # Send an HTTP GET request to the API
        response = requests.get(url)
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
            # Now you can work with the parsed JSON data
            return data
        else:
            print("Request failed with status code:", response.status_code)
    except requests.RequestException as e:
        print("An error occurred:", e)

def get_financial_statements(ticker, limit, period, statement_type):
    if statement_type == "Income Statement":
        url = f"https://financialmodelingprep.com/api/v3/income-statement/{ticker}?period={period}&limit={limit}&apikey={FMP_API_KEY}"
    elif statement_type == "Balance Sheet":
        url = f"https://financialmodelingprep.com/api/v3/balance-sheet-statement/{ticker}?period={period}&limit={limit}&apikey={FMP_API_KEY}"
    elif statement_type == "Cash Flow":
        url = f"https://financialmodelingprep.com/api/v3/cash-flow-statement/{ticker}?period={period}&limit={limit}&apikey={FMP_API_KEY}"
    data = get_jsonparsed_data(url)
    if isinstance(data, list) and data:
        print("Dataframe is",pd)
        return pd.DataFrame(data)
    else:
        st.error("Unable to fetch financial statements. Please ensure the ticker is correct and try again.")
        return pd.DataFrame()

def generate_financial_summary(financial_statements, statement_type):
    """
    Generate a summary of financial statements for the statements using GPT-3.5 Turbo or GPT-4.
    """
    summaries = []
    for i in range(len(financial_statements)):
        row_data = financial_statements.iloc[i]
        if statement_type == "Income Statement":
            summary = f"""
                For the period ending {financial_statements['date'][i]}, the company reported the following:
                {row_data}
                """
        elif statement_type == "Balance Sheet":
            summary = f"""
                For the period ending {financial_statements['date'][i]}, the company reported the following:
                {row_data}
                """
        elif statement_type == "Cash Flow":
            summary = f"""
                For the period ending {financial_statements['date'][i]}, the company reported the following:
                {row_data}
                """
        summaries.append(summary)

    # Combine all summaries into a single string
    all_summaries = "\n\n".join(summaries)

    # Call GPT-4 for analysis - didn't work so shifted to 3.5
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are an AI trained to provide financial analysis based on financial statements.",
            },
            {
                "role": "user",
                "content": f"""
                Please analyze the following data and provide insights:\n{all_summaries}.\n 
                Write each section out as instructed in the summary section and then provide analysis of how it's changed over the time period.
                ...
                """
            }
        ]
    )

    return response['choices'][0]['message']['content']
        
def financial_statements():
    st.title('GPT-4 & Financial Statements')
    statement_type = st.selectbox("Select financial statement type:", ["Income Statement", "Balance Sheet", "Cash Flow"])
    col1, col2 = st.columns(2)
    with col1:
        period = st.selectbox("Select period:", ["Annual", "Quarterly"]).lower()
    with col2:
        limit = st.number_input("Number of past financial statements to analyze:", min_value=1, max_value=10, value=4)
    default_value = "googl"
    ticker = st.text_input("Please enter the company ticker:",default_value)
    if st.button('Run'):
        if ticker:
            ticker = ticker.upper()
            financial_statements = get_financial_statements(ticker, limit, period, statement_type)

            with st.expander("View Financial Statements"):
                st.dataframe(financial_statements)

            financial_summary = generate_financial_summary(financial_statements, statement_type)
            st.write(f'Summary for {ticker}:\n {financial_summary}\n')

def main():
    st.sidebar.title('AI Financial Analyst')
    app_mode = st.sidebar.selectbox("Choose your AI assistant:",
        ["Financial Statements"])
    if app_mode == 'Financial Statements':
        financial_statements()


if __name__ == '__main__':
    main()
