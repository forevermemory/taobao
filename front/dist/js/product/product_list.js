$(document).ready(function($) {
	// 初始化双向选择
    $('#multiselect').multiselect();


	//　初始化日期选择控件
	$('#pl-end').cxCalendar()
    $('#pl-start').cxCalendar()
    
    // 获取品类名称
    // let goodIds = []
    // $.each($('.good_id'), function (indexInArray, valueOfElement) { 
    //     goodIds.push($(valueOfElement).data('good_id'))
    // });
    // getAllGoodId({'good_ids':goodIds+'','kind':'cates'},function (res) {  
    //     $.each($('.cate_name'), function (indexInArray, valueOfElement) { 
    //         $(valueOfElement).text(res[indexInArray]['cate_name'])
    //     });
    // })
    // // 获取是否有sku
    // getNewProductSkus(goodIds)
});

function PrefixIntegerZero(num, length) {

    return (Array(length).join('0') + parseInt(num)).slice(-length)
}


/************************************************* */
// 获取查询参数　候选品 和评审 查询条件和渲染的内容是一样的执行查询
function exeQueryHouxuanpin(event) {  
    
    let urlQuery = $(event).data('query-url')
    let code = $('#pl-code').val()
    let name = $('#pl-name').val()
    let pinlei = $('#pl-pinlei').val()

    let chargerIds = $('#pl-charger').find("option:selected").val()

    let suppilerIds = $('#pl-supplier').data('id')
    let dingweiIds = $('#pl-tag-dingwei').data('id')
    let suppilerVal = $('#pl-supplier').val()
    let dingweiVal = $('#pl-tag-dingwei').val()

    let jibie =$('#pl-tag-jibie').find("option:selected").val()
    let shiling =$('#pl-tag-shiling').find("option:selected").val()
    let pifa =$('#pl-tag-pifa').find("option:selected").val()
    let pinpai =$('#pl-pinpai').find("option:selected").val()
    let creater =$('#pl-creater').find("option:selected").val()

    let start = $('#pl-start').val()
    let end = $('#pl-end').val()
    let skuName = $('#pl-sku-name').val()

    let flag = $('#exportCSV').data('flag')
 
    // 是否展开扩展查询   默认为true 隐藏
    let isSpread = $('#extendQueryCondition').hasClass('hidden')
    let data = {
        // 'p':1,
        'code':code,
        'name':name,
        'pinlei':pinlei,
        'chargers':chargerIds,
        'suppliers':suppilerIds,
        'dingweis':dingweiIds,
        'suppilerVal':suppilerVal,
        'dingweiVal':dingweiVal,
        'jibie':jibie,
        'shiling':shiling,
        'pifa':pifa,
        'pinpai':pinpai,
        'start':start,
        'creater':creater,
        'end':end,
        'sku_name':skuName,
        'spread':isSpread,
        'flag':flag,
    }
    $('#exportCSV').data('flag',0)
    // 统一执行这个函数 导出csv
    exportCsvBase(urlQuery,data,flag)



}

// 点击扩展查询展示
function extendButtonDisplay(event) {  
	let extendQueryConditionElement = $('#extendQueryCondition')
	if(extendQueryConditionElement.hasClass('hidden')){
		extendQueryConditionElement.removeClass('hidden')
	}else{
		extendQueryConditionElement.addClass('hidden')

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

//终止产品
function cancelOneSelectProduct(event) {
    let pid = $(event).data('pid')
    $('#cancelGoodId').val(pid)
    $('#cancelProductPhaseModal').modal('show')

}

// 终止关闭按钮
function cancelProductPhaseModalClose(params) {


    let data = {
        'good_id':$('#cancelGoodId').val(),
    }
    $('#cancelProductButtonComfirm').addClass('disabled')
    $('#cancelProductButtonComfirm').text('操作中...')
    $.ajax({
        type: "get",
        url: "/select/cancel_product/",
        data: data,
        success: function (response) {
            $('#cancelProductButtonComfirm').removeClass('disabled')
            $('#cancelProductButtonComfirm').text('确认')
            if(response['code']=='0'){
                // 操作成功
                window.messageBox.show('操作成功')
                window.location.reload()
                $('#cancelProductPhaseModal').modal('hide')
            }else{
                window.messageBox.show('操作失败!请刷新重试')
                return false
            }
        },
        error:function (response) {  
            window.messageBox.show('服务端错误!请刷新重试或者联系管理员！')
            return false
        }
    });
    
}


