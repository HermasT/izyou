$(document).ready(function() {

	$("#gender_male").bind("click", function() {
		$("#btn_add_teacher_gender").val("1");
		$("#btn_add_teacher_gender").html("男 <span class='caret'></span>");
    });

    $("#gender_female").bind("click", function() {
		$("#btn_add_teacher_gender").val("2");
		$("#btn_add_teacher_gender").html("女 <span class='caret'></span>");
    });

    $("#gtype_1").bind("click", function() {
		$("#btn_add_teacher_gtype").val("1");
		$("#btn_add_teacher_gtype").html("桥牌 <span class='caret'></span>");
    });

    $("#gtype_2").bind("click", function() {
		$("#btn_add_teacher_gtype").val("2");
		$("#btn_add_teacher_gtype").html("数独 <span class='caret'></span>");
    });

    $("#gtype_3").bind("click", function() {
		$("#btn_add_teacher_gtype").val("3");
		$("#btn_add_teacher_gtype").html("围棋 <span class='caret'></span>");
    });

    $("#btn_add_teacher").bind("click", function() {
    	var name = document.getElementById("add_teacher_name");
    	if (empty_input(name.value)) {
			$.MsgBox.Alert("非法输入", "请输入姓名");
			return;
		}

		var birth = document.getElementById("add_teacher_birth");
		if (empty_input(birth.value)) {
			$.MsgBox.Alert("非法输入", "请输入出生年月");
			return;
		}

		var gender = document.getElementById("btn_add_teacher_gender");
		if (empty_input(gender.value)) {
			$.MsgBox.Alert("非法输入", "请选择性别");
			return;
		}
		
		var gtype = document.getElementById("btn_add_teacher_gtype");
		if (empty_input(gtype.value)) {
			$.MsgBox.Alert("非法输入", "请选择科目类型");
			return;
		}

		var uprice = document.getElementById("add_teacher_uprice");
		var desc = document.getElementById("add_teacher_desc");
		var extend = document.getElementById("add_teacher_extend");
	    
		$.ajax({
			url:'/rest/add_teacher',
		    data: {
		    	"name": name.value,
		    	"birth": birth.value,
		    	"gender": gender.value,
		    	"gtype": gtype.value,
		    	"uprice": uprice.value,
		    	"desc": desc.value,
		    	"extend": extend.value
		    },
		    type: 'get',
		    cache: false,
		    dataType: 'json',
		    success: function(data) {
		    	if (data["error"] == 0) {
		    		$("#add_teacher_id").val(data["tid"]);
			    	$.MsgBox.Alert("新增讲师", "您的请求已提交成功", function() {
			    		window.location.href = "/teacher";
			    	});
		    	} else {
		    		$.MsgBox.Alert("新增讲师", data["error"]);
		    	}
		    },
		    error: function() {
		        $.MsgBox.Alert("新增讲师", "请求失败，请稍候重试");
		    }
		})
    });

})