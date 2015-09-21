$(document).ready(function() {

	$("#gender_male").bind("click", function() {
		$("#btn_update_teacher_gender").val("1");
		$("#btn_update_teacher_gender").html("男 <span class='caret'></span>");
    });

    $("#gender_female").bind("click", function() {
		$("#btn_update_teacher_gender").val("2");
		$("#btn_update_teacher_gender").html("女 <span class='caret'></span>");
    });

    $("#gtype_1").bind("click", function() {
		$("#btn_update_teacher_gtype").val("1");
		$("#btn_update_teacher_gtype").html("桥牌 <span class='caret'></span>");
    });

    $("#gtype_2").bind("click", function() {
		$("#btn_update_teacher_gtype").val("2");
		$("#btn_update_teacher_gtype").html("数独 <span class='caret'></span>");
    });

    $("#gtype_3").bind("click", function() {
		$("#btn_update_teacher_gtype").val("3");
		$("#btn_update_teacher_gtype").html("围棋 <span class='caret'></span>");
    });

    $("#btn_update_teacher").bind("click", function() {
    	var tid = document.getElementById("update_teacher_id");
    	var name = document.getElementById("update_teacher_name");
    	if (empty_input(name.value)) {
			$.MsgBox.Alert("非法输入", "请输入姓名");
			return;
		}

		var birth = document.getElementById("update_teacher_birth");
		if (empty_input(birth.value)) {
			$.MsgBox.Alert("非法输入", "请输入出生年月");
			return;
		}

		var gender = document.getElementById("btn_update_teacher_gender");
		if (empty_input(gender.value)) {
			$.MsgBox.Alert("非法输入", "请选择性别");
			return;
		}
		
		var gtype = document.getElementById("btn_update_teacher_gtype");
		if (empty_input(gtype.value)) {
			$.MsgBox.Alert("非法输入", "请选择科目类型");
			return;
		}

		var uprice = document.getElementById("update_teacher_uprice");
		var desc = document.getElementById("update_teacher_desc");
		var extend = document.getElementById("update_teacher_extend");
	    
		$.ajax({
			url:'/rest/update_teacher',
		    data: {
		    	"tid": tid.value,
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
		    	$.MsgBox.Alert("更改讲师信息", "您的请求已提交成功", function() {
		    		window.location.href = "/teacher";
		    	});
		    },
		    error: function() {
		        $.MsgBox.Alert("更改讲师信息", "请求失败，请稍候重试");
		    }
		})
    });

})