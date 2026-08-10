// 本地环境检测入口。
// challenge_payload_bootstrap.js / challenge_payload_runner.js 由用户手动固定，
// 用于吐环境、观察缺失环境和补环境调试。缺失时不要自动生成占位样本。
require('./mod')
require('./challenge_payload_bootstrap')
require('./challenge_payload_runner')

function get_cookie() {
    return document.cookie;
}

console.log(get_cookie());
