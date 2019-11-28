$(document).ready(function($) {
	// 初始化模态对话框


	// 初始化双向选择框
	$('#multiselect').multiselect();
	//　初始化日期选择控件
	$('#pl-end').cxCalendar()
    $('#pl-start').cxCalendar()
    

  

});




function PrefixIntegerZero(num, length) {

    return (Array(length).join('0') + parseInt(num)).slice(-length)
}
/************************************************** */


// 回车搜索品类
$('#p-pinlei').keyup(function (event) { 
    if(event.keyCode == 13){
        sessionStorage.removeItem('liandongPathIdArray')
        let enter_query = $(event.target).val()
        if(enter_query.trim() == ''){
            return
        }
        var isAddCate = $('#isAddCate').val()
        var data = {}
        isAddCate == '1' ? data['is_cate'] = 1 : data['is_cate'] = ''
        $.ajax({
            type: "get",
            url: "/select/cpm_category/",
            data: {
                'enter_query':enter_query,
                'is_cate':isAddCate,
            },
            success: function (response) {
                let items = JSON.parse(response['items'])
                // console.log(items)   // 会有多个种类  不处理  默认显示第一个
                if(items.length == 0){
                    window.messageBox.show('未找到该品类,请尝试其他关键词')
                    return
                }
                // 分割path_id
                let pathIdArray = items[0].fields.pathid.split(',')
                let pathLength = pathIdArray.length
                // $('#p-pinlei').data('path_id_length',pathLength)
                // $('#p-pinlei').data('path_ids',items[0].fields.pathid)
                sessionStorage.setItem('liandongPathIdArray',JSON.stringify(pathIdArray))
                // 一级需要跳转
                firstLiandongAutoScroll(pathIdArray[0])
                $('#'+pathIdArray[0]).click()
             
            }
        });
    }
});



// 一级自动跳转
function firstLiandongAutoScroll(firstId) {  
    // let firstCategory = JSON.parse(sessionStorage.getItem('firstCategory'))
    $.each($('.qrm-lev-1 li'), function (index, value) { 
        if($(value).attr('id') == firstId){
            // $(value).siblings().removeClass('active')
            $(value).addClass('active')
            var sTop = (index-1)*40
            var nowScrollTop=$('.qrm-lev-1').scrollTop();//当前已经滚动了多少
            $('.qrm-border1').stop(true).animate({"scrollTop":sTop+nowScrollTop},400);
            return
        }
    });

}





// 新增产品时候选择品类时候内容变化自动跳转事件
function addProductPeileiChange(event) {  
    let inputVal = $(event).val()
    if(inputVal == ''){
        return false
    }
    let firstCategory = JSON.parse(sessionStorage.getItem('firstCategory'))
    firstCategory.forEach(element => {
        if(element.fields.name.indexOf(inputVal)!=-1){
            // console.log(element.fields.name)
            $.each($('.qrm-lev-1 li'), function (index, value) { 
                if($(value).data('first-id') == element.pk){
                    $(value).addClass('active').siblings().removeClass('active')
                    // var sTop=$('.qrm-lev-1').offset().top
                    var sTop = (index-1)*40
                    var nowScrollTop=$('.qrm-lev-1').scrollTop();//当前已经滚动了多少
                    $('.qrm-border').stop(true).animate({"scrollTop":sTop+nowScrollTop},400);
                }
            });
           return
        }
    });
}

/************************************************** */
/************************************************** */
//  双向选择对话框 modal 打开获取数据事件


// 双向选择对话框 modal关闭事件
// function ProductAddoneModelCloseButton(params) {
//     let kind = $('#ProductAddoneModelHiddenInput').val()
//     let DestVal = ''
//     let DestText = ''
//     $("#multiselect_to option").each((i,item)=> {
//         DestVal += $(item).val()+','
//         DestText += $(item).text() + ','
//     })
//     $('input[name="'+kind+'"]').val(DestText)
//     $('input[name="'+kind+'"]').data('id',DestVal)
// 	$('#ProductAddoneModel').modal('hide')
// }


/******************************************** */
// 删除一个产品弹出框判断
function deleteOneSelectProduct(event) {  
    // 判断有没有关联关系　
    $('#deleteOneSelectProductModal').modal('show')
    // let brand_id = $(event).data('id')
    // $.ajax({
    //     type: "get",
    //     url: "/basic/brand_confirm/",
    //     data: {'id':brand_id},
    //     success: function (response) {
    //         if(response['code']==0){
    //             $('#addBrandHiddenInputId').val(response['id'])
    //             $('#deleteBrandCloseEventSaveButton').attr('disabled',false)
    //             $('#deleteBrandCloseEventAlertMsg').text(response['msg'])
    //             // 可以删除
    //         }else if(response['code'==1]){
    //             // 不可删除
    //             $('#deleteBrandCloseEventSaveButton').attr('disabled',true)
    //             $('#deleteBrandCloseEventAlertMsg').text(response['msg'])
    //         }
    //     }
    // });
}

