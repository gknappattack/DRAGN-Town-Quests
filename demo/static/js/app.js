
function onLoad() {
    var input = document.getElementById("user_input");
    console.log(input)
    // Execute a function when the user presses a key on the keyboard
    input.addEventListener("keypress", function(event) {
        // If the user presses the "Enter" key on the keyboard
        if (event.key === "Enter") {
        // Cancel the default action, if needed
        event.preventDefault();
        // Trigger the button element with a click
        //console.log("event triggered");
        sendMessage();
        }
    });
}


function sendMessage() {
    var user_input = document.getElementById("user_input").value;
    if (user_input === "") {
        console.log("Input was empty");
    }
    else {
        console.log(user_input);
        var npc_input = "This is a test.";
        document.getElementById("chat_console").innerHTML = document.getElementById("chat_console").innerHTML + "<div class=\"user_chat\">" + user_input + "</div>" + "<div class=\"npc_chat\">" + npc_input + "</div>";
        document.getElementById("user_input").value = null;
    }
}