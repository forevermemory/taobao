/*****************员工start********************** */
// 前面补0
function PrefixIntegerZero(num, length) {
    return (Array(length).join('0') + num).slice(-length);
}


function IsArrayEqual(a, b) {
    // 判断数组的长度
    if (a.length !== b.length) {
        return false
    } else {
        // 循环遍历数组的值进行比较
        for (let i = 0; i < a.length; i++) {
            if (a[i] !== b[i]) {
                return false
            }
        }
        return true
    }
}
// 新增用户弹出框
// 清空所有input的内容
function addUserOpenEvent(event) { 

    $('#addUserHiddenInputId').val('')

    $('#addUserCode').val('')
    $('#addUserUsername').val('')
    $('#addUserName').val('')
    $('#addUserPassword').val('')
    $('#addUserTelephone').val('')
    $('#addUserXueli').val('')
    $('#addUserRole').val('')
    $('#addUserAddress').val('')
    $('#addUserAddressNow').val('')
    $('#addUserEmail').val('')
    $('#addUserUsername').attr('readonly',false)
    $('#addUserPassword').parent().parent().removeClass('hidden')
    emptyAllUserAlertMsg()
    $('#addUserEvent').modal('show')
    $('#addUserCode').focus()


}
// 清空所有弹框中的内容
function emptyAllUserAlertMsg() {  
    $('#addUserCode').siblings('.alertMsg').text('')
    $('#addUserUsername').siblings('.alertMsg').text('')
    $('#addUserName').siblings('.alertMsg').text('')
    $('#addUserPassword').siblings('.alertMsg').text('')
    $('#addUserTelephone').siblings('.alertMsg').text('')
    $('#addUserXueli').siblings('.alertMsg').text('')
    $('#addUserRole').siblings('.alertMsg').text('')
    $('#addUserAddress').siblings('.alertMsg').text('')
    $('#addUserAddressNow').siblings('.alertMsg').text('')
    $('#addUserEmail').siblings('.alertMsg').text('')
}
// 测试多级对话框
// $(document).ready(function () {
    // $('.modal').on('show.bs.modal', function (event) {
    //     var idx = $('.modal:visible').length;
    //     $(this).css('z-index', 1040 + (10 * idx));
    // });
    // $('.modal').on('shown.bs.modal', function (event) {
    //     var idx = ($('.modal:visible').length) - 1; // raise backdrop after animation.
    //     $('.modal-backdrop').not('.stacked').css('z-index', 1039 + (10 * idx));
    //     $('.modal-backdrop').not('.stacked').addClass('stacked');
    // });
// });


// 二级对话框关闭事件
function ShowSubModalButton(event) {  
    $('#modal_title_role_alert').text('')
 
    if(($("input[type='checkbox']:checked").length) == '0'){
        $('#modal_title_role_alert').text('必须选择一种角色')
        return false
    }
    let ids = ''
    let values = ''
    $.each($("input[type='checkbox']:checked"), function (indexInArray, valueOfElement) { 
         ids += $(valueOfElement).data('id')+','
         values += $(valueOfElement).data('desc')+' '

    });
    $('#ChooseUserRoleModelHiddenInput').val(ids)
    $('#addUserRole').val(values)
    emptyAllUserAlertMsg()
    $('#ShowSubModalChooseRole').modal('hide')
}

// 弹出二级选择角色对话框
function ShowSubModal(event) {  
    let rawRoleValue = $('#addUserRole').val()
    let rawRoleIds = $('#EditRawRoleIds').val()

    $('#ShowSubModalChooseRole').modal('show')
    $("#checkBoxModal").empty()
    $('#modal_title_role').text('选择员工角色')
    $('#ShowSubModalChooseRole').css('z-index',1060)
    $.ajax({
        type: "get",
        url: '/select/add_one_type/',
        data: {'kind':'role'},
        success: function (response) {
            if(response['code'] == undefined){
                let roles = JSON.parse(response['roles'])
                roles.forEach(element => {
                    $("#checkBoxModal").append(`
                    <div class="form-check checkbox">
                        <input class="form-check-input"  data-name="`+element.fields.name+`" id="checkItem`+element.pk+`" type="checkbox" value="" data-id="`+element.pk+`" data-desc="`+element.fields.desc+`" data-role="1">
                        <label class="form-check-label" for="checkItem`+element.pk+`">`+element.fields.desc+`</label>
                    </div>`)
                    // 遍历checkbox 动态加上是否选中状态
                });
                $.each($('input[type="checkbox"][data-role="1"]'), function (indexInArray, valueOfElement) { 
                    let roleId = $(valueOfElement).data('id')
                    console.log() // ["1", "3", ""]
                    let rawRoleIdsArray = rawRoleIds.split(',')
                    for (let k = 0; k < rawRoleIdsArray.length; k++) {
                        if(parseInt(rawRoleIdsArray[k])>0){
                            if(parseInt(roleId)==parseInt(rawRoleIdsArray[k])){
                                $(valueOfElement).attr('checked',true)
                            }
                        }
                    }
                });
            }
        }
    });

}