function confirmDeleteSelectProductCloseButton(event) {  
    // let brand_id = $('#addBrandHiddenInputId').val()
    $('#deleteSelectProductCloseEventAlertMsg').text()
    // console.log(brand_id)
    // $.ajax({
    //     type: "get",
    //     url: "/basic/brand_del/",
    //     data: {'id':brand_id},
    //     success: function (response) {
    //         if (response['code'] == undefined){
    //             // 删除成功
    //             $('#deleteBrandEvent').modal('hide')
    //             window.location.reload()
    //         }else if(response['code'] == 0){
    //             //删除失败
    //             $('#deleteBrandCloseEventAlertMsg').text(response['msg'])
    //         }
    //     }
    // });
    $('#deleteOneSelectProductModal').modal('hide')

}
/******************************************** */
// 点击扩展查询展示
function extendButtonDisplay(event) {  
	let extendQueryConditionElement = $('#extendQueryCondition')
	if(extendQueryConditionElement.hasClass('hidden')){
		extendQueryConditionElement.removeClass('hidden')
	}else{
		extendQueryConditionElement.addClass('hidden')

	}

}
/*****************************************
// 重置所有查询条件　???
function removeAllQueryConditions() {  
	$('#pl-code').val('')
	$('#pl-name').val('')
	$('#pl-pinlei').val('')
	$('#pl-charger').val('')

	$('#pl-tag-jibie').find("option[value='']").attr("selected",true)
	$('#pl-tag-dingwei').val('')
	$('#pl-start').val('')
	$('#pl-end').val('')
	$('#pl-tag-shiling').val('')
	$('#pl-creater').find("option[value='']").attr("selected",true)
	$('#pl-tag-pifa').find("option[value='']").attr("selected",true)
	$('#pl-suppiler').val('')
	$('#pl-pinpai').find("option[value='']").attr("selected",true)
    $('#pl-sku-name').val('')
}
*** */
/******************************************** */
// 新增产品的判断是否合理事件
function productAddCommitEvent(event) {  
    if($('#productAddCommit').hasClass('disabled')){
        return 
    }
    let productCode = $('#p-code').val()
    let productId = $('#editOneGood').val()
    let productName = $('#p-name').val()
    let productPinleiIds= $('#p-pinlei').data('final-id')
    let productPinleiValues= $('#p-pinlei').val()
    let productPinpaiValues= $('#p-pinpai').find("option:selected").val()
    
    // 负责人修改为一个 
    let productChargerIds= $('#p-charger').find("option:selected").val()
    let productChargerValues= $('#p-charger').find("option:selected").val()
    // let productChargerIds= $('#p-charger').data('id')
    let productChargerRawIds= $('#p-charger').data('raw_id')
    // let productChargerValues= $('#p-charger').val()


    let productSupplierIds= $('#p-supplier').data('id')
    let productSupplierRawIds= $('#p-supplier').data('raw-id')
    let productSupplierValues= $('#p-supplier').val()
    let productShilingiValues= $('#p-shiling').find("option:selected").val()
    let productJibieiValues= $('#p-jibie').find("option:selected").val()
    let productPifaValues= $('#p-pifa').find("option:selected").val()
    let productTagDingweiIds= $('#p-tag-dingwei').data('id')
    let productTagDingweirValues= $('#p-tag-dingwei').val()
    let productTagChangjingIds= $('#p-tag-changjing').data('id')
    let productTagChangjingrValues= $('#p-tag-changjing').val()
    let productDescValues= $('#p-desc').val()
    let csrfTokenValue = $("input[name='csrfmiddlewaretoken']").val()

    let isValid = checkProductAddIsvalid(productCode,productName,productPinleiIds,productPinleiValues,productPinpaiValues,productChargerIds,productChargerValues,productSupplierIds,productSupplierValues,productShilingiValues,productTagChangjingIds,productTagChangjingrValues,productDescValues)

    productJibieiValues==''?productJibieiValues='0':productJibieiValues
    productTagDingweiIds==''?productTagDingweiIds='1':productTagDingweiIds
    productPifaValues==''?productPifaValues='0':productPifaValues

    if(!isValid){
        return false
    }
 
    let data = {
        'csrfmiddlewaretoken':csrfTokenValue,
        'hcode':productCode,
        'name':productName,
        'pinleis':productPinleiIds,
        'pinpai':productPinpaiValues,
        'chargers':productChargerIds,
        'suppliers':productSupplierIds,
        'shiling':productShilingiValues,
        'jibie':productJibieiValues,
        'pifa':productPifaValues,
        'tag_dingwei':productTagDingweiIds,
        'tag_changjing':productTagChangjingIds,
        'desc':productDescValues,
    }

    console.log(productId)
    if (productId !=''){


        let isChangeCharger = false
        let isChangeSupplier = false
        productChargerRawIds == productChargerIds ? isChangeCharger = false:isChangeCharger = true
        productSupplierRawIds == productSupplierIds ? isChangeSupplier = false:isChangeSupplier = true
        // 编辑产品
        data['pid'] = productId
        data['raw_suppliers'] = productSupplierRawIds
        data['raw_chargers'] = productChargerRawIds
        data['is_change_charger'] = isChangeCharger
        data['is_change_supplier'] = isChangeSupplier
        $('#productAddCommit').addClass('disabled')
        $('#productAddCommit').text('操作中...')

 
        $.ajax({
            type: "post",
            url: "/select/edit_one/",
            data: data,
            success: function (response) {
                console.log(response)
                $('#productAddCommit').removeClass('disabled')
                $('#productAddCommit').text('保存')
                if(response['code'] == '0'){
                    // ok
                    window.messageBox.show('编辑成功')
                    if(response['new']!=''){
                        sessionStorage.setItem('return2new','1')
                    }else{
                        sessionStorage.removeItem('return2new')
                    }


                    window.location.href = response['url']
                }else if(response['code']=='8') {
                    window.messageBox.show('产品编码重复,请更换编码。')
                    return false
                }else{
                    window.messageBox.show(response['msg'])
                    return false
                }
            },error:function (params) {
                window.messageBox.show('服务端错误!请刷新重试或者联系管理员！')
            }
        });
    }else{
        // 新增产品


        $('#productAddCommit').addClass('disabled')
        $('#productAddCommit').text('操作中...')
        $.ajax({
            type: "post",
            url: "/select/add_one/",
            data: data,
            success: function (response) {
                $('#productAddCommit').removeClass('disabled')
                $('#productAddCommit').text('保存')
                if(response['code']=='0'){
                    window.location.href = response['url']
                }else if(response['code']=='8'){
                    $("#p-code").focus()
                    window.messageBox.show('产品编码重复,请更换编码。')
                    return false
                }else{
                    window.messageBox.show('新增失败,请刷新重试!')
                    return false
                }
            },error:function () {
                $('#productAddCommit').removeClass('disabled')
                $('#productAddCommit').text('保存')
                window.messageBox.show('服务端错误!请刷新重试或者联系管理员！')
            }
        });
    }
     

}

