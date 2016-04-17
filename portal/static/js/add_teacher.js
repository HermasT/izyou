$(document).ready(function() {
    $("#btn_add_teacher").bind("click", function() {
    	var name = document.getElementById("add_teacher_name").value;
    	if (empty_input(name)) {
			$.MsgBox.Alert("非法输入", "请选择注册的用户名");
			return;
		}

		var gtype = document.getElementById("btn_add_teacher_gtype").value;
		if (empty_input(gtype)) {
			$.MsgBox.Alert("非法输入", "请选择科目类型");
			return;
		}

		var uprice = document.getElementById("add_teacher_uprice").value;
	    
		$.ajax({
			url:'/rest/add_teacher',
		    data: {
		    	"name": name,
		    	"gtype": gtype,
		    	"uprice": uprice
		    },
		    type: 'get',
		    cache: false,
		    dataType: 'json',
		    success: function(data) {
		    	if (data["error"] == 0) {
		    		$("#add_teacher_id").val(data["tid"]);
			    	$.MsgBox.Alert("新增教师", "您的请求已提交成功", function() {
			    		window.location.href = "/teacher";
			    	});
		    	} else {
		    		$.MsgBox.Alert("新增教师", data["cause"]);
		    	}
		    },
		    error: function() {
		        $.MsgBox.Alert("新增教师", "请求失败，请稍候重试");
		    }
		})
    });
})