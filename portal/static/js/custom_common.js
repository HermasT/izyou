// 空值
function empty_input(value) {
	return (value == null || value == "");
}

// 合法的用户名  数字、字母、下划线组成的6-30位字符串
function is_valid_username(username) {
    var pattern = /^(\w){6,30}$/;
    if (pattern.test(username)) {
        return true;
    } else {
        return false;
    }
}

// 合法的密码  数字、字母、下划线组成的6-18位字符串
function is_valid_password(password) {
    var pattern=/^(\w){6,18}$/;
    if (pattern.test(password)) {
        return true;
    } else {
        return false;
    }
}

// 合法的手机号（弱校验） 1xxbbbbcccc
function is_valid_phone(phone) {
    var pattern = /^1\d{10}$/;
    if (pattern.test(phone)) {
        return true;
    } else {
        return false;
    }
}

// 合法的邮箱地址  xxx@yyy.zzz
function is_valid_email(email) {
    var pattern=/^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/;
    if (pattern.test(email)) {
        return true;
    } else {
        return false;
    }
}

// 合法的验证码  4位以上全是数字
function is_valid_code(code) {
    var pattern = /[0-9]{4}[0-9]*$/;
    if (pattern.test(code)) {
        return true;
    } else {
        return false;
    }
}

function content_array_to_json_array(contents) {
    var content_json_array = [];
　　 $.each(JSON.parse(contents), function(i, content){
        var content_json = {};
        content_json.index = content[0];
        content_json.title = content[1];
        content_json.detail = content[2];
        content_json_array.push(content_json);
　　 });
    return content_json_array;
}

function schedule_array_to_json_array(schedules) {
    var schedule_json_array = [];
　　 $.each(JSON.parse(schedules), function(i, schedule){
        var schedule_json = {};
        schedule_json.index = schedule[0];
        schedule_json.time = schedule[1];
        schedule_json.rid = schedule[2];
        schedule_json.mteacher = schedule[3];
        schedule_json.bteacher = schedule[4];
        schedule_json_array.push(schedule_json);
　　 });
    return schedule_json_array;
}

(function ($) {
    $.MsgBox = {
        Alert: function (title, msg) {
            GenerateHtml("alert", title, msg);
            btnOk();
            btnNo();
        },
        Alert: function (title, msg, callback) {
            GenerateHtml("alert", title, msg);
            btnOk(callback);
            btnNo();
        },
        Confirm: function (title, msg, callback) {
            GenerateHtml("confirm", title, msg);
            btnOk(callback);
            btnNo();
        }
    }

    var GenerateHtml = function (type, title, msg) {

        var _html = '<div id="mb_box"></div><div id="mb_con" textAlign="center"><span id="mb_tit">' + title + '</span>';
        _html += '<div id="mb_msg">' + msg + '</div><div id="mb_btnbox">';

        if (type == "alert") {
            _html += '<input id="mb_btn_ok" type="button" value="确定" />';
        } else if (type == "confirm") {
            _html += '<input id="mb_btn_ok" type="button" value="确定" />';
            _html += '<input id="mb_btn_no" type="button" value="取消" />';
        }
        _html += '</div></div>';

        $("body").append(_html);
        GenerateCss();
    }

    var GenerateCss = function () {

        $("#mb_box").css({ width: '100%', height: '100%', zIndex: '99999', position: 'fixed',
            filter: 'Alpha(opacity=60)', backgroundColor: 'black', top: '0', left: '0', opacity: '0.6'
        });

        $("#mb_con").css({ zIndex: '999999', width: '300px', position: 'fixed',
            backgroundColor: 'White', borderRadius: '3px'
        });

        $("#mb_tit").css({ display: 'block', fontSize: '15px', color: '#444', padding: '10px 15px',
            backgroundColor: '#DDD', borderRadius: '3px 3px 0 0', textAlign: 'center',
            borderBottom: '1px solid #009BFE', fontWeight: 'bold'
        });

        $("#mb_msg").css({ padding: '20px', lineHeight: '20px',
            borderBottom: '1px dashed #DDD', fontSize: '13px'
        });

        $("#mb_ico").css({ display: 'block', position: 'absolute', right: '10px', top: '9px',
            border: '1px solid Gray', width: '18px', height: '18px', textAlign: 'center',
            lineHeight: '16px', cursor: 'pointer', borderRadius: '12px', fontFamily: '微软雅黑'
        });

        $("#mb_btnbox").css({ margin: '15px 0 15px 0', textAlign: 'center' });
        $("#mb_btn_ok,#mb_btn_no").css({ width: '100px', height: '30px', color: 'white', border: 'none', borderRadius:'3px' });
        $("#mb_btn_ok").css({ backgroundColor: '#168bbb' });
        $("#mb_btn_no").css({ backgroundColor: 'gray', marginLeft: '20px' });


        var _widht = document.documentElement.clientWidth;
        var _height = document.documentElement.clientHeight;

        var boxWidth = $("#mb_con").width();
        var boxHeight = $("#mb_con").height();

        $("#mb_con").css({ top: (_height - boxHeight) / 2 + "px", left: (_widht - boxWidth) / 2 + "px" });
    }

    var btnOk = function (callback) {
        $("#mb_btn_ok").click(function() {
            $("#mb_box, #mb_con").remove();
            if (typeof(callback) == 'function') {
                callback();
            }
        });
    }

    var btnNo = function () {
        $("#mb_btn_no, #mb_ico").click(function() {
            $("#mb_box, #mb_con").remove();
        });
    }
})(jQuery)

$(document).ready(function() {
    $("#title_btn_login").bind("click", function() {
        window.location.href = "/login";
    });

    $("#title_btn_logout").bind("click", function() {
        window.location.href = "/logout";
    });

    $("#title_btn_register").bind("click", function() {
        window.location.href = "/register";
    });
})