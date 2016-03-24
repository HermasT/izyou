$(document).ready(function() {

    $("#btnEditUser").bind("click", function() {
    	var cid = document.getElementById("update_course_id");
    	var name = document.getElementById("update_course_name");

    	var txtEmail = document.getElementById("txtEmail");
		if (empty_input(txtEmail.value)) {
			$.MsgBox.Alert("非法输入", "请选输入邮箱地址");
			return;
		}

		if(txtEmail.value.length > 64){
			$.MsgBox.Alert("非法输入", "输入邮箱地址过长");
			return;	
		}

	   if (!is_valid_email(txtEmail.value)) {
	    	$.MsgBox.Alert("非法输入", "邮箱地址不合法");
			return;
	    }

	  	var txtMobile = document.getElementById("txtMobile");
		if (empty_input(txtMobile.value)) {
			$.MsgBox.Alert("非法输入", "请选输入手机号码");
			return;
		}

		if(txtMobile.value.length > 11){
			$.MsgBox.Alert("非法输入", "输入手机号码不得超过11位");
			return;	
		}

		if (!is_valid_phone(txtMobile.value)) {
	    	$.MsgBox.Alert("非法输入", "手机号码不合法");
	    	return;
	    } 

		var txtName = document.getElementById("txtName");
		if (empty_input(txtName.value)) {
			$.MsgBox.Alert("非法输入", "请选输入姓名");
			return;
		}

		if(txtName.value.length > 32){
			$.MsgBox.Alert("非法输入", "输入姓名过长");
			return;	
		}

		var btn_user_gender = document.getElementById("btn_user_gender");
		var txtBirth = document.getElementById("txtBirth");
	
		$.ajax({
			url:'/rest/api_update_userprofile',
		    data: {
		    	"name": txtName.value,
		    	"email": txtEmail.value,
		    	"phone": txtMobile.value,
		    	"birth": txtBirth.value,
		    	"gender": btn_user_gender.value
		    },
		    type: 'post',
		    cache: false,
		    dataType: 'json',
		    success: function(data) {
		    	if (data["error"] == 0) {
		    		$.MsgBox.Alert("更新用户信息", "您的请求已提交成功", function() {
			    		window.location.href = "/userprofile?username=" + $('#hidden_userName').val();
			    	});
		    	} else {
		    		$.MsgBox.Alert("更改课程信息", data["cause"]);
		    	}
		    },
		    error: function() {
		        $.MsgBox.Alert("更改课程信息", "请求失败，请稍候重试");
		    }
		})
    });

})