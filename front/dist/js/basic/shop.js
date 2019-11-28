

// 新增店铺按钮
function addshopOpenEvent() {  
    $('#shopTitle').text('添加店铺')
    $('#addshopEvent').modal('show')
}

// 新增店铺保存事件
function addshopCloseEvent(event) {  
    if($('#addshopCloseBtn').hasClass('hidden')){
        return false
    }

    // 获取数据
    let shop_id = $('#addshopHiddenInputId').val()
    let code = $('#shopCode').val()
    let name = $('#shopName').val()
    let sub_name = $('#shopSubName').val()
    let link = $('#shopLink').val()
    let avenue_id = $('#shopAvenue').find("option:selected").val()
    let csrfTokenValue = $("input[name='csrfmiddlewaretoken']").val()
        
    // 校验
    if(!/[1-9][0-9]{2}/.test(code)){
        window.messageBox.show('请输入正确编码,如 100-999')
        return false
    }
    
    if(name.trim() == ''){
        window.messageBox.show('请输入正确店铺名称')
        return false
    }
    
    if(sub_name.trim() == ''){
        window.messageBox.show('请输入店铺简称')
        return false
    }else if(sub_name.trim().length>2){
        
        window.messageBox.show('店铺简称不能超过两个字符')
        return false
    }

    if(link.trim() == ''){
        window.messageBox.show('请输入链接')
        return false
    }

    if(shop_id){
        // 编辑店铺
        let data = {
            'csrfmiddlewaretoken':csrfTokenValue,
            'code':code,
            'name':name,
            'sub_name':sub_name,
            'link':link,
            'avenue_id':avenue_id,
            'shop_id':shop_id,
        }
        ReloadAjax('put',data,"/basic/shop/",'addshopCloseBtn','addshopEvent')
    }else{
        // 新增店铺
        let data = {
            'csrfmiddlewaretoken':csrfTokenValue,
            'code':code,
            'name':name,
            'sub_name':sub_name,
            'link':link,
            'avenue_id':avenue_id,
        }
        ReloadAjax('post',data,"/basic/shop/",'addshopCloseBtn','addshopEvent')
    }


}

// 编辑一个店铺
function editshopClickEvent(event) {  
    $('#addshopHiddenInputId').val($(event).data('id'))
    $('#shopCode').val($(event).data('code'))
    $('#shopName').val($(event).data('name'))
    $('#shopSubName').val($(event).data('sub_name'))
    $('#shopLink').val($(event).data('link'))
    let avenue_id = $(event).data('avenue')
    for (let k = 0; k < $('#shopAvenue option').length; k++) {
        if($($('#shopAvenue option')[k]).val() == avenue_id){
            $($('#shopAvenue option')[k]).prop('selected','true')
        }
    }

    $('#shopTitle').text('编辑店铺')
    $('#addshopEvent').modal('show')

}
// window.messageBox.show('操作成功')