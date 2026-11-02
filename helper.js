// Solis JS helper functions

function lastUpdated(date_str) {
    let text;
    let time = new Date(date_str).getTime();
    let now = Date.now();
    let sec = (now - time) / 1000 || null;
    //console.log('DEBUG: lastUpdated now time sec', now, time, sec)
    //console.log('DEBUG: lastUpdated test sec', (sec < 0), (sec >= -3), (sec <= -1), (sec >= -3 && sec <= -1))
    if (Number.isNaN(sec) || sec === null) {
        text = "-";
    }
    else if (sec > 3600) {
        text = (sec/60/60).toFixed(0) + ' hours ago';
    } else if (sec > 60) { 
        text = (sec/60).toFixed(0) + ' minutes ago';
    } else if (sec >= -3 && sec <= -1) { 
        text = ' 0 seconds ago';
    } else if (sec < -3) {
        text = sec.toFixed(0) + ' seconds ago (‼️time desync)';
    } else { 
        text = sec.toFixed(0) + ' seconds ago';
    }
    document.getElementById('updated').innerText = text;
}

function jsonType(jsonString) {
    jsonString = jsonString.replaceAll('&', '&amp;').replaceAll('/', '&lt;').replaceAll('>', '&gt;');
    return jsonString.replace(/("(?:\\.|[^"\\])*"(?:\s*:)?|\b(?:true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+-]?\d+)?)/g, function (match) {
        let type = 'number';
        if (match.startsWith('"')) {
            if (match.endsWith(':')) {
                type = 'key';
            } else {
                type = 'string';
            }
        } else if (/true|false/.test(match)) {
            type = 'boolean';
        } else if (/null/.test(match)) {
            type = 'null';
        }
        return `<span class="${type}">${match}</span>`;
    });
};


// from https://gist.github.com/Kvit/df8a04e84a2b56b1dda10dd6d42b9b30
const jsonSearch = (obj, searchKey, replaceValue, results = []) => {
    if (Array.isArray(obj)) {
        for (const element of obj) {
            jsonSearch(element, searchKey, replaceValue, results);
        }
        return obj;
    }
    if (obj === null || typeof obj !== "object") {
        return obj;
    }
    for (const [key, value] of Object.entries(obj)) {
        if (key === searchKey) {
            obj[key] = replaceValue;
            results.push(Array.isArray(value) && value.length === 1 ? value[0] : value);
        }
        if (value !== null && typeof value === "object") {
            jsonSearch(value, searchKey, replaceValue, results);
        }
    }
    return obj;
};

function prettyPrintJSON(json, mask) {
    document.getElementById("message").innerHTML = ''
    document.getElementById("message").innerHTML = `${showClose()}`
    let result
    if (mask) {
        let tmp = jsonSearch(json, 'IP')
        let jStr = jsonType(JSON.stringify(tmp, null, 2))
        //val = mask ? jStr.replace(/[A-Z0-9]{10}/g, '***') : jStr
        result =  jStr.replace(/[A-Z0-9]{10}/g, '***')
    } else {
        result  = jsonType(JSON.stringify(json, null, 2))
    }
    document.getElementById("message").innerHTML += `<pre>${result}</pre>`
    setTimeout(() => {
        document.getElementById('message').scrollIntoView();
    }, 50);
}

function flattenObject(obj, prefix = '') {
    return Object.keys(obj).reduce((acc, key) => {
        const fullKey = prefix ? `${prefix}.${key}` : key;
        if (typeof obj[key] === 'object' && obj[key] !== null && !Array.isArray(obj[key])) {
            Object.assign(acc, flattenObject(obj[key], fullKey));
        } else {
            acc[fullKey] = obj[key];
        }; 
        return acc;
    }, {});
};

function formatHtmlValue(key, value, mask) {
    if (typeof value === 'string') {
        if (mask) {
            value = value.replace(/^[A-Z0-9]{10}/, '***');
        }
        return '"' + value + '"';
    }
    if (typeof value === 'number' && key.endsWith('IP') && mask) {
        return '***';
    }
    return value;
}

function json2Html(data, mask) {
    let html = showClose()
    html += `
        <table>
            <tr>
                <th>Name</th>
                <th>Value</th>
            </tr>`;
    for (let [k, v] of Object.entries(flattenObject(data))) {
        if (!k) continue;
        html += `
                <tr>
                    <td>${k}</td>
                    <td>${formatHtmlValue(k, v, mask)}</td>
                </tr>`;
    };
    html += '</table>';
    document.getElementById('message').innerHTML = html;
    setTimeout(() => {
        document.getElementById('message').scrollIntoView();
    }, 50);
};

function showClose(){
    return `
        <div class="close">
            <a href="#" onclick='document.getElementById("message").innerHTML = "";'>Close</a> [<a href="#" onclick='document.getElementById("message").innerHTML = "";'>x</a>]
        </div>
    `;
}

function fetchJSONData (filename, output='pretty', mask='false') {
    fetch(filename)
        .then((response) => {
            if (!response.ok) {
                throw new Error(`Error fetching json data, response was not ok (filename=${filename})`);
            }
            return response.json();
        })
        .then((data) => {
            //console.log('DEBUG: fetchJSONData data =', data);
            if (output == 'pretty'  ) {
                prettyPrintJSON(data, mask);
            } else if (output =='html') {
                json2Html(data, mask);
            }
        })
        .catch((error) => {
            console.error("Error loading JSON file", error);
        });
}