// 校验添加产品输入是否合理
function checkProductAddIsvalid(productCode,productName,productPinleiIds,productPinleiValues,productPinpaiValues,productChargerIds,productChargerValues,productSupplierIds,productSupplierValues,productShilingiValues,productTagChangjingIds,productTagChangjingrValues,productDescValues) {  
    // productAddAlertmsgModal

    if(!/^h\d{5}$/.test(productCode)){
        $("#p-code").focus()
        window.messageBox.show('请正确输入产品编码,如h19001-h20001')
        return false
    }else{
        if(productName.trim()==''){
            $("#p-name").focus()
            window.messageBox.show('请输入产品名称')
            return false
        }else{
            if(productPinleiIds==''){
                $("#p-pinlei").focus()
                return false
            }else{
                if(productPinpaiValues==''){
                    $("#p-pinpai").focus()
                    window.messageBox.show('请选择品牌')
                    return false
                }else{
                    if(productChargerValues==''){
                        $("#p-charger").focus()
                        window.messageBox.show('请选择负责人')
                        return false
                    }else{
                        if(productSupplierValues == ''){
                            $("#p-supplier").focus()
                            window.messageBox.show('请选择供应商')
                            return false
                        }else{
                            if(productShilingiValues == ''){
                                $("#p-shiling").focus()
                                window.messageBox.show('请选择时令')
                                return false
                            }else{
                                return true
                                // if(productTagChangjingrValues==''){
                                //     $("#p-changjing").focus()
                                //     productAlertMsg('请选择场景')
                                //     return false
                                // }else
                                // {return true
                                // }
                            }
                        }
                    }
                }
            }
        }
    }

}

// 三秒弹框自动关闭 显示错误信息
function productAlertMsg(msg) {  
    $('#productAddAlertmsgModal').modal('show')
    $('#modal_title_p_alert').text(msg)
    setTimeout(() => {
        $('#productAddAlertmsgModal').modal('hide')
    }, 2000);
}

// 清空所有输入框的值
function cancelAddProductInputValue(params) {


    // 返回候选品列表
    window.location.href = '/select/p_list/'
}
/******************************************** */

function returnModify(event) {
    let pid = $(event).data('pid')
    window.location.href = '/select/edit_one?pid='+pid
    
}
/******************************************** */

function watchList(event) {


    if(sessionStorage.getItem('return2new')==undefined){
        window.location.href = '/select/p_list/'
    }else{
        window.location.href = '/select/add_sku/'

    }
    
}

/******************************************** */
function clearAddProductInputValue() {
    window.location.reload()
}
/******************************************** */
