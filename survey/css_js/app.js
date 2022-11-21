var url = ""
var counter = 2;
function resetAllFields(){
    document.getElementById("userInput").value = "";
    $('input[name="question1"]').prop('checked', false);
    $('input[name="question2"]').prop('checked', false);
    $('#question3').val('')
}

function submitInput(){
    var inputFromUser = document.getElementById("userInput").value;
    if(inputFromUser.length === 0){
        $("#messageValidation").show()
    }
    else{
        $("#messageValidation").hide()
        var data = {
            "input": true,
            "message": inputFromUser
        }
        //Here we send and recieve Data
        console.log(data)
        //Displaying Output from backend
        $("#output").text("You still have: "+ (counter-1) + " more other than this");


        $("#questionairesToSend").show()
        $("#inputFromUser").hide()
        resetAllFields();
    }
}

function submitQuestionaire(){
    $("#messageQuestionare").hide()

    var q1 = $('input[name="question1"]:checked').val();
    var q2 = $('input[name="question2"]:checked').val();
    var q3 = $("#question3").val();

    if(q1 === undefined || q2 === undefined || q3.length === 0){
        $("#messageQuestionare").show()
    }

    else{
        var data = {
            "input": false,
            "Question1": q1,
            "Question2": q2,
            "Question3": q3
        }
        //Here we send and recieve Data
        //console.log(data);

        var xhr = new XMLHttpRequest();
        xhr.open("POST", url, true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4 && xhr.status === 200) {
                var json = JSON.parse(xhr.responseText);
                console.log(json);
            }
        };
        var request = JSON.stringify(data);
        xhr.send(request);
        console.log(request);


        resetAllFields();
        $("#questionairesToSend").hide()
        $("#inputFromUser").show()
        if(counter == 1){
            $("#output").text("Thank you for taking this Survey");
            $("#inputFromUser").hide()
            return
        }
        counter --;
    }
    
}