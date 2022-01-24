var GUESSES = {};
var WORDS = {};
var ROW_NUM = 6;

function goHome(){
    readWords();
    readGuesses();
    drawInitialBoard(function(){
        $("#start-play").show();
        $("#submit-response").hide();
        $("#play-again").hide();
        $("#edit-previous").hide();
    });

}

function displayBoard(callback) {
    $("#help").hide();
    $("#board-container").show();

}

function drawInitialBoard(callback){
    displayBoard();

    $("#board").html("");
    var gamerow = $("#game-row-clone").clone();
    gamerow.removeAttr("id");
    gamerow.show();

    var tile = $("#tile-clone").clone();
    tile.removeAttr("id");

    for (let i = 0; i < 5; i++) {
        gamerow.find("div").first().append(tile.clone());
    }
    for (let i = 0; i < ROW_NUM; i++) {
        $("#board").append(gamerow.clone());
    }

    var msg = ["guess", "your", "words", "in", "six", "tries"];
    var style = ["correct", "present", "absent", "tbd", "tbd", "tbd"];

    for (let i = 0; i < ROW_NUM; i++) {
        var row = $("#board game-row").eq(i);
            for (let j = 0; j < 5; j++) {
                writeInitLetter(row, i, j);
            }
    }
    function writeInitLetter(row, i, j) {
        setTimeout(function() {
            var tile = row.find(".tile").eq(j);
            if (j < msg[i].length) {
                tile.attr("data-state", style[i]);
                tile.text(msg[i][j]);
            }
            else {
                tile.attr("data-state", "empty");
            }
            tile.show();
            tile.attr("data-animation", "pop");
            tile.attr("data-animation", "flip-in");
            tile.attr("data-animation", "flip-out");
            if ((i == ROW_NUM-1) && (j == 4)) {
                callback();
            }
        }, 20*(i*ROW_NUM+j));
    }
}

function readTXT(file_path){
    var lines;
    $.ajax({
        url: file_path,
        type: 'get',
        async: false,
        success: function(data) {
            lines = data.split("\n");
        }
     });
    return lines;
}

function readWords(){
    $.get('data/small.txt', function(data) {
        WORDS = data.split("\n");
    })
    // WORDS = readTXT('data/small.txt');
}

function readGuesses(){
    // var player = "smallMaxInformationGainWordlePlayer";
    var player = "HeuristicWordlePlayer";
    $.getJSON( "gh-pages/traces_" + player + ".json", function(data) {
        GUESSES = data;
    });
}

function startPlay(){
    for (let i = 0; i < ROW_NUM; i++) {
        var row = $("#board game-row").eq(i);
            for (let j = 0; j < 5; j++) {
                var tile = row.find(".tile").eq(j);
                tile.attr("data-state", "empty");
                tile.text("");
                tile.removeClass("inactive");
            }
    }
    $("#start-play").hide();
    $("#play-again").hide();
    $("#submit-response").show();
    $("#edit-previous").show();

    displayBoard();
    // disableResponse();

    showWord(0, getRandomFirstGuessIdx());
}

function getRandomFirstGuessIdx(){
    var items = Object.keys(GUESSES);
    var pick = items[Math.floor(Math.random()*items.length)];
    return pick.split(",")[0];
}

function disableResponse(){
    var btn = $("#submit-response");
    btn.css("cursor", "not-allowed");
    btn.removeClass("hover");
    btn.attr("onclick", "");
    btn.css("background-color", "var(--key-bg)");
}
function enableResponse(){
    var btn = $("#submit-response");
    btn.css("cursor", "pointer");
    btn.addClass("hover");
    btn.attr("onclick", "submitResponse()");
    btn.css("background-color", "var(--blue)");
}

function showWord(i, word_idx, state){
    displayBoard();

    var row = $("#board game-row").eq(i);
    row.attr("letters", WORDS[word_idx]);
    row.attr("guess_state", word_idx);
    if (typeof(state) == "undefined") {
        state = "absent";
    }
    for (let j = 0; j < 5; j++) {
        setTimeout(function() {
            var tile = row.find(".tile").eq(j);
            tile.attr("data-state", state);
            tile.attr("data-animation", "pop");
            tile.attr("data-animation", "flip-in");
            tile.attr("data-animation", "flip-out");
            tile.attr("letter", WORDS[word_idx][j]);
            tile.text(WORDS[word_idx][j]);
            setTileButton(tile);
        }, 50*(i*ROW_NUM+j));
    }
}

