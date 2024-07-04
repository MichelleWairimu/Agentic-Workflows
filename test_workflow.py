from workflow import app

inputs = {"question": "Count customers by zip code. Return the 5 most common zip codes"}
result = app.invoke(inputs)
print(result)
