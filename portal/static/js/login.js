$(document).ready(function() {
	$("#blogin").bind("click", function() {
		var username = document.getElementById("iusername");
	    var password = document.getElementById("ipassword");
	    var next = document.getElementById("inext");

		if (empty_input(username.value)) {
			$.MsgBox.Alert("非法输入", "用户名为空");
	    } else if (empty_input(password.value)) {
	    	$.MsgBox.Alert("非法输入", "密码为空");
	    } else {
	    	$.ajax({
				url:'/rest/login',
			    data: {"username" :username.value, "password": password.value, "next":next.value},
			    type: 'get',
			    cache: false,
			    dataType: 'json',
			    success: function(data) {
			    	console.log(data)
			    	if (data["error"] > 0) {
			    		$.MsgBox.Alert("登录失败", data["cause"]);
			    	} else {
			    		var next = data["next"];
			    		if (next == null || next == "") {
			    			window.location.href = "/after_login";
			    		} else {
			    			window.location.href = "/after_login?next=" + next;
			    		}
			    	}
			    },
			    error: function() {
			        $.MsgBox.Alert("登录失败", "请求失败，请稍候重试");
			    }
			})
	    }
    });

    $("#bregister").bind("click", function() {
    	window.location.href = "/register";
    });
})