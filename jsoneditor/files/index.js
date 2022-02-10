var editor

function init(data) {
    const container = document.getElementById("jsoneditor");
    const options = data.options;
    editor = new JSONEditor(container, options);
    const initialJson = data.data;
    const jsoneditorMenu = document.getElementsByClassName('jsoneditor-menu')[0]
    editor.set(initialJson);
    document.title = data.title
    if (data.callback) {
        addCallbackButton(jsoneditorMenu, editor)
    }
    if (data.keep_running) {
        addCloseButton(jsoneditorMenu);
    }
    if (data.additional_js) {
        eval(data.additional_js)
    }
    if (!data.keep_running) {
        setTimeout(() => makeSureServerIsClosed(), 1000)
    }
}


function makeSureServerIsClosed() {
    let xhr = new XMLHttpRequest();
    xhr.open("GET", window.location.origin + '/close');
    xhr.onerror = () => {}
    xhr.send(null);
}


function addCallbackButton(jsoneditorMenu, editor) {
    const callbackButton = document.createElement('button')
    callbackButton.className = 'send-back-json'
    callbackButton.title = 'Trigger callback with the current data'
    jsoneditorMenu.append(callbackButton)
    callbackButton.onclick = () => {
        var xhr = new XMLHttpRequest();
        xhr.open("POST", window.location.origin + '/callback', true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.send(JSON.stringify({
            data: editor.get()
        }));
    }
}


function addCloseButton(jsoneditorMenu) {
    const closeButton = document.createElement('button')
    closeButton.className = 'finish-and-shutdown'
    closeButton.title = 'Finish and Shutdown'
    jsoneditorMenu.append(closeButton)
    closeButton.onclick = () => {
        let xhr = new XMLHttpRequest();
        xhr.onreadystatechange = function () {
            if (this.readyState == 4 && this.status == 200) {
                window.close();
            }
        }
        xhr.open("GET", window.location.origin + '/close');
        xhr.onerror = () => {
            window.close();
        }
        xhr.send(null);
    }
}


function getData() {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            data = JSON.parse(xhr.responseText);
            init(data)
        }
    };
    xhr.open("GET", window.location.origin + '/get_data', true);
    xhr.send();
}

getData();
