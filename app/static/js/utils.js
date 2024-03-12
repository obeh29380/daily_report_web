
const cookie2json = (document) => {
    const cookies = document.cookie.split(';');
    json_cookies = {}
    cookies.forEach(function(cookie) {
        json_cookies[cookie.trim().split('=')[0]] = cookie.trim().split('=')[1];
    })
    return json_cookies;
};

const decodeJwt = (token) => {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    return JSON.parse(decodeURIComponent(escape(window.atob(base64))));
};

const callApi = (url, data, type) => {
    return $.ajax({
        url: url,
        type: type,
        dataType: 'json',
        contentType: 'application/json',
        data: JSON.stringify(data),
        timeout: 5000,
    })
};

const callApiFromForm = (url, data, type, headers) => {
    return $.ajax({
        url: url,
        type: type,
        dataType: 'json',
        data: data,
        headers: headers,
        timeout: 5000,
    })
};