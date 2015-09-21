$(document).ready(function() {

    $("#btn_update_course").bind("click", function() {
    	var cid = document.getElementById("update_course_id");
    	var name = document.getElementById("update_course_name");

    	var status = document.getElementById("btn_update_course_status");
		if (empty_input(status.value)) {
			$.MsgBox.Alert("非法输入", "请选择课程状态");
			return;
		}

		var startdate = document.getElementById("update_course_start");
		if (empty_input(startdate.value)) {
			$.MsgBox.Alert("非法输入", "请输入课程开始日期");
			return;
		}

		var enddate = document.getElementById("update_course_end");
		if (empty_input(enddate.value)) {
			$.MsgBox.Alert("非法输入", "请输入课程结束日期");
			return;
		}
		
		var teacher = document.getElementById("btn_update_course_teacher");
		if (empty_input(teacher.value)) {
			$.MsgBox.Alert("非法输入", "请选择授课讲师");
			return;
		}

		var count = document.getElementById("update_course_count");
		if (empty_input(count.value)) {
			$.MsgBox.Alert("非法输入", "请输入课程次数");
			return;
		}

		var fee = document.getElementById("update_course_fee");
		if (empty_input(fee.value)) {
			$.MsgBox.Alert("非法输入", "请输入课程收费金额");
			return;
		}

		var desc = document.getElementById("update_course_desc");
		var extend = document.getElementById("update_course_extend");
	    
		$.ajax({
			url:'/rest/update_course',
		    data: {
		    	"cid": cid.value,
		    	"name": name.value,
		    	"status": status.value,
		    	"start": startdate.value,
		    	"end": enddate.value,
		    	"teacher": teacher.value,
		    	"count": count.value,
		    	"fee": fee.value,
		    	"desc": desc.value,
		    	"extend": extend.value
		    },
		    type: 'get',
		    cache: false,
		    dataType: 'json',
		    success: function(data) {
		    	if (data["error"] == 0) {
		    		$.MsgBox.Alert("更改课程信息", "您的请求已提交成功", function() {
			    		window.location.href = "/course";
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