$(function () {  


})


// 新增分组打开modal
function addGroupModalOpenEvent() {  
    $('#groupTitle').text('添加分组')
    $('#addGroupModal').modal('show')
    $('#groupName').focus()
}

// 新增渠道保存事件
function addgroupCloseEvent(event) {  
    if($('#addgroupCloseBtn').hasClass('hidden')){
        return false
    }

    // 获取数据
    let group_id = $('#addgroupHiddenInputId').val()
    let name = $('#groupName').val()
    let csrfTokenValue = $("input[name='csrfmiddlewaretoken']").val()
        
    // 校验
    if(name.trim() == ''){
        window.messageBox.show('请输入正确分组名称')
        return false
    }
    if(group_id){
        // 编辑渠道
        let data = {
            'csrfmiddlewaretoken':csrfTokenValue,
            'name':name,
            'group_id':group_id,
        }
        $('#addgroupCloseBtn').text('操作中..')
        $('#addgroupCloseBtn').addClass('disabled')
        $.ajax({
            type: "get",
            url: "/auth/group_edit/",
            data: data,
            success: function (response) {
                console.log(response)
                $('#addgroupCloseBtn').removeClass('disabled')
                $('#addgroupCloseBtn').text('保存')
                if(response['code']=='0'){
                    window.messageBox.show('操作成功')
                    $('#addgroupEvent').modal('hide')
                    window.location.reload()
                }else{
                    window.messageBox.show(response['msg'])
                }
            },
            error:function (response) {  
                $('#addgroupCloseBtn').removeClass('disabled')
                $('#addgroupCloseBtn').text('保存')
                window.messageBox.show('服务端错误!请刷新重试或者联系管理员！')
            }
        });

    }else{
        // 新增渠道
        let data = {
            'csrfmiddlewaretoken':csrfTokenValue,
            'name':name
        }
        $('#addgroupCloseBtn').text('操作中..')
        $('#addgroupCloseBtn').addClass('disabled')
        $.ajax({
            type: "post",
            url: "/auth/group/",
            data: data,
            success: function (response) {
                console.log(response)
                $('#addgroupCloseBtn').removeClass('disabled')
                $('#addgroupCloseBtn').text('保存')
                if(response['code']=='0'){
                    window.messageBox.show('操作成功')
                    $('#addgroupEvent').modal('hide')
                    window.location.reload()
                }else{
                    window.messageBox.show(response['msg'])
                }
            },
            error:function (response) {  
                $('#addgroupCloseBtn').removeClass('disabled')
                $('#addgroupCloseBtn').text('保存')
                window.messageBox.show('服务端错误!请刷新重试或者联系管理员！')
            }
        });
    }


}

// 编辑一个渠道
function editGroup(event) {  
    $('#addgroupHiddenInputId').val($(event).data('id'))
    $('#groupName').val($(event).data('name'))

    $('#groupTitle').text('编辑分组')
    $('#addGroupModal').modal('show')

}