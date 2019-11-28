$(function () {
    $('#addSkuForm').bootstrapValidator({
        message: 'This value is not valid',
    　feedbackIcons: {
            valid: 'glyphicon glyphicon-ok',
            invalid: 'glyphicon glyphicon-remove',
            validating: 'glyphicon glyphicon-refresh'
        },
        fields: {
            'sku-code': {
                message: '编码不正确',
                validators: {
                    notEmpty: {
                        message: '编码不能为空'
                    },
                    regexp: {
                        regexp: /^\d{2}[1-9]$/,
                        message: '请正确输入sku编码 如001~099'
                    }
                }
            },
            'sku-name': {
                validators: {
                    notEmpty: {
                        message: 'sku名称不能为空'
                    }
                }
            },
            'sku-len': {
                validators: {
                    notEmpty: {
                        message: 'sku长度不能为空'
                    },
                    regexp:{
                        regexp: /^[0-9]+([.]{1}[0-9]+){0,1}$/,
                        message: '请正确输入'
                    }
                }
            },
            'sku-wid': {
                validators: {
                    notEmpty: {
                        message: 'sku宽度不能为空'
                    },
                    regexp:{
                        regexp: /^[0-9]+([.]{1}[0-9]+){0,1}$/,
                        message: '请正确输入'
                    }
                }
            },
            'sku-hei': {
                validators: {
                    notEmpty: {
                        message: 'sku高度不能为空'
                    },
                    regexp:{
                        regexp: /^[0-9]+([.]{1}[0-9]+){0,1}$/,
                        message: '请正确输入'
                    }
                }
            },
            'sku-wei': {
                validators: {
                    notEmpty: {
                        message: 'sku重量不能为空'
                    },
                    regexp:{
                        regexp: /^[0-9]+([.]{1}[0-9]+){0,1}$/,
                        message: '请正确输入'
                    }
                }
            },
            'price_jin': {
                validators: {
                    notEmpty: {
                        message: '进货价不能为空'
                    },
                    regexp:{
                        regexp: /^[0-9]+([.]{1}[0-9]{2}){0,1}$/,
                        message: '请正确输入价格,如下所示 1.81'
                    }
                }
            },
            'price_sale': {
                validators: {
                    regexp:{
                        regexp: /^[0-9]+([.]{1}[0-9]{2}){0,1}$/,
                        message: '请正确输入价格,如下所示 1.81'
                    }
                }
            },
            'price_pifa': {
                validators: {
                    regexp:{
                        regexp: /^[0-9]+([.]{1}[0-9]{2}){0,1}$/,
                        message: '请正确输入价格,如下所示 1.81'
                    }
                }
            },
            'quality': {
                validators: {
                    regexp:{
                        regexp: /^[0-9]+$/,
                        message: '请正确输入天数'
                    }
                }
            },
            'number_box': {
                validators: {
                    regexp:{
                        regexp: /^[0-9]+$/,
                        message: '请正确输入装箱数'
                    }
                }
            },
            'p_cycle': {
                validators: {
                    regexp:{
                        regexp: /^[0-9]+$/,
                        message: '请正确输入采购周期'
                    }
                }
            },
            'date_market': {
                // message : "计划开始日期必须输入",
                validators : {
                    date : {
                        format: 'YYYY/MM/DD',
                        message : "日期格式为2019/09/01"
                    }
                }
            },
            'sku-img': {
                validators: {
                    notEmpty: {
                        message: '请选择图片'
                    },
                    file: {
                        extension: 'png,jpg,jpeg',
                        type: 'image/png,image/jpg,image/jpeg',
                        message: '图片类型只能为 png,jpg,jpeg的一种'
                    }
                }
            },
        },
        submitHandler: function (validator, form, submitButton) {
            console.log("submit")
        }
    })
    .on('success.form.bv', function (e) { 
        //点击提交验证通过之后
        e.preventDefault();

    
        $('button[type="submit"]').removeAttr("disabled")

        // var flag = $('#form').data("bootstrapValidator").isValid();//校验合格
        var $form = $(e.target)
        // var bv = $form.data('bootstrapValidator')  data('bootstrapValidator')
        // data = $form.serialize()  用于不附带文件直接上传
        
        if($('#sku-img')[0].files[0]==undefined){
            window.messageBox.show('清上传sku图片')
            $('#sku-img').focus()
            return false
        }
        // 手动处理附带文件的ajax
        var formData = new FormData()
        let skuImageObj = $('#sku-img')[0]
        formData.append('sku-img', skuImageObj.files[0])
        formData.append('pid', $('#addSKUHiddenInput').val())
        formData.append('sku-code', $('#sku-code').val())
        formData.append('sku-name', $('#sku-name').val())
        formData.append('sku-len', $('#sku-len').val())
        formData.append('sku-wid', $('#sku-wid').val())
        formData.append('sku-hei', $('#sku-hei').val())
        formData.append('sku-wei', $('#sku-wei').val())
        formData.append('price_jin', $('#price_jin').val())
        let priceSale =  $('#price_sale').val()
        if (priceSale == ''){
            priceSale =0
        }
        let pricePifa =  $('#price_pifa').val()
        if (pricePifa == ''){
            pricePifa =0
        }
        formData.append('price_sale',priceSale)
        formData.append('price_pifa', pricePifa)
        formData.append('price_is_limit', $('#price_is_limit').find("option:selected").val())
        formData.append('sku_bar_code', $('#sku_bar_code').val())
        let priceQuality =  $('#quality').val()
        if (priceQuality == ''){
            priceQuality =0
        }
        let priceNumberBox =  $('#number_box').val()
        if (priceNumberBox == ''){
            priceNumberBox =0
        }

        formData.append('quality', priceQuality)
        formData.append('number_box',priceNumberBox)
        formData.append('p_cycle', $('#p_cycle').val())
        let dateMarket = $('#date_market').val()
        if(dateMarket == ''){
            // ,'2019/12/12'
            dateMarket = '2019/12/12'
        }
        formData.append('date_market', dateMarket)
        formData.append('desc', $('#desc').val())

        //
        // 设置按钮禁用
        // if($('#addSkuButtonconfirm').hasClass('disabled')){
        //     return false
        // }



        $('#addSkuButtonconfirm').addClass('disabled')
        $('#addSkuButtonconfirm').text('操作中...')
        $.ajax({
            type: "post",
            url: "/select/add_sku_detail/",
            data: formData,
            processData: false,  // tell jQuery not to process the data
            contentType: false,  // tell jQuery not to set contentType
            success: function (response) {
                console.log(response)
                $('#addSkuButtonconfirm').removeClass('disabled')
                $('#addSkuButtonconfirm').text('确定')
                if(response['code']=='0'){
                    window.messageBox.show('操作成功')
                    // 清空其他的信息  设置sku自动增一
                    clearAddInfoAfterSkuSuccess()
                    $('#addSkuButtonconfirm').removeClass('disabled')
                    $("#addSkuForm").bootstrapValidator('resetForm')
                    // $('#addSkuPhaseModal').modal('hide')
                    // window.location.reload()
                }else{
                    $('#addSkuButtonconfirm').removeClass('disabled')
                    window.messageBox.show(response['msg'])
                }
            },
            error:function (response) {  
                $('#addSkuButtonconfirm').removeClass('disabled')
                $('#addSkuButtonconfirm').text('确定')
                window.messageBox.show('服务端错误!请刷新重试或者联系管理员！')
            }
        });
    })
    // .on('error.form.bv', function (e) { //点击提交验证失败之后
    //     $('[type="submit"]').removeAttr("disabled");
    // });









/***************************************************** */
// 编辑sku信息的校验
$('#editSkuForm').bootstrapValidator({
    message: 'This value is not valid',
　feedbackIcons: {
        valid: 'glyphicon glyphicon-ok',
        invalid: 'glyphicon glyphicon-remove',
        validating: 'glyphicon glyphicon-refresh'
    },
    fields: {
        'edit-sku-name': {
            validators: {
                notEmpty: {
                    message: 'sku名称不能为空'
                }
            }
        },
        'edit-sku-len': {
            validators: {
                notEmpty: {
                    message: 'sku长度不能为空'
                },
                regexp:{
                    regexp: /^[0-9]+([.]{1}[0-9]+){0,1}$/,
                    message: '请正确输入'
                }
            }
        },
        'edit-sku-wid': {
            validators: {
                notEmpty: {
                    message: 'sku宽度不能为空'
                },
                regexp:{
                    regexp: /^[0-9]+([.]{1}[0-9]+){0,1}$/,
                    message: '请正确输入'
                }
            }
        },
        'edit-sku-hei': {
            validators: {
                notEmpty: {
                    message: 'sku高度不能为空'
                },
                regexp:{
                    regexp: /^[0-9]+([.]{1}[0-9]+){0,1}$/,
                    message: '请正确输入'
                }
            }
        },
        'edit-sku-wei': {
            validators: {
                notEmpty: {
                    message: 'sku重量不能为空'
                },
                regexp:{
                    regexp: /^[0-9]+([.]{1}[0-9]+){0,1}$/,
                    message: '请正确输入'
                }
            }
        },
        'edit-price_jin': {
            validators: {
                notEmpty: {
                    message: '进货价不能为空'
                },
                regexp:{
                    regexp: /^[0-9]+([.]{1}[0-9]{2}){0,1}$/,
                    message: '请正确输入价格,如下所示 1.81'
                }
            }
        },
        'edit-price_sale': {
            validators: {
                regexp:{
                    regexp: /^[0-9]+([.]{1}[0-9]{2}){0,1}$/,
                    message: '请正确输入价格,如下所示 1.81'
                }
            }
        },
        'edit-price_pifa': {
            validators: {
                regexp:{
                    regexp: /^[0-9]+([.]{1}[0-9]{2}){0,1}$/,
                    message: '请正确输入价格,如下所示 1.81'
                }
            }
        },
        'edit-quality': {
            validators: {
                regexp:{
                    regexp: /^[0-9]+$/,
                    message: '请正确输入天数'
                }
            }
        },
        'edit-number_box': {
            validators: {
                regexp:{
                    regexp: /^[0-9]+$/,
                    message: '请正确输入装箱数'
                }
            }
        },
        'edit-p_cycle': {
            validators: {
                regexp:{
                    regexp: /^[0-9]+$/,
                    message: '请正确输入采购周期'
                }
            }
        },
        'edit-date_market': {
            validators : {
                date : {
                    format: 'YYYY/MM/DD',
                    message : "日期格式为2019/09/01"
                }
            }
        },
        'edit-sku-img': {
            validators: {
                file: {
                    extension: 'png,jpg,jpeg',
                    type: 'image/png,image/jpg,image/jpeg',
                    message: '图片类型只能为 png,jpg,jpeg的一种'
                }
            }
        },
    },
    submitHandler: function (validator, form, submitButton) {
        console.log("submit")
    }
})
.on('success.form.bv', function (e) { //点击提交验证通过之后
    e.preventDefault();
    $('button[type="submit"]').removeAttr("disabled")

    // var flag = $('#form').data("bootstrapValidator").isValid();//校验合格
    // var $form = $(e.target)
    // var bv = $form.data('bootstrapValidator')  data('bootstrapValidator')
    // data = $form.serialize() //  用于不附带文件直接上传
    // 手动处理附带文件的ajax
    var formData = new FormData()
    let skuImageObj = $('#edit-sku-img')[0]
    formData.append('sku-img', skuImageObj.files[0])
    formData.append('sku-id', $('#edit-sku-hidden-id').val())
    formData.append('good-id', $('#currentGoodId').val())
    formData.append('sku-code', $('#edit-sku-code').val())
    formData.append('sku-name', $('#edit-sku-name').val())
    formData.append('sku-len', $('#edit-sku-len').val())
    formData.append('sku-wid', $('#edit-sku-wid').val())
    formData.append('sku-hei', $('#edit-sku-hei').val())
    formData.append('sku-wei', $('#edit-sku-wei').val())
    formData.append('price_jin', $('#edit-price_jin').val())
    let priceSale =  $('#edit-price_sale').val()
    if (priceSale == ''){
        priceSale =0
    }
    let pricePifa =  $('#edit-price_pifa').val()
    if (pricePifa == ''){
        pricePifa =0
    }
    formData.append('price_sale',priceSale)
    formData.append('price_pifa', pricePifa)
    formData.append('price_is_limit', $('#edit-price_is_limit').find("option:selected").val())
    formData.append('sku_bar_code', $('#edit-sku_bar_code').val())
    let priceQuality =  $('#edit-quality').val()
    if (priceQuality == ''){
        priceQuality =0
    }
    let priceNumberBox =  $('#edit-number_box').val()
    if (priceNumberBox == ''){
        priceNumberBox =0
    }

    formData.append('quality', priceQuality)
    formData.append('number_box',priceNumberBox)
    formData.append('p_cycle', $('#edit-p_cycle').val())
    let dateMarket =  $('#edit-date_market').val()
    if(dateMarket == ''){
        // ,'2019/12/12'
        dateMarket = '2019/12/12'
    }
    formData.append('date_market', dateMarket)
    formData.append('desc', $('#edit-desc').val())

    FileAjax('post',formData,"/select/edit_sku/",'EditSkuButtonconfirm','editSkuPhaseModal')


})// 编辑sku结束

});  // $()结束


