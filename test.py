from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_openai import ChatOpenAI
from data_preparation import query_db
from setup_environment import LLAMA_API

DB_DESCRIPTION = """You have access to the following tables and columns in a SQLite3 database:

Retail Table
Customer_ID: A unique ID that identifies each customer.
Name: The customer's name.
Gender: The customer's gender: Male, Female.
Age: The customer's age.
Country: The country where the customer resides.
State: The state where the customer resides.
City: The city where the customer resides.
Zip_Code: The zip code where the customer resides.
Product: The product purchased by the customer.
Category: The category of the product.
Price: The price of the product.
Purchase_Date: The date when the purchase was made.
Quantity: The quantity of the product purchased.
Total_Spent: The total amount spent by the customer.
"""

model = ChatOpenAI(
    openai_api_key=LLAMA_API,
    openai_api_base="https://api.llama-api.com",
    model="llama3-70b"  # Ensure the model is correctly specified
)

can_answer_router_prompt = PromptTemplate(
    template="""system
    You are a database reading bot that can answer users' questions using information from a database. \\n

    {data_description} \\n\\n

    Given the user's question, decide whether the question can be answered using the information in the database. \\n\\n

    Return a JSON with two keys, 'reasoning' and 'can_answer', and no preamble or explanation.
    Return one of the following JSON:

    {{"reasoning": "I can find the average total spent by customers in California by averaging the Total_Spent column in the Retail table filtered by State = 'CA'", "can_answer":true}}
    {{"reasoning": "I can find the total quantity of products sold in the Electronics category using the Quantity column in the Retail table filtered by Category = 'Electronics'", "can_answer":true}}
    {{"reasoning": "I can't answer how many customers purchased products last year because the Retail table doesn't contain a year column", "can_answer":false}}

    user
    Question: {question} \\n
    assistant""",
    input_variables=["data_description", "question"],
)

can_answer_router = can_answer_router_prompt | model | JsonOutputParser()

def check_if_can_answer_question(state):
    try:
        result = can_answer_router.invoke({"question": state["question"], "data_description": DB_DESCRIPTION})
        return {"plan": result["reasoning"], "can_answer": result["can_answer"]}
    except Exception as e:
        print(f"Error in check_if_can_answer_question: {e}")
        return {"plan": str(e), "can_answer": False}

def skip_question(state):
    return "no" if state["can_answer"] else "yes"

write_query_prompt = PromptTemplate(
    template="""system
    You are a database reading bot that can answer users' questions using information from a database. \\n

    {data_description} \\n\\n

    In the previous step, you have prepared the following plan: {plan}

    Return an SQL query with no preamble or explanation. Don't include any markdown characters or quotation marks around the query.
    user
    Question: {question} \\n
    assistant""",
    input_variables=["data_description", "question", "plan"],
)

write_query_chain = write_query_prompt | model | StrOutputParser()

def write_query(state):
    try:
        result = write_query_chain.invoke({
            "data_description": DB_DESCRIPTION,
            "question": state["question"],
            "plan": state["plan"]
        })
        return {"sql_query": result}
    except Exception as e:
        print(f"Error in write_query: {e}")
        return {"sql_query": str(e)}

def execute_query(state):
    query = state["sql_query"]
    try:
        return {"sql_result": query_db(query).to_markdown()}
    except Exception as e:
        return {"sql_result": str(e)}

write_answer_prompt = PromptTemplate(
    template="""system
    You are a database reading bot that can answer users' questions using information from a database. \\n

    In the previous step, you have planned the query as follows: {plan},
    generated the query {sql_query}
    and retrieved the following data:
    {sql_result}

    Return a text answering the user's question using the provided data.
    user
    Question: {question} \\n
    assistant""",
    input_variables=["question", "plan", "sql_query", "sql_result"],
)

write_answer_chain = write_answer_prompt | model | StrOutputParser()

def write_answer(state):
    try:
        result = write_answer_chain.invoke({
            "question": state["question"],
            "plan": state["plan"],
            "sql_result": state["sql_result"],
            "sql_query": state["sql_query"]
        })
        return {"answer": result}
    except Exception as e:
        print(f"Error in write_answer: {e}")
        return {"answer": str(e)}

cannot_answer_prompt = PromptTemplate(
    template="""system
    You are a database reading bot that can answer users' questions using information from a database. \\n

    You cannot answer the user's questions because of the following problem: {problem}.

    Explain the issue to the user and apologize for the inconvenience.
    user
    Question: {question} \n
    assistant""",
    input_variables=["question", "problem"],
)

cannot_answer_chain = cannot_answer_prompt | model | StrOutputParser()

def explain_no_answer(state):
    try:
        result = cannot_answer_chain.invoke({
            "problem": state["plan"],
            "question": state["question"]
        })
        return {"answer": result}
    except Exception as e:
        print(f"Error in explain_no_answer: {e}")
        return {"answer": str(e)}

# Test function to run the workflow
def run_test_workflow():
    state = {
        "question": "What is the average total spent by customers in California?",
        "can_answer": None,
        "plan": None,
        "sql_query": None,
        "sql_result": None
    }

    # Step 1: Check if the question can be answered
    state.update(check_if_can_answer_question(state))
    if not state["can_answer"]:
        state.update(explain_no_answer(state))
        return state["answer"]

    # Step 2: Generate the SQL query
    state.update(write_query(state))
    if "sql_query" not in state or not state["sql_query"]:
        state.update(explain_no_answer(state))
        return state["answer"]

    # Step 3: Execute the SQL query
    state.update(execute_query(state))
    if "sql_result" not in state or not state["sql_result"]:
        state.update(explain_no_answer(state))
        return state["answer"]

    # Step 4: Write the final answer
    state.update(write_answer(state))
    return state["answer"]

# Run the test workflow
print(run_test_workflow())
