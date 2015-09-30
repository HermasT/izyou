$(document).ready(function() {

    $("#btn_create_course").bind("click", function() {
    	var name = document.getElementById("create_course_name");
    	if (empty_input(name.value)) {
			$.MsgBox.Alert("非法输入", "请输入课程名称");
			return;
		}

		var gtype = document.getElementById("btn_create_course_gtype");
		if (empty_input(gtype.value)) {
			$.MsgBox.Alert("非法输入", "请选择课程类型");
			return;
		}

		var startdate = document.getElementById("create_course_start");
		if (empty_input(startdate.value)) {
			$.MsgBox.Alert("非法输入", "请输入课程开始日期");
			return;
		}

		var enddate = document.getElementById("create_course_end");
		if (empty_input(enddate.value)) {
			$.MsgBox.Alert("非法输入", "请输入课程结束日期");
			return;
		}
		
		var teacher = document.getElementById("btn_create_course_teacher");
		if (empty_input(teacher.value)) {
			$.MsgBox.Alert("非法输入", "请选择授课讲师");
			return;
		}

		var count = document.getElementById("create_course_count");
		if (empty_input(count.value)) {
			$.MsgBox.Alert("非法输入", "请输入课程次数");
			return;
		}

		var fee = document.getElementById("create_course_fee");
		if (empty_input(fee.value)) {
			$.MsgBox.Alert("非法输入", "请输入课程收费金额");
			return;
		}

		var desc = document.getElementById("create_course_desc");
		var extend = document.getElementById("create_course_extend");
	    
		$.ajax({
			url:'/rest/create_course',
		    data: {
		    	"name": name.value,
		    	"gtype": gtype.value,
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
		    		$("#create_course_id").val(data["cid"]);
			    	$.MsgBox.Alert("新增课程", "您的请求已提交成功", function() {
			    		window.location.href = "/course";
			    	});
			    } else {
			    	$.MsgBox.Alert("新增课程", data["cause"]);
			    }
		    },
		    error: function() {
		        $.MsgBox.Alert("新增课程", "请求失败，请稍候重试");
		    }
		})
    });

})