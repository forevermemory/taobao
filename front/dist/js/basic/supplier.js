
/*****************供应商start********************** */
// 新增供应商弹出框
function addSuppilerOpenEvent(event) { 
    // 清空所有input的内容
    $('#addSupplierHiddenInputId').val('')

    $('#addSupplierCode').val('')
    $('#addSupplierName').val('')
    $('#addSupplierConcat').val('')
    $('#addSupplierPhone').val('')
    $('#addSupplierTelephone').val('')
    $('#addSupplierEmail').val('')
    $('#addSupplierAddress').val('')
    $('#addSupplierNote').val('')
    
    $('#addSuppilerEvent').modal('show')
    $('#addSupplierCode').focus()
}
// 清空所有弹框中的内容
function emptyAllSupplierAlertMsg() {  
    $('#addSupplierCode').siblings('.alertMsg').text('')
    $('#addSupplierName').siblings('.alertMsg').text('')
    $('#addSupplierConcat').siblings('.alertMsg').text('')
    $('#addSupplierPhone').siblings('.alertMsg').text('')
    $('#addSupplierTelephone').siblings('.alertMsg').text('')
    $('#addSupplierEmail').siblings('.alertMsg').text('')
    $('#addSupplierAddress').siblings('.alertMsg').text('')
    $('#addSupplierNote').siblings('.alertMsg').text('')
}


// 新增或者修改
function addSupplierCloseEvent(event) {
 /******************更新***********/
  
    let supplierId = $('#addSupplierHiddenInputId').val()
    let supplierCode = $('#addSupplierCode').val()
    let supplierName = $('#addSupplierName').val()
    let supplierConcat = $('#addSupplierConcat').val()
    let supplierPhone = $('#addSupplierPhone').val()
    let supplierTelephone = $('#addSupplierTelephone').val()
    let supplierEmail = $('#addSupplierEmail').val()
    let supplierAddress = $('#addSupplierAddress').val()
    let supplierNote = $('#addSupplierNote').val()
    let csrfTokenValue = $("input[name='csrfmiddlewaretoken']").val()
    if (supplierId){
        // 是更新信息   条件：编码，名称，地址必填。手机或固话必须填一个
        let allIsValid = checkAllConditionIsValid(supplierCode,supplierName,supplierConcat,supplierPhone,supplierTelephone,supplierEmail,supplierAddress,supplierNote)
        if (!allIsValid){
            return false
        }        
        let data = {
            'csrfmiddlewaretoken':csrfTokenValue,
            'id':supplierId,
            'code':PrefixIntegerZero(parseInt(supplierCode),4),
            'name':supplierName,
            'concat':supplierConcat,
            'phone':supplierPhone,
            'telephone':supplierTelephone,
            'email':supplierEmail,
            'address':supplierAddress,
            'note':supplierNote,
        }
        
        ReloadAjax('post',data,"/basic/supplier_add/",'addSupplierCloseBtn','addBrandEvent') 
            }else{
                
                /******************新增 **********/
                let allIsValid = checkAllConditionIsValid(supplierCode,supplierName,supplierConcat,supplierPhone,supplierTelephone,supplierEmail,supplierAddress,supplierNote)
                if (!allIsValid){
                    return false
                }    
                let data = {
            'csrfmiddlewaretoken':csrfTokenValue,
            'code':supplierCode,
            'name':supplierName,
            'concat':supplierConcat,
            'phone':supplierPhone,
            'telephone':supplierTelephone,
            'email':supplierEmail,
            'address':supplierAddress,
            'note':supplierNote,
        }
        ReloadAjax('get',data,"/basic/supplier_add/",'addSupplierCloseBtn','addBrandEvent') 
    }


}


// 检查所有的信息是否合理  主校验函数
function checkAllConditionIsValid(code,name,concat,phone,telephone,email,address,note) {
    // let res1 = checkAddSupplierBasicInfosIsValidUtil(code,name,address)
    // let res2 = checkPhoneOrTelephone(phone,telephone)
    // let res3 = checkEmailIsValid(email)
    if( checkAddSupplierBasicInfosIsValidUtil(code,name,address)){
        if(checkPhoneOrTelephone(phone,telephone)){
            if(checkEmailIsValid(email)){
                return true
            }else{
                return false
            }
        }else{
            return false
        }
    }else{
        return false
    }
}
// 电话或者手机必须有一个
function checkPhoneOrTelephone(phone,telephone) {  
    if(phone){
        // 填写了电话　同时判断手机是否合理
        return checkPhoneIsValid(phone)  && checkTelephoneIsValid(telephone)
    }else{
        // 未填写电话
        return checkTelephoneIsValidVersion2(telephone)
    }
}
// 校验编码，名称，地址必填。
function checkAddSupplierBasicInfosIsValidUtil(code,name,address) { 
    if (!(/[0-9]{4}/.test(code))){

        emptyAllSupplierAlertMsg()
        $("#addSupplierCode").focus();
        $("#addSupplierCode").siblings('.alertMsg').text('请正确填写编码,如0001-9999')
        return false
    }else{
        if(name.trim() == ''){
            emptyAllSupplierAlertMsg()
            $("#addSupplierName").focus();
            $("#addSupplierName").siblings('.alertMsg').text('请填写名称')
            return false
        }else{
            if(address.trim() == ''){
                emptyAllSupplierAlertMsg()
                $("#addSupplierAddress").focus();
                $("#addSupplierAddress").siblings('.alertMsg').text('请填写地址')
                return false
            }else{
                return true
            }
        }
    }
}
// 校验邮箱是否合理
function checkEmailIsValid(email) {  
    if (email){
        if(!(/^[\w.\-]+@(?:[a-z0-9]+(?:-[a-z0-9]+)*\.)+[a-z]{2,3}$/.test(email))){
            $("#addSupplierEmail").focus();
            emptyAllSupplierAlertMsg()
            $("#addSupplierEmail").siblings('.alertMsg').text('邮箱格式错误')
            return false;
        }else{
            return true
        }
    }else{
        return true
    }
}
// 校验电话是否合理
function checkPhoneIsValid(phone) {  
    if (phone){
        if(!(/^0\d{2,3}-?\d{7,8}$/.test(phone))){
            $("#addSupplierPhone").focus();
            emptyAllSupplierAlertMsg()
            $("#addSupplierPhone").siblings('.alertMsg').text('电话格式错误')
            return false;
        }else{
            return true
        }
    }else{
        emptyAllSupplierAlertMsg()
        $("#addSupplierPhone").siblings('.alertMsg').text('电话格式错误')
        return false
    }
}

