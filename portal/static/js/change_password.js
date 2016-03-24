$(document).ready(function() {

    $("#btnEditUser").bind("click", function() {
    	
    	var txtOldPassword = document.getElementById("txtOldPassword");
		if (empty_input(txtOldPassword.value)) {
			$.MsgBox.Alert("非法输入", "请输入原密码");
			return;
		}

		var txtNewPassword = document.getElementById('txtNewPassword');
		if (empty_input(txtNewPassword.value)) {
			$.MsgBox.Alert("非法输入", "请输入新密码");
			return;	
		}

		var txtPasswordComfirm = document.getElementById('txtPasswordComfirm');
		if (empty_input(txtPasswordComfirm.value)) {
			$.MsgBox.Alert("非法输入", "请输入新密码确认");
			return;	
		}

		if(txtPasswordComfirm.value != txtNewPassword.value){
				$.MsgBox.Alert("非法输入", "2次输入的新密码不一致");
			return;	
		}
	
		$.ajax({
			url:'/rest/api_update_password',
		    data: {
		    	"oldPassword": txtOldPassword.value,
		    	"newPassword": txtNewPassword.value
		    },
		    type: 'post',
		    cache: false,
		    dataType: 'json',
		    success: function(data) {
		    	if (data["error"] == 0) {
		    		$.MsgBox.Alert("更新密码", "密码修改成功， 请重新登陆", function() {
			    		window.location.href = "/logout";
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