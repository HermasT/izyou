var create_table = null;

$(document).ready(function () {
    var count = document.getElementById("add_detail_course_count").value;
    var table_content_data = []
    for (var i = 0; i < count; i++) {
        var content_line = [];
        content_line[0] = i + 1;
        content_line[1] = '';
        content_line[2] = '';
        table_content_data[i] = content_line;
    }
    create_table = $("#add_detail_table").editTable({
        data: table_content_data,
        headerCols: ['课次', '主题', '内容概要'],
        first_row: false,
        has_add_icon: true,
        validate_field: function (col_id, value, col_type, element) {
            if (col_type === 'text') {
                $(element).css({
                    'background-color': '#fff'
                });
                if (value == null || value == "") {
                    $(element).css({
                        'background-color': '#DB4A39'
                    });
                    return false;
                }
            }
            return true;
        },
    });

    $("#add_course_detail").bind("click", function () {
        var cid = document.getElementById("add_detail_course_id").value;
        var name = document.getElementById("add_detail_course_name").value;
        var count = document.getElementById("add_detail_course_count").value;
        if (empty_input(cid)) {
            $.MsgBox.Alert("非法输入", "非法访问");
            return;
        }

        var contents = create_table.getJsonData();
        if (JSON.parse(contents).length != count) {
            $.MsgBox.Alert("非法输入", "正确配置应当是" + count + "次课时");
            return;
        }
        if (!create_table.isValidated()) {
            $.MsgBox.Alert("非法输入", "课程内容输入不合法");
            return;
        }

        $.ajax({
            url: '/rest/add_course_detail',
            data: {"cid":cid, "contents": JSON.stringify(content_array_to_json_array(contents))},
            type: 'post',
            cache: false,
            dataType: 'json',
            success: function (data) {
                if (data["error"] == 0) {
                    $.MsgBox.Alert("添加课程内容", "您的请求已提交成功，请添加班次", function () {
                        window.location.href = "/add_course_schedule?cid=" + cid + "&name=" + name;
                    });
                } else {
                    $.MsgBox.Alert("添加课程班次", data["cause"]);
                }
            },
            error: function () {
                $.MsgBox.Alert("添加课程内容", "请求失败，请稍候重试");
            }
        })
    });
})