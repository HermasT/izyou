$(document).ready(function() {
    $("#btn_update_teacher").bind("click", function() {
    	var tid = document.getElementById("update_teacher_id").value;
    	var name = document.getElementById("update_teacher_name").value;
    	if (empty_input(name)) {
			$.MsgBox.Alert("非法输入", "请输入用户名");
			return;
		}
		
		var gtype = document.getElementById("btn_update_teacher_gtype").value;
		if (empty_input(gtype)) {
			$.MsgBox.Alert("非法输入", "请选择科目类型");
			return;
		}

		var uprice = document.getElementById("update_teacher_uprice").value;
		// var desc = document.getElementById("update_teacher_desc");
		// var extend = document.getElementById("update_teacher_extend");
	    
		$.ajax({
			url:'/rest/update_teacher',
		    data: {
		    	"tid": tid,
		    	"name": name,
		    	"gtype": gtype,
		    	"uprice": uprice
		    	// "desc": desc.value,
		    	// "extend": extend.value
		    },
		    type: 'get',
		    cache: false,
		    dataType: 'json',
		    success: function(data) {
		    	if (data["error"] == 0) {
		    		$.MsgBox.Alert("更改教师信息", "您的请求已提交成功", function() {
			    		window.location.href = "/teacher";
			    	});
		    	} else {
		    		$.MsgBox.Alert("更改教师信息", data["cause"]);
		    	}
		    },
		    error: function() {
		        $.MsgBox.Alert("更改教师信息", "请求失败，请稍候重试");
		    }
		})
    });

})