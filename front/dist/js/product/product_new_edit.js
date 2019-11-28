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







/******************************************** */
// 新增产品的判断是否合理事件
function productNewEditCommitEvent(event) {  
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
        'code':productCode,
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
        data['new'] = 'new'
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


                    if(response['new']!=undefined){
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

}

// 校验添加产品输入是否合理
function checkProductAddIsvalid(productCode,productName,productPinleiIds,productPinleiValues,productPinpaiValues,productChargerIds,productChargerValues,productSupplierIds,productSupplierValues,productShilingiValues,productTagChangjingIds,productTagChangjingrValues,productDescValues) {  
    // productAddAlertmsgModal

    if(!/(^[1,2,3,4,5]{1}[0-9]{4}$)|(^[T][1,2,3,4,5]{1}[0-9]{4}$)/.test(productCode)){
        $("#p-code").focus()
        window.messageBox.show('请正确输入产品编码,如19001-20001')
        return false
    }else{
        if(productName.trim()==''){
            $("#p-name").focus()
            window.messageBox.show('请输入产品名称')
            return false
        }else{
            if(productPinleiValues==''){
                $("#p-pinlei").focus()
                window.messageBox.show('请选择品类')
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



/******************************************** */
function cancelEditNewProduct() {  

    // 跳转回到新品管理页面
    window.location.href="/select/add_sku/"

}
