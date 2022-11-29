var url = "/chat"
var counter = 2; //This counter allows you to take the survey 2 times

function resetAllFields(){
    document.getElementById("userInput").value = "";
    $('input[name="question1"]').prop('checked', false);
    $('input[name="question2"]').prop('checked', false);
    $('#question3').val('')
    $('#firstResponse').empty();
    $('#secondResponse').empty();
    $('#thirdResponse').empty();
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
        $("#initialTextInOutput").hide()
        $("#loadingPopup").show()
        var xhr = new XMLHttpRequest();
        xhr.open("POST", url, true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4 && xhr.status === 200) {
                

                var json = JSON.parse(xhr.responseText);
                $('#firstResponse').append('<h3>Prompt 1</h3><br><span id="boldtext">Title: </span>',json.p1.title.substring(6,json.p1.title.length),
                '<br><br><span id="boldtext">Quest: </span>',json.p1.quest.substring(6,json.p1.quest.length),'<br><br><span id="boldtext">Dialogue: </span>'
                ,json.p1.dialogue.substring(8,json.p1.dialogue.length),'<br>   ');
                $('#secondResponse').append('<h3>Prompt 2</h3><br><span id="boldtext">Title: </span>',json.p2.title.substring(6,json.p2.title.length),
                '<br><br><span id="boldtext">Quest: </span>',json.p2.quest.substring(6,json.p2.quest.length),'<br><br><span id="boldtext">Dialogue: </span>'
                ,json.p2.dialogue.substring(8,json.p2.dialogue.length),'<br>   ');
                $('#thirdResponse').append('<h3>Prompt 3</h3><br><span id="boldtext">Title: </span>',json.p3.title.substring(6,json.p3.title.length),
                '<br><br><span id="boldtext">Quest: </span>',json.p3.quest.substring(6,json.p3.quest.length),'<br><br><span id="boldtext">Dialogue: </span>'
                ,json.p3.dialogue.substring(8,json.p3.dialogue.length));
                console.log(json);
                $("#questionairesToSend").show()
                $("#loadingPopup").hide()
            }
        };
        var request = JSON.stringify(data);
        xhr.send(request);


        
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


        resetAllFields();
        $("#initialTextInOutput").show()
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