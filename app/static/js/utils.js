
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

const callApi = (url, data, type, headers) => {
    return $.ajax({
        url: url,
        type: type,
        headers: headers,
        dataType: 'json',
        contentType: 'application/json',
        data: JSON.stringify(data),
        timeout: 5000,
    })
};

const callApiFromForm = (url, data = {}, type = 'GET', headers = {}) => {
    return $.ajax({
        url: url,
        type: type,
        dataType: 'json',
        data: data,
        headers: headers,
        timeout: 5000,
    })
};


const togglePageButton = (current) => {

    const nav_home = document.querySelector('#nav-home');
    const nav_report = document.querySelector('#nav-report');
    const nav_report_summary = document.querySelector('#nav-report-summary');
    const nav_master = document.querySelector('#nav-master');

    nav_home.classList.remove('active');
    nav_report.classList.remove('active');
    nav_report_summary.classList.remove('active');
    nav_master.classList.remove('active');

    switch (location.pathname) {
        case '/home':
            nav_home.classList.toggle('active');
            break;
        case '/daily_report/top':
            nav_report.classList.toggle('active');
            break;
        case '/daily_report/summary':
            nav_report_summary.classList.toggle('active');
            break;
        case '/master/top':
            nav_master.classList.toggle('active');
            break;
        default:
      }

};
