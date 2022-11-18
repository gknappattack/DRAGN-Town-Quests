from flask import Flask, render_template, request, jsonify #importing the module
import json
from .main import QuestEngine

qe = QuestEngine()

app=Flask(__name__, template_folder='html', static_folder='css_js') #instantiating flask object

@app.route('/survey')
def survey():
    return render_template('index.html')

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    data = request.data
    json_data = json.loads(data)
    print("THIS IS THE INPUT: ", json_data)

    # THIS IS WHERE I NEED TO PARSE THE INPUT AND RUN IT THROUGH THE MODELS AND RETURN

    res = qe.receive_input_API(json_data["data"])

    return jsonify(res)


@app.route('/') #defining a route in the application
def func(): #writing a function to be executed 
       return 'PythonGeeks'

if __name__=='__main__': #calling  main 
       app.debug=True #setting the debugging option for the application instance
       app.run(host="0.0.0.0", port="5000") #launching the flask's integrated development webserver