// 校验手机是否合理
function checkTelephoneIsValid(telephone) {  
    if (telephone){
        if(!(/^1[3456789]\d{9}$/.test(telephone))){
            $("#addSupplierTelephone").focus();
            emptyAllSupplierAlertMsg()
            $("#addSupplierTelephone").siblings('.alertMsg').text('手机号码格式错误')
            return false;
        }else{
            return true
        }
    }else{
        return true
    }
}
// 校验手机是否合理
function checkTelephoneIsValidVersion2(telephone) {  
    if (telephone){
        if(!(/^1[3456789]\d{9}$/.test(telephone))){
            $("#addSupplierTelephone").focus();
            emptyAllSupplierAlertMsg()
            $("#addSupplierTelephone").siblings('.alertMsg').text('手机号码格式错误')
            return false;
        }else{
            return true
        }
    }else{
        emptyAllSupplierAlertMsg()
        $("#addSupplierTelephone").siblings('.alertMsg').text('手机号码格式错误')
        return false
    }
}

// 编辑弹出框
function editSuppilerClickEvent(event) { 
    let supplier_id = $(event).data('id')
    $('#addSuppilerEvent').modal('show')
    $.ajax({
        type: "get",
        url: "/basic/supplier/",
        data: {'supplier_id':supplier_id},
        success: function (response) {
            if (response['code'] == '0'){
                let supplierObj = JSON.parse(response['supplier'])
                emptyAllSupplierAlertMsg()
                $('#addSupplierHiddenInputId').val(supplierObj['id'])
                $('#addSupplierCode').val(supplierObj['code'])
                $('#addSupplierName').val(supplierObj['name'])
                $('#addSupplierConcat').val(supplierObj['concat'])
                $('#addSupplierPhone').val(supplierObj['phone'])
                $('#addSupplierTelephone').val(supplierObj['telephone'])
                $('#addSupplierEmail').val(supplierObj['email'])
                $('#addSupplierAddress').val(supplierObj['address'])
                $('#addSupplierNote').val(supplierObj['note'])

            }else{
                $('#addSupplierCode').siblings('.alertMsg').text(response['msg'])
            }
        }
    });
 }



 // 删除品牌弹框
function deleteSupplierConfirmClickEvent(event) {  
    // 判断有没有关联关系　
    $('#deleteSupplierCloseEventAlertMsg').text('')
    $('#deleteSupplierEvent').modal('show')
    let supplier_id = $(event).data('id')

    let data = {
        'id':supplier_id,
    }
    $.ajax({
        type: "put",
        url: "/basic/supplier/",
        data: data,
        success: function (response) {
            if(response['code']=='0'){
                $('#addSupplierHiddenInputId').val(response['id'])
                $('#deleteSupplierCloseEventSaveButton').removeClass('disabled')
                $('#deleteSupplierCloseEventAlertMsg').text(response['msg'])
                // 可以删除
            }else if(response['code']=='1'){
                // 不可删除
                $('#deleteSupplierCloseEventSaveButton').addClass('disabled')
                $('#deleteSupplierCloseEventAlertMsg').text(response['msg'])
            }
        },
        error:function(){
            $('#deleteSupplierCloseEventAlertMsg').text('服务端错误，请联系管理员')
            $('#deleteSupplierCloseEventSaveButton').removeClass('disabled')
            
        }
    });
}

function deleteSupplierCloseEvent(event) {  
    let supplier_id = $('#addSupplierHiddenInputId').val()
    if($('#deleteSupplierCloseEventSaveButton').hasClass('disabled')){
        return false
    }
    let data  = {'id':supplier_id}
    ReloadAjax('post',data,"/basic/supplier/",'deleteSupplierCloseEventSaveButton','deleteSupplierEvent') 

}



/****************供应商end******************** */