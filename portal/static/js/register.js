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
    console.log(phone);
    console.log(pattern.test(phone));
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

$(document).ready(function() {
	$("#cb_terms").change(function(){
		if ($("#cb_terms").is(":checked")) {
			$("#btn_register").removeClass('disabled');
		} else {
			$("#btn_register").addClass('disabled');
		}
	});

	$("#btn_register").bind("click", function() {
		var username = document.getElementById("iusername");
	    var password = document.getElementById("ipassword");
	    var password2 = document.getElementById("ipassword2");
	    var phone = document.getElementById("iphone");
	    var email = document.getElementById("iemail");
	    var name = document.getElementById("iname");

		if (!is_valid_username(username.value)) {
			$.MsgBox.Alert("非法输入", "用户名不合法");
	    } else if (!is_valid_password(password.value)) {
	    	$.MsgBox.Alert("非法输入", "登录密码不合法");
	    } else if (password.value != password2.value) {
	    	$.MsgBox.Alert("非法输入", "两次输入的密码不一致");
	    } else if (!is_valid_phone(phone.value)) {
	    	$.MsgBox.Alert("非法输入", "手机号码不合法");
	    } else if (!is_valid_email(email.value)) {
	    	$.MsgBox.Alert("非法输入", "邮箱地址不合法");
	    } else {
	    	$.ajax({
				url:'/rest/register',
			    data: {"username" :username.value, "password": password.value, 
			    	"phone": phone.value, "email": email.value, "name": name.value},
			    type: 'get',
			    cache: false,
			    dataType: 'json',
			    success: function(data) {
			    	if (data["error"] > 0) {
			    		$.MsgBox.Alert("注册失败", data["cause"]);
			    	} else {
			    		window.location.href = "/login";
			    	}
			    },
			    error: function() {
			        $.MsgBox.Alert("注册失败", "操作失败，请稍候重试");
			    }
			})
	    }
    });
})