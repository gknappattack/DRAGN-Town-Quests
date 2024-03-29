from flask import Flask, render_template, request, jsonify #importing the module
import json
from main import QuestEngine

qe = QuestEngine()
app=Flask(__name__, template_folder='./demo/html', static_folder='./demo/static') #instantiating flask object

@app.route('/')
def survey():
    return render_template('demo.html')

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    data = request.data
    json_data = json.loads(data)
    print("THIS IS THE INPUT: ", json_data)

    # THIS IS WHERE I NEED TO PARSE THE INPUT AND RUN IT THROUGH THE MODELS AND RETURN
    if json_data["input"]:
        res = qe.receive_input_API(json_data["message"])
        print("The Res: ", res)
        return jsonify(res)
    else:
        print("Sending Back to Front End. . .")
        successful_log = qe.log_round(json_data, True)

        res = {
            "log_success":successful_log
        }
        return jsonify(res)

if __name__=='__main__': #calling  main 
    app.debug=True #setting the debugging option for the application instance
    app.run(host="0.0.0.0", port="3000") #launching the flask's integrated development webserver
