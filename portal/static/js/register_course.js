$(document).ready(function() {

    $("#btn_register_course").bind("click", function() {
    	var cid = document.getElementById("register_course_id");
    	if (empty_input(cid.value)) {
			$.MsgBox.Alert("非法输入", "请输入课程编号");
			return;
		}

    	var username = document.getElementById("register_user_name");
    	if (empty_input(username.value)) {
			$.MsgBox.Alert("非法输入", "请输入报名的用户名");
			return;
		}

    	var paytype = document.getElementById("btn_register_course_paytype");
		if (empty_input(paytype.value)) {
			$.MsgBox.Alert("非法输入", "请选择支付类型");
			return;
		}

		var extend = document.getElementById("register_course_extend");

		console.log("register_course")
	    
		$.ajax({
			url:'/rest/register_course',
		    data: {
		    	"cid": cid.value,
		    	"username": username.value,
		    	"paytype": paytype.value,
		    	"extend": extend.value
		    },
		    type: 'get',
		    cache: false,
		    dataType: 'json',
		    success: function(data) {
		    	$.MsgBox.Alert("课程报名", "您的请求已提交成功", function() {
		    		// window.location.href = "/course";
		    	});
		    },
		    error: function() {
		        $.MsgBox.Alert("课程报名", "请求失败，请稍候重试");
		    }
		})
    });

})