/************************************************************************ */

// 添加sku弹出框
function addSkuPhaseBtnClick(event) {  
    let pid = $(event).data('id')
    $('#addSKUHiddenInput').val(pid)
    $('#addSkuPhaseModal').modal('show')


}

// 编辑sku弹出框
function editSkuPhaseBtnClick(event) {  
    let sid = $(event).data('sku-id')
    $('#edit-sku-hidden-id').val(sid)
    $('#editSkuPhaseModal').modal('show')


    $.ajax({
        type: "get",
        url: "/select/edit_sku/",
        data: {'sid':sid},
        success: function (response) {
            if(response['code']=='0'){
                skuObj = JSON.parse(response['sku'])[0]['fields']
                // 在页面插入信息
                $('#edit-sku-code').val(skuObj['sku_code'])
                $('#edit-sku-name').val(skuObj['sku_name'])
                $('#edit-sku-len').val(skuObj['length'])
                $('#edit-sku-wid').val(skuObj['width'])
                $('#edit-sku-hei').val(skuObj['height'])
                $('#edit-sku-wei').val(skuObj['weight'])
                $('#edit-price_jin').val(skuObj['price_jin']/100)
                $('#edit-price_sale').val(skuObj['price_sale']==0?0:skuObj['price_sale']/100)
                $('#edit-price_pifa').val(skuObj['price_pifa']==0?0:skuObj['price_pifa']/100)
                // $('#edit-price_pifa').val(getMoneyFloat(skuObj['']))
                // 是否限价
                $('#edit-price_is_limit').find("option[value='"+skuObj['p_cycle']+"price_is_limit']").attr("selected",true)
                $('#sku_bar_code').val(skuObj['sku_bar_code'])
                $('#edit-quality').val(skuObj['quality'])
                $('#edit-number_box').val(skuObj['number_box'])
                $('#edit-p_cycle').val(skuObj['p_cycle'])
                // 上市日期
                $('#edit-date_market').val(new Date(skuObj['date_market']).format('Y/m/d'))
                $('#edit-desc').val(skuObj['desc'])

                // sku_image: "1567754230.815296-19002-002.jpg"
              
            }else{
                window.messageBox.show(+response['msg'])
                
                // $('#edit-sku-code').siblings('.alertMsg').text('服务端错误，请刷新联系管理员')
            }
        },error:function(err){
            window.messageBox.show('服务端错误!请刷新重试或者联系管理员！')
            // $('#edit-sku-code').siblings('.alertMsg').text('服务端错误，请刷新重试')
        }
    });
}
// 删除sku弹出框
function deleteSkuPhaseBtnClick(event) {  
    let sid = $(event).data('sku-id')
    $('#deleteSkuHidden').val(sid)
    $('#modal_title_p_alert').text('是否确认删除该sku?')
    $('#productAddAlertmsgModal').modal('show')
}
// 删除确认框
function deleteSkuComfirmModalClose() {  

    if($('#deleteSkuButtonConfirm').hasClass('disabled')){
        return 
    }
    let skuId =    $('#deleteSkuHidden').val()
    let good_id =    $('#currentGoodId').val()
    let data = {'sku_id':skuId,'good_id':good_id}
    ReloadAjax('delete',data,"/select/edit_sku/",'deleteSkuButtonConfirm','productAddAlertmsgModal') 


    // $('#deleteSkuButtonConfirm').addClass('disabled')
    // $('#deleteSkuButtonConfirm').text('删除中...')
    // $.ajax({
    //     type: "delete",
    //     url: "/select/edit_sku/",
    //     data: {'sku_id':skuId,'good_id':good_id},
    //     success: function (response) {
    //         console.log(response)
    //         $('#deleteSkuButtonConfirm').removeClass('disabled')
    //         $('#deleteSkuButtonConfirm').text('删除')
    //         if(response['code']=='0'){
    //             $('#productAddAlertmsgModal').modal('hide')
    //             window.location.href = response['url']
    //         }else{
    //             window.messageBox.show(response['msg'])
    //         }
    //     },
    //     error:function (response) {  
    //         window.messageBox.show('服务端错误!请刷新重试或者联系管理员！')
    //     }
    // });
}