// 新增或者修改
//https://www.nuoweb.com/program/1157.html 二级对话框
function addUserCloseEvent(event) {
    /******************更新***********/
    if($('#saveUserButton').hasClass('disabled')){
        return 
    }
    let UserHiddenInputId = $('#addUserHiddenInputId').val()
    let UserCode = $('#addUserCode').val()
    let UserUsername = $('#addUserUsername').val()
    let UserName = $('#addUserName').val()
    let UserPassword = $('#addUserPassword').val()
    let UserTelephone = $('#addUserTelephone').val()
    let UserXueli = $('#addUserXueli').val()
    let UserRole = $('#ChooseUserRoleModelHiddenInput').val()
    let UserAddress = $('#addUserAddress').val()
    let UserAddressNow = $('#addUserAddressNow').val()
    let UserEmail = $('#addUserEmail').val()
    let csrfTokenValue = $("input[name='csrfmiddlewaretoken']").val()
    if (UserHiddenInputId){
        // 是更新信息   条件：编码，名称，地址必填。手机或固话必须填一个
        let allIsValid = checkUpdateUserIsValid(UserCode,UserName,UserTelephone,UserXueli,UserRole,UserAddress,UserAddressNow,UserEmail)
        if (!allIsValid){
            return false
        }        
        // 判断角色是否变更 EditRawRoleIds  新的 UserRole
        let isChangeRole = IsArrayEqual(UserRole,$('#EditRawRoleIds').val())
        let data = {
            'csrfmiddlewaretoken':csrfTokenValue,
            'user_id':UserHiddenInputId,
            'role_ids':UserRole,
            'code':PrefixIntegerZero(parseInt(UserCode),4),
            'name':UserName,
            'xueli':UserXueli,
            'telephone':UserTelephone,
            'email':UserEmail,
            'address':UserAddress,
            'address_now':UserAddressNow,
            'is_change_role':!isChangeRole
        }
        ReloadAjax('post',data,"/basic/cpmuser_add/",'saveUserButton','addUserEvent') 
    }else{

        /******************新增 **********/
        let allIsValid = checkCreateUserIsValid(UserCode,UserUsername,UserName,UserPassword,UserTelephone,UserXueli,UserRole,UserAddress,UserAddressNow,UserEmail)
        if (!allIsValid){
            return false
        }    

        let data = {
            'username':UserUsername,
            'password':UserPassword,
            'role_ids':UserRole,
            'code':UserCode,
            'name':UserName,
            'xueli':UserXueli,
            'telephone':UserTelephone,
            'email':UserEmail,
            'address':UserAddress,
            'address_now':UserAddressNow,
        }
        ReloadAjax('get',data,"/basic/cpmuser_add/",'saveUserButton','addUserEvent') 
    }


}


// 重写校验编码
function reCheckUsercode(userCode) {  
    let codeArray = userCode.split('')
    if(codeArray.length != 4){
        return false
    }
    codeArray.forEach(element => {
        if(!(/[0-9]/.test(element))){
            return false
        }
    })

    return true

}

