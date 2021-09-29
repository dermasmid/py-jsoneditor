function init(data) {
    const container = document.getElementById("jsoneditor");
    const options = data.options;
    const editor = new JSONEditor(container, options ? options : {colorPicker: false});
    const initialJson = data.data;
    const jsoneditorMenu = document.getElementsByClassName('jsoneditor-menu')[0]
    editor.set(initialJson);
    document.title = data.title
    if (data.callback) {
        addCallbackButton(jsoneditorMenu)
    }
    if (data.keep_running) {
        addCloseButton(jsoneditorMenu);
    }
}


function setFavicon() {
    const favicon = document.createElement('link');
    favicon.rel = 'icon';
    favicon.href = 'files/img/favicon.ico?random=' + (Math.random() + 1).toString(36).substring(7);
    document.getElementsByTagName('head')[0].appendChild(favicon);
};


function addCallbackButton(jsoneditorMenu) {
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
    closeButton.className = 'finnish-and-shuttdown'
    closeButton.title = 'Finnish and shuttdown'
    jsoneditorMenu.append(closeButton)
    closeButton.onclick = () => {
        let xhr = new XMLHttpRequest();
        xhr.onreadystatechange = function() {
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
    xhr.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
        data = JSON.parse(xhr.responseText);
        init(data)
    }
    };
    xhr.open("GET", window.location.origin + '/get_data', true);
    xhr.send();
}


setFavicon();
getData();
