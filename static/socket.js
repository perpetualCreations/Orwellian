var socket = io();
var tableDataCache = [];

socket.on("eventUpdate", data => {
    // there should NEVER be STATE updates, they aren't defined.
    if (data["type"] == "STATE") {
        console.log("???")
    }
    else if (data["type"] == "TABLE") {
        // scripting for populating target table
        document.getElementById(data["id"]).innerHTML = "";
        for (row in data["data"]) {
            tableRow = document.createElement("tr");
            for (column in data["data"][row]) {
                if (data["data"][row][column] == null) {
                    data["data"][row][column] = "";
                }
                tableRow.innerHTML += ("<td>" + data["data"][row][column] + "</td>");
            }
            if (data["id"] == "user-table-content") {
                // add select button to all agents
                tableRow.innerHTML += ('<td><button onclick="' + "remove('" + data["data"][row][0] + "');" + '">Remove</button></td>'); 
                document.getElementById(data["id"]).appendChild(tableRow);
                // when table content is for agents, cache into variable
                tableDataCache = data["data"];
            }
        }
    }
});

socket.on("logError", data => {
    document.getElementById("errors").style.display = "initial";
    document.getElementById("error-log").innerHTML += "<p>[" + data["timestamp"] + "]: " + data["message"] + "</p>";
});

function dispatchCommand(command, type, payload) {
    socket.emit("command", {"command": command, "requestType": type, "payload": payload});
}

function remove(name) {
    dispatchCommand("REMOVE_USER", "PAYLOAD", name);
}

function add() {
    dispatchCommand("ADD_USER", "PAYLOAD", document.getElementById("add-user-input").value);
    document.getElementById("add-user-input").value = "";
}
