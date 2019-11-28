/****************定位start************************* */
// 添加场景弹框
function addDingweiOpenEvent(e) {
    $('.alertMsg').text('')
    $('#add-dingwei').val('')
    $('#addDingweiHiddenInputId').val('')
    $('#addDingweiHiddenInputCode').val('')
	$('#addDingweiEvent').modal('show')
    $('#add-dingwei').focus()
}
// 保存 / 新增 品牌
function addDingweiCloseEvent(e) {
    /******************更新***********/
    let DingweiId = $('#addDingweiHiddenInputId').val()
    if (DingweiId){
        // 是更新信息
        let DingweiName = $('#add-dingwei').val().trim()
        if (DingweiName == ''){
            window.messageBox.show('请填写此项')
            return false
        }
        let csrfTokenValue = $("input[name='csrfmiddlewaretoken']").val()
        let data = {
            'csrfmiddlewaretoken':csrfTokenValue,
            'dingwei_id':DingweiId,
            'name':DingweiName,
        }
        ReloadAjax('post',data,"/basic/dingwei_add/",'addDingweiCloseEventBtn','addDingweiEvent') 

    }else{
        /******************新增 **********/
        let Dingwei = $('#add-dingwei').val().trim()
        if (Dingwei == ''){
            window.messageBox.show('请填写此项')
            return false
        }
        let data = {'dingwei':Dingwei}
        ReloadAjax('get',data,"/basic/dingwei_add/",'addDingweiCloseEventBtn','addDingweiEvent') 

    }

    
	
}
// 编辑品牌弹出框
function editDingweiClickEvent(event) { 
    let Dingwei_id = $(event).data('id')
    $.ajax({
        type: "get",
        url: "/basic/dingwei",
        data: {'dingwei_id':Dingwei_id},
        success: function (response) {
            if (response['code'] == '0'){
                let DingweiObj = JSON.parse(response['dingwei'])
                $('#addDingweiEvent').modal('show')
                $('#addDingweiHiddenInputId').val(DingweiObj['id'])
                $('#add-dingwei').val(DingweiObj['name'])
            }
        }
    });
}

// 删除品牌弹框
function deleteDingweiConfirmClickEvent(event) {  
    // 判断有没有关联关系　
    $('#deleteDingweiEvent').modal('show')
    let Dingwei_id = $(event).data('id')
    $.ajax({
        type: "post",
        url: "/basic/dingwei/",
        data: {'id':Dingwei_id},
        success: function (response) {
            if(response['code']=='0'){
                $('#addDingweiHiddenInputId').val(response['id'])
                $('#deleteDingweiCloseEventSaveButton').removeClass('disabled')
                $('#deleteDingweiCloseEventAlertMsg').text(response['msg'])
                // 可以删除
            }else if(response['code']!=='0'){
                // 不可删除
                $('#deleteDingweiCloseEventSaveButton').addClass('disabled')
                $('#deleteDingweiCloseEventAlertMsg').text(response['msg'])
            }
        },
        error:function(){
            $('#deleteDingweiCloseEventSaveButton').addClass('disabled')
            $('#deleteDingweiCloseEventAlertMsg').text("服务端错误，请联系管理员")
        }
    });
}

// 删除定位
function deleteDingweiCloseEvent(event) {  
    let Dingwei_id = $('#addDingweiHiddenInputId').val()
    // $('#deleteDingweiCloseEventAlertMsg').text('')
    if($('#deleteDingweiCloseEventSaveButton').hasClass('disabled')){
        return false
    }
    let data = {'id':Dingwei_id}
    ReloadAjax('delete',data,"/basic/dingwei/",'deleteDingweiCloseEventSaveButton','deleteDingweiEvent')

}
/*****************定位end********************* */