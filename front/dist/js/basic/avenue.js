

// 新增渠道按钮
function addavenueOpenEvent() {  
    $('#avenueTitle').text('添加渠道')
    $('#addavenueEvent').modal('show')
}

// 新增渠道保存事件
function addavenueCloseEvent(event) {  
    if($('#addavenueCloseBtn').hasClass('hidden')){
        return false
    }

    // 获取数据
    let a_id = $('#addavenueHiddenInputId').val()
    let code = $('#avenueCode').val()
    let name = $('#avenueName').val()
    let csrfTokenValue = $("input[name='csrfmiddlewaretoken']").val()
        
    // 校验
    if(!/[1-9][0-9]/.test(code)){
        window.messageBox.show('请输入正确编码,如 10-99')
        return false
    }
    
    if(name.trim() == ''){
        window.messageBox.show('请输入正确渠道名称')
        return false
    }
    if(a_id){
        // 编辑渠道
        let data = {
            'csrfmiddlewaretoken':csrfTokenValue,
            'code':code,
            'name':name,
            'a_id':a_id,
        }
        ReloadAjax('put',data,"/basic/avenue/",'addavenueCloseBtn','addavenueEvent')
    }else{
        // 新增渠道
        let data = {
            'csrfmiddlewaretoken':csrfTokenValue,
            'code':code,
            'name':name
        }
        ReloadAjax('post',data,"/basic/avenue/",'addavenueCloseBtn','addavenueEvent')
    }


}

// 编辑一个渠道
function editavenueClickEvent(event) {  
    $('#addavenueHiddenInputId').val($(event).data('id'))
    $('#avenueCode').val($(event).data('code'))
    $('#avenueName').val($(event).data('name'))

    $('#avenueTitle').text('编辑渠道')
    $('#addavenueEvent').modal('show')

}
// window.messageBox.show('操作成功')