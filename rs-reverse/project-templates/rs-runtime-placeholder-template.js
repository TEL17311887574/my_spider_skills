require('./mod')

// 占位符区域：rs_reverse.js 只保留模板，不写入真实动态挑战源码。
// 自动采集得到的 payload 只替换到临时 runtime 文件。
'challenge_payload_bootstrap';
'challenge_payload_runner';

function get_cookie() {
    return document.cookie;
}

console.log(get_cookie());
