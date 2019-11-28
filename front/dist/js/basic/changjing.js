/****************场景start************************* */
// 添加场景弹框
function addChangjingOpenEvent(e) {
    $('.alertMsg').text('')
    $('#add-changjing').val('')
    $('#addChangjingHiddenInputId').val('')
    $('#addChangjingHiddenInputCode').val('')
	$('#addChangjingEvent').modal('show')
    $('#add-changjing').focus()
}
// 保存 / 新增 品牌
function addChangjingCloseEvent(e) {
    /******************更新***********/
    let changjingId = $('#addChangjingHiddenInputId').val()
    if (changjingId){
        // 是更新信息
        let changjingName = $('#add-changjing').val().trim()
        if (changjingName == ''){
            window.messageBox.show('请填写此项')
            return false
        }
        let csrfTokenValue = $("input[name='csrfmiddlewaretoken']").val()
        let data = {
            'csrfmiddlewaretoken':csrfTokenValue,
            'changjing_id':changjingId,
            'name':changjingName,
        }
        ReloadAjax('post',data,"/basic/changjing_add/",'addChangjingCloseBtn','addChangjingEvent') 

    }else{

        /******************新增 **********/
        let changjing = $('#add-changjing').val().trim()
        if (changjing == ''){
            window.messageBox.show('请填写此项')
            return false
        }
        let data = {'changjing':changjing}
        ReloadAjax('get',data,"/basic/changjing_add/",'addChangjingCloseBtn','addChangjingEvent') 
 
    }

    
	
}
// 编辑品牌弹出框
function editChangjingClickEvent(event) { 
    let changjing_id = $(event).data('id')
    $('#addChangjingEvent').modal('show')
    $.ajax({
        type: "get",
        url: "/basic/changjing",
        data: {'changjing_id':changjing_id},
        success: function (response) {
            if (response['code'] == '0'){
                let changjingObj = JSON.parse(response['changjing'])
                $('#addChangjingHiddenInputId').val(changjingObj['id'])
                $('#add-changjing').val(changjingObj['name'])
            }
        }
    });
}

// 删除品牌弹框
function deleteChangjingConfirmClickEvent(event) {  
    // 判断有没有关联关系　
    $('#deleteChangjingEvent').modal('show')
    let changjing_id = $(event).data('id')
    $.ajax({
        type: "post",
        url: "/basic/changjing/",
        data: {'id':changjing_id},
        success: function (response) {
            if(response['code']=='0'){
                $('#addChangjingHiddenInputId').val(response['id'])
                $('#deleteChangjingCloseEventSaveButton').removeClass('disabled')
                $('#deleteChangjingCloseEventAlertMsg').text(response['msg'])
                // 可以删除
            }else if(response['code']!=='0'){
                // 不可删除
                $('#deleteChangjingCloseEventSaveButton').addClass('disabled')
                $('#deleteChangjingCloseEventAlertMsg').text(response['msg'])
            }
        },
        error:function(){
            $('#deleteChangjingCloseEventSaveButton').addClass('disabled')
            $('#deleteChangjingCloseEventAlertMsg').text("服务端错误，请联系管理员")

        }
    });
}

// 删除场景
function deleteChangjingCloseEvent(event) {  
    let changjing_id = $('#addChangjingHiddenInputId').val()
    if($('#deleteChangjingCloseEventSaveButton').hasClass('disabled')){
        return false
    }
    let data = {'id':changjing_id}
    ReloadAjax('delete',data,"/basic/changjing/",'deleteChangjingCloseEventSaveButton','deleteChangjingEvent') 

}
/*****************场景end********************* */