function setTileButton(tile) {
    tile.css("cursor", "pointer");
    tile.attr("onclick", "tileChangeColor(this)");
    tile.removeClass("inactive");
}

function tileChangeColor(btn) {
    var change = {
        // "tbd": "correct",
        "correct": "present",
        "present": "absent",
        "absent": "correct",
        "congrats": "absent",
    }
    var tile = $(btn);
    var original = tile.attr("data-state");
    tile.attr("data-state", change[original]);

    // var siblings = tile.siblings();
    // var have_colors = true;
    // for (var i = 0; i < siblings.length; i++)
    //     have_colors &&= ($(siblings[i]).attr("data-state") != "tbd");
    // if (have_colors) {
    //     enableResponse();
    // }
}

function getResponseCode(i) {
    var row = $("#board game-row").eq(i);
    var evaluations = {"correct": 2, "present": 1, "absent": 0};
    var code = 0;

    for (let j = 0; j < 5; j++) {
        var tile = row.find(".tile").eq(j);
        code += evaluations[tile.attr("data-state")] * Math.pow(3, j);
    }
    return code.toString();
}

function has_response(guess_state) {
    return guess_state.split(",").length > 1
}

function lockRow(row) {
    for (let j = 0; j < 5; j++) {
        var tile = row.find(".tile").eq(j);
        tile.attr("onclick", "");
        tile.css("cursor", "not-allowed");
        tile.addClass("inactive");
    }
}
function unlockRow(i) {
    var row = $("#board game-row").eq(i);
    for (let j = 0; j < 5; j++) {
        var tile = row.find(".tile").eq(j);
        setTileButton(tile);
    }
    var guess_state = row.attr("guess_state");
    row.attr("guess_state", guess_state.split(",")[0]);
}

function animateSuccessRow(i) {
    var row = $("#board game-row").eq(i);
    for (let j = 0; j < 5; j++) {
        setTimeout(function(i, j){
            var tile = row.find(".tile").eq(j);
            tile.attr("data-state", "congrats");
            console.log(tile);
        }, i*ROW_NUM+j);
    }
}

function submitResponse(){
    var d = Object.assign({}, GUESSES);
    var next_word_idx;
    var next_i;
    var final_guess = false;

    for (let i = 0; i < ROW_NUM; i++) {
        var row = $("#board game-row").eq(i);
        var guess_state = row.attr("guess_state");
        if (has_response(guess_state)) d = d[guess_state];
        else {
            var new_state = guess_state + "," + getResponseCode(i);
            if (new_state in d) {
                var next_states = Object.keys(d[new_state]);
                next_word_idx = parseInt(next_states[0].split(",")[0]);
                next_i = i + 1;
                row.attr("guess_state", new_state);
                lockRow(row);
                showWord(next_i, next_word_idx);
                if (next_states.length == 1) final_guess = true;
            } else if (getResponseCode(i) == "242") {
                next_i = i;
                final_guess = true;
            } else {
                failPlay();
                return;
            }
            if (final_guess) {
                showWord(next_i, next_word_idx, "congrats");
                $("#submit-response").hide();
                $("#play-again").show();
            }
            else if (new_state in d) showWord(next_i, next_word_idx);
            break;
        }
    }
}

function clearTiles(row) {
    for (let j = 0; j < 5; j++) {
        var tile = row.find(".tile").eq(j);
        tile.attr("data-state", "empty");
        tile.removeAttr("letter");
        tile.text("");
        tile.css("cursor", "");
        tile.removeAttr("onclick");
        tile.removeClass("inactive");
    }
}

function editPrevious(){
    var prev_i = 0;

    for (let i = ROW_NUM-1; i >= 1; i--) {
        var row = $("#board game-row").eq(i);
        var guess_state = row.attr("guess_state");
        if (guess_state) {
            row.removeAttr("guess_state");
            row.attr("letters", "");
            clearTiles(row);
            prev_i = i-1;
            break;
        }
    }
    if (prev_i >= 0) unlockRow(prev_i);
    $("#submit-response").show();
    $("#play-again").hide();

    displayBoard();
}

function failPlay(){
    $("#alert").dialog("open");
}

function closeBox(name){
    $("#" + name).dialog("close");
}

function switchBoard() {
    $("#help").toggle();
    $("#board-container").toggle();
}

function switchStory() {
    $("#story").toggle();
    $("#board-container").toggle();
    // $("#action-container").toggle();
}