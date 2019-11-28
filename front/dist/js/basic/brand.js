
/****************品牌start************************* */
// 添加品牌弹框
function addBrandOpenEvent(e) {
    $('.alertMsg').text('')
    $('#add-brand').val('')
    $('#addBrandHiddenInputId').val('')
    $('#addBrandHiddenInputCode').val('')
	$('#addBrandEvent').modal('show')
    $('#add-brand').focus()
}
// 保存 / 新增 品牌
function addBrandCloseEvent(e) {
    /******************更新***********/
    let brandId = $('#addBrandHiddenInputId').val()
    if (brandId){
        // 是更新信息
        let brandName = $('#add-brand').val().trim()
        if (brandName == ''){
            window.messageBox.show('请填写品牌')
            return false
        }
        let csrfTokenValue = $("input[name='csrfmiddlewaretoken']").val()

        let data =  {'csrfmiddlewaretoken':csrfTokenValue,'brand_id':brandId,'name':brandName,}
        ReloadAjax('post',data,"/basic/brand_add/",'addBrandCloseBtn','addBrandEvent') 

    }else{

        /******************新增 **********/
        let brand = $('#add-brand').val().trim()
        if (brand == ''){
            window.messageBox.show('请填写品牌')
            return false
        }
        let data = {'brand':brand}
        ReloadAjax('get',data,"/basic/brand_add/",'addBrandCloseBtn','addBrandEvent') 

    }

    
	
}
// 编辑品牌弹出框
function editBrandClickEvent(event) { 
    let brand_id = $(event).data('id')
    $.ajax({
        type: "get",
        url: "/basic/brand",
        data: {'brand_id':brand_id},
        success: function (response) {
            if (response['code'] == '0'){
                let brandObj = JSON.parse(response['brand'])
                $('#addBrandEvent').modal('show')
                $('#addBrandHiddenInputId').val(brandObj['id'])
                $('#addBrandHiddenInputCode').val(brandObj['code'])
                $('#add-brand').val(brandObj['name'])
            }
        }
    });
}

// 删除品牌弹框
function deleteBrandConfirmClickEvent(event) {  
    // 判断有没有关联关系　
    $('#deleteBrandEvent').modal('show')
    let brand_id = $(event).data('id')
    $.ajax({
        type: "post",
        url: "/basic/brand/",
        data: {'id':brand_id},
        success: function (response) {
            if(response['code']=='0'){
                $('#addBrandHiddenInputId').val(response['id'])
                $('#deleteBrandCloseEventSaveButton').removeClass('disabled')
                $('#deleteBrandCloseEventAlertMsg').text('可以删除')
                // 可以删除
            }else if(response['code'] == '1'){
                // 不可删除
                $('#deleteBrandCloseEventSaveButton').addClass('disabled')
                $('#deleteBrandCloseEventAlertMsg').text(response['msg'])
            }
        },
        error:function(){
            $('#deleteBrandCloseEventSaveButton').addClass('disabled')
            $('#deleteBrandCloseEventAlertMsg').text('服务端错误,请联系管理员')
        }
    });
}

// 删除品牌 点击确认删除
function deleteBrandCloseEvent(event) {  
    let brand_id = $('#addBrandHiddenInputId').val()
    if($('#deleteSupplierCloseEventSaveButton').hasClass('disabled')){
        return false
    }

    let data = {'id':brand_id}
    ReloadAjax('delete',data,"/basic/brand/",'deleteSupplierCloseEventSaveButton','deleteBrandEvent') 

}
/*****************品牌end********************* */