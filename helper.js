// Solis JS helper functions

function lastUpdated(date) {
    let now = Date.now();
    let time = new Date(date).getTime();
    let sec = (now - time) / 1000 || -1;
    let text;
    if (sec > 3600) {
        text = (sec/60/60).toFixed(0) + ' hours ago';
    } else if (sec > 60) { 
        text = (sec/60).toFixed(0) + ' minutes ago';
    } else { 
        text = sec.toFixed(0) + ' seconds ago';
    }
    if (sec < 0)  {
        //console.log('DEBUG: lastUpdated - time not in sync (sec < 0)')
        text += ' (‼️time desync) ';
    }
    document.getElementById('updated').innerText = text;
}

function jsonType(jsonString) {
    jsonString = jsonString.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    return jsonString.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
      let type = 'number';
      if (/^"/.test(match)) {
          if (/:$/.test(match)) {
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
    const r = results;
    // if this is array, iterate elements
    if (Array.isArray(obj)) {
        //console.log("DEBUG: jsonSearch - ARRAY LENGTH ", obj.length);
        for (const element of obj) {
            // console.log("DEBUG: jsonSearch -- searching array element: ");
            jsonSearch(element, searchKey, r);
        }
    // if this is object, iterate keys
    } else if (typeof obj === "object") {
        for (let key in obj) {
            let value = obj[key];
            // add matching key to results
            if (key === searchKey) {
                obj[key] = replaceValue;
                // Optional: unbox array of one
                if (Array.isArray(value) && value.length === 1) value = value[0];
                r.push(value);
            }
            const keyType = typeof obj[key];
            //console.log("DEBUG: jsonSearch - key: ", key, " / type: ", keyType);
            // look inside objects
            if (keyType === "object") {
                //console.log("DEBUG: jsonSearch - searching inside object: ", key);
                jsonSearch(value, searchKey, r);
            }
        }
    }
  //return r;
  return obj
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

function json2Html(data, mask) {
    let html = showClose()
    html += `
        <table>
            <tr>
                <th></th>
                <th>Value</th>
            </tr>`;
    for (let [k, v] of Object.entries(flattenObject(data))) { 
        if (k) {
            if (typeof v == 'string') {
                if (mask) {
                    v = v.replace(/^[A-Z0-9]{10}/, '***');
                };
                v = '"' + v + '"'
            }
            if (typeof v == 'number') {
                if (k.endsWith('IP')) { 
                    if (mask) {
                        v = '***';
                    }
                }
            }
            html += `
                <tr>
                    <td>${k}</td>
                    <td>${v}</td>
                </tr>`;
        };
    };
    html += '</table>';
    document.getElementById('message').innerHTML = html;
    setTimeout(() => {
        document.getElementById('message').scrollIntoView();
    }, 50);
};

function showClose(){
    return `
        <div class="close" style="float:right;position:fixed;top:10px;right:30px;">
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