// 手动关闭新增sku事件
function addSkuCancelEvent() {  
    $('#addSkuPhaseModal').modal('hide')
    window.location.reload()
}


// 在sku新增成功后清空需要的地方信息  并且skucode自增1 
// 装箱数(个)采购周期(天)上市日期 不清空
function clearAddInfoAfterSkuSuccess() {  
    let resCode = skuAutoincreasementOne( $('#sku-code').val())
    $('#sku-code').val(resCode)
    $('#sku-name').focus()

    $('#sku-name').val('')
    $('#sku-len').val('')
    $('#sku-wid').val('')
    $('#sku-hei').val('')
    $('#sku-wei').val('')
    $('#price_jin').val('')
    $('#price_sale').val('')
    $('#price_pifa').val('')
    $('#sku_bar_code').val('')
    $('#quality').val('')
    $('#desc').val('')
    resetFileInput($('#sku-img'))


}

// 清空 input file 兼容ie
// file = $("#file_uploade");
function resetFileInput(file){
    // $('#sku-img')[0].files[0]  文件对象
    file.after(file.clone().val(""))
    file.remove()
}

// https://blog.csdn.net/ahou2468/article/details/78839861

// sku编码自动增长1
function skuAutoincreasementOne(skuCode) {  
    let intCode = parseInt(skuCode) + 1 
    let resCode = ''
    if((intCode + '').length == 1){
        resCode = '00'+intCode
    }else if((intCode + '').length == 2){
        resCode = '0'+intCode
    }else{
        resCode = intCode
    }

    return resCode
}

