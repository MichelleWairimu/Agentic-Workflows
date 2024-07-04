# workflow.py
from langgraph.graph import END, StateGraph
from test import (
    check_if_can_answer_question, write_query, execute_query,
    write_answer, explain_no_answer, skip_question
)

from typing_extensions import TypedDict

class WorkflowState(TypedDict):
    question: str
    plan: str
    can_answer: bool
    sql_query: str
    sql_result: str
    answer: str

workflow = StateGraph(WorkflowState)

workflow.add_node("check_if_can_answer_question", check_if_can_answer_question)
workflow.add_node("write_query", write_query)
workflow.add_node("execute_query", execute_query)
workflow.add_node("write_answer", write_answer)
workflow.add_node("explain_no_answer", explain_no_answer)

workflow.set_entry_point("check_if_can_answer_question")

workflow.add_conditional_edges(
    "check_if_can_answer_question",
    skip_question, # given the text response from this function,
    { # we choose which node to go to
        "yes": "explain_no_answer",
        "no": "write_query",
    },
)

workflow.add_edge("write_query", "execute_query")
workflow.add_edge("execute_query", "write_answer")

workflow.add_edge("explain_no_answer", END)
workflow.add_edge("write_answer", END)

app = workflow.compile()
