var url = "/chat"
const MAX_COUNTER = 4;
var counter = MAX_COUNTER; //This counter allows you to take the survey 2 times
$('#dragnLink').hide();
var subjectID = 0;
var prev_input = "";
var prev_p1 = "";
var prev_p2 = "";
var prev_p3 = "";
var prev_key = "";

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
    if (subjectID == 0){
        // set the subject ID
        subjectID = Date.now();
    }
    var inputFromUser = document.getElementById("userInput").value;
    if(inputFromUser.length === 0){
        $("#messageValidation").show()
    }
    else{
        $("#messageValidation").hide()
        var data = {
            "input": true,
            "message": inputFromUser,
            "subjectID": subjectID
        }
        prev_input = inputFromUser;
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
                
                if (json.error == false) {
                    prev_p1 = `${json.p1.quest}|${json.p1.title}|${json.p1.dialogue}`;
                    prev_p2 = `${json.p2.quest}|${json.p2.title}|${json.p2.dialogue}`;
                    prev_p3 = `${json.p3.quest}|${json.p3.title}|${json.p3.dialogue}`;
                    prev_key = `${json.key.p1}/${json.key.p2}/${json.key.p3}`;


                    $('#firstResponse').append('<h3>Prompt 1</h3><br><span id="boldtext">Title: </span>',json.p1.title.substring(6,json.p1.title.length),
                    '<br><br><span id="boldtext">Quest: </span>',json.p1.quest.substring(6,json.p1.quest.length),'<br><br><span id="boldtext">Dialogue: </span>'
                    ,json.p1.dialogue.substring(json.p1.dialogue.indexOf(":")+1,json.p1.dialogue.length),'<br>   ');
                    $('#secondResponse').append('<h3>Prompt 2</h3><br><span id="boldtext">Title: </span>',json.p2.title.substring(6,json.p2.title.length),
                    '<br><br><span id="boldtext">Quest: </span>',json.p2.quest.substring(6,json.p2.quest.length),'<br><br><span id="boldtext">Dialogue: </span>'
                    ,json.p2.dialogue.substring(json.p2.dialogue.indexOf(":")+1,json.p2.dialogue.length),'<br>   ');
                    $('#thirdResponse').append('<h3>Prompt 3</h3><br><span id="boldtext">Title: </span>',json.p3.title.substring(6,json.p3.title.length),
                    '<br><br><span id="boldtext">Quest: </span>',json.p3.quest.substring(6,json.p3.quest.length),'<br><br><span id="boldtext">Dialogue: </span>'
                    ,json.p3.dialogue.substring(json.p3.dialogue.indexOf(":")+1,json.p3.dialogue.length));
                    console.log(json);
                    $("#questionairesToSend").show()
                    $("#loadingPopup").hide()
                }
                else {
                    $("#remainingText").text("")
                    $("#remainingText").append('<span id="boldtext"></span>Round(s) Remaining: ', counter)
                    $("#remainingText").append('<br> <span class="message">AN ERROR OCCURRED IN THE SYSTEM, PLEASE TRY AGAIN.</span>')
                    $("#initialTextInOutput").show()
                    $("#inputFromUser").show()
                    $("#loadingPopup").hide()
                }
            }
        };
        var request = JSON.stringify(data);
        xhr.send(request);


        
        $("#inputFromUser").hide()
        $("#yourInput").text("")
        $("#yourInput").append("<b>Your Input: </b>",inputFromUser)
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
            "Question3": q3,
            "subjectID": subjectID,
            "round": counter - MAX_COUNTER,
            "prevInput": prev_input,
            "prevP1": prev_p1,
            "prevP2": prev_p2,
            "prevP3": prev_p3,
            "prevKey": prev_key
        };
        //Here we send and recieve Data
        //console.log(data);

        var xhr = new XMLHttpRequest();
        xhr.open("POST", url, true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4 && xhr.status === 200) {
                var json = JSON.parse(xhr.responseText);
                console.log(json);

                if (json.log_success == true) {
                    // i need to do the normal stuff here
                    resetAllFields();
                    $("#initialTextInOutput").show()
                    $("#questionairesToSend").hide()
                    $("#inputFromUser").show()
                    if(counter == 1){
                        $("#output").text("Thank you for taking this survey.");
                        $("#output").append("<br>If you want to learn more about what we do, visit:")
                        $("#inputFromUser").hide()
                        $("#dragnLink").show()
                        return
                    }
                    counter --;
                    $("#remainingText").text("")
                    $("#remainingText").append('<span id="boldtext"></span>Round(s) Remaining: ', counter)
                }
                else {
                    // i need to make them repeat, and add text saying there was an internal error, try again
                    resetAllFields();
                    $("#initialTextInOutput").show()
                    $("#questionairesToSend").hide()
                    $("#inputFromUser").show()
                    $("#remainingText").text("")
                    $("#remainingText").append('<span id="boldtext"></span>Round(s) Remaining: ', counter)
                    $("#remainingText").append('<br> <span class="message">AN ERROR OCCURRED IN THE SYSTEM, PLEASE TRY AGAIN.</span>')
                
                }
            }
        };
        var request = JSON.stringify(data);
        xhr.send(request);
    }
    
}