// 校验编码，名称，地址必填。
function checkUpdateUserIsValid(UserCode,UserName,UserTelephone,UserXueli,UserRole,UserAddress,UserAddressNow,UserEmail) { 
    if(!reCheckUsercode(UserCode)){
        
        emptyAllUserAlertMsg()
        $("#addUserCode").focus()
        $("#addUserCode").siblings('.alertMsg').text('请输入正确的编码,如0001-9999')
        return false
    }else{
        if(UserName.trim() == ''){
            emptyAllUserAlertMsg()
            $("#addUserName").focus();
            $("#addUserName").siblings('.alertMsg').text('请填写姓名')
            return false
        }else{
            if(!checkTelephoneIsValid(UserTelephone)){
                emptyAllUserAlertMsg()
                $("#addUserTelephone").focus();
                $("#addUserTelephone").siblings('.alertMsg').text('请正确填写手机号码')
                return false
            }else{
                if(UserXueli.trim() == ''){
                    emptyAllUserAlertMsg()
                    $("#addUserXueli").focus();
                    $("#addUserXueli").siblings('.alertMsg').text('请填写学历')
                    return false
                }else{
                    if(UserRole.trim() == ''){
                        emptyAllUserAlertMsg()
                        $("#addUserRole").focus();
                        $("#addUserRole").siblings('.alertMsg').text('请选择角色')
                        return false
                    }else{
                        if(UserAddress.trim() == ''){
                            emptyAllUserAlertMsg()
                            $("#addUserAddress").focus();
                            $("#addUserAddress").siblings('.alertMsg').text('请填写联系地址')
                            return false
                        }else{
                            if(UserAddressNow.trim() == ''){
                                emptyAllUserAlertMsg()
                                $("#addUserAddressNow").focus();
                                $("#addUserAddressNow").siblings('.alertMsg').text('请填写常住地')
                                return false
                            }else{
                                if(!checkEmailIsValid(UserEmail)){
                                    emptyAllUserAlertMsg()
                                    $("#addUserEmail").focus();
                                    $("#addUserEmail").siblings('.alertMsg').text('请填写正确的邮箱')
                                    return false
                                }else{
                                    // ok
                                    return true
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
function checkCreateUserIsValid(UserCode,UserUsername,UserName,UserPassword,UserTelephone,UserXueli,UserRole,UserAddress,UserAddressNow,UserEmail) { 
    if(!reCheckUsercode(UserCode)){
        emptyAllUserAlertMsg()
        $("#addUserCode").focus();
        $("#addUserCode").siblings('.alertMsg').text('请输入正确的编码,如0001-9999')
        return false
    }else{
        if(UserUsername.trim() == ''){
            emptyAllUserAlertMsg()
            $("#addUserUsername").focus();
            $("#addUserUsername").siblings('.alertMsg').text('请填写账号')
            return false
        }else{
            if(UserName.trim() == ''){
                emptyAllUserAlertMsg()
                $("#addUserName").focus();
                $("#addUserName").siblings('.alertMsg').text('请填写姓名')
                return false
            }else{
                if(UserPassword.trim().length < 6){
                    emptyAllUserAlertMsg()
                    $("#addUserPassword").focus();
                    $("#addUserPassword").siblings('.alertMsg').text('密码长度需要大于六位')
                    return false
                }else{
                    if(!checkTelephoneIsValid(UserTelephone)){
                        emptyAllUserAlertMsg()
                        $("#addUserTelephone").focus();
                        $("#addUserTelephone").siblings('.alertMsg').text('请正确填写手机号码')
                        return false
                    }else{
                        if(UserXueli.trim() == ''){
                            emptyAllUserAlertMsg()
                            $("#addUserXueli").focus();
                            $("#addUserXueli").siblings('.alertMsg').text('请填写学历')
                            return false
                        }else{
                            if(UserRole.trim() == ''){
                                emptyAllUserAlertMsg()
                                $("#addUserRole").focus();
                                $("#addUserRole").siblings('.alertMsg').text('请选择角色')
                                return false
                            }else{
                                if(UserAddress.trim() == ''){
                                    emptyAllUserAlertMsg()
                                    $("#addUserAddress").focus();
                                    $("#addUserAddress").siblings('.alertMsg').text('请填写联系地址')
                                    return false
                                }else{
                                    if(UserAddressNow.trim() == ''){
                                        emptyAllUserAlertMsg()
                                        $("#addUserAddressNow").focus();
                                        $("#addUserAddressNow").siblings('.alertMsg').text('请填写常住地')
                                        return false
                                    }else{
                                        if(!checkEmailIsValid(UserEmail)){
                                            emptyAllUserAlertMsg()
                                            $("#addUserEmail").focus();
                                            $("#addUserEmail").siblings('.alertMsg').text('请填写正确的邮箱')
                                            return false
                                        }else{
                                            // ok
                                            return true
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
// 校验邮箱是否合理
function checkEmailIsValid(email) {  
    if (email){
        if(!(/^[\w.\-]+@(?:[a-z0-9]+(?:-[a-z0-9]+)*\.)+[a-z]{2,3}$/.test(email))){
            $("#addUserEmail").focus();
            emptyAllUserAlertMsg()
            $("#addUserEmail").siblings('.alertMsg').text('邮箱格式错误')
            return false;
        }else{
            return true
        }
    }else{
        return true
    }
}


// 校验手机是否合理
function checkTelephoneIsValid(telephone) {  
    if (telephone){
        if(!(/^1[3456789]\d{9}$/.test(telephone))){
            $("#addUserTelephone").focus();
            emptyAllUserAlertMsg()
            $("#addUserTelephone").siblings('.alertMsg').text('手机号码格式错误')
            return false;
        }else{
            return true
        }
    }else{
        emptyAllUserAlertMsg()
        $("#addUserTelephone").siblings('.alertMsg').text('手机号码格式错误')
        return false
    }
}

// 编辑弹出框
function editUserClickEvent(event) { 
    let User_id = $(event).data('id')
    $.ajax({
        type: "get",
        url: "/basic/cpmuser/",
        data: {'user_id':User_id},
        success: function (response) {
            console.log(response)
            if (response['code'] == '0'){
                let UserObj = response['user']
                $('#addUserEvent').modal('show')
                emptyAllUserAlertMsg()
                $('#addUserHiddenInputId').val(UserObj['id'])
                $('#addUserCode').val(UserObj['code'])
                $('#addUserUsername').val(UserObj['username'])
                $('#addUserUsername').attr('readonly',true)
                $('#addUserPassword').parent().parent().addClass('hidden')
                
                let rolesTemp = ''
                let rolesIds = ''
                UserObj['roles'].forEach(element => {
                    rolesTemp+= element.desc +','
                    rolesIds+= element.id +','
                });
                $('#addUserRole').val(rolesTemp)
                $('#EditRawRoleIds').val(rolesIds)
                $('#ChooseUserRoleModelHiddenInput').val(rolesIds)
                $('#addUserRole').data('role_ids',rolesIds)

                $('#addUserName').val(UserObj['name'])
                $('#addUserXueli').val(UserObj['xueli'])
                $('#addUserPhone').val(UserObj['phone'])
                $('#addUserTelephone').val(UserObj['telephone'])
                $('#addUserEmail').val(UserObj['email'])
                $('#addUserAddress').val(UserObj['address'])
                $('#addUserAddressNow').val(UserObj['address_now'])

            }else{
                $('#addUserEvent').modal('show')
                $('#addUserCode').siblings('.alertMsg').text(response['msg'])
            }
        }
    });
 }




/****************员工end******************** */
// 删除员工弹出框
function deleteUserConfirmClickEvent(event) {  
    
    $('#deleteUserEvent').modal('show')
}

// 删除员工弹出框关闭
function deleteUserCloseEvent(event) {  
    $('#deleteUserEvent').modal('hide')
}
// 修改密码
function changeUserPasswordClickEvent(event) {  
    $('#changePasswordHiddenInput').val($(event).data('id'))
    $('#changeUserPasswordEvent').modal('show')
    $('#ChangeNewPassword').focus()
}
// 
function changeUserPasswordCloseEvent(event) {  

    if($('#changeUserpasswordCloseEventSaveButton').hasClass('disabled')){
        return 
    }

    let newPassword = $('#ChangeNewPassword').val()
    if(newPassword.trim().length < 6){
        emptyAllUserAlertMsg()
        $("#ChangeNewPassword").focus();
        $("#changeUserPasswordCloseEventAlertMsg").text('密码长度需要大于六位')
        return false
    }
    // 获取用户id
    let userId = $('#changePasswordHiddenInput').val()
    let data = {'user_id':userId,'new_password':newPassword}
    ReloadAjax('post',data,"/basic/cpmuser/",'changeUserpasswordCloseEventSaveButton','changeUserPasswordEvent') 


}
/****************员工end******************** */




