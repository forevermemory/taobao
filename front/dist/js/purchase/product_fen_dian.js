$(document).ready(function($) {
	// 初始化模态对话框
    // $('#purchaseIndexGoodPdate').cxCalendar()
    $('#purchaseIndexGoodRealArrivaldate').cxCalendar()
});




// 分货点货的条件查询
function exeQueryFenAndDian(event) {  
    let urlQuery = $(event).data('query-url')
    let code = $('#pl-code').val()
    let name = $('#pl-name').val()
    let pinlei = $('#pl-pinlei').val()
    let chargerIds = $('#pl-charger').find("option:selected").val()
    let suppilerIds = $('#pl-supplier').data('id')
    let suppilerVal = $('#pl-supplier').val()
    let jibie =$('#pl-tag-jibie').find("option:selected").val()
    let start = $('#pl-start').val()
    let end = $('#pl-end').val()
    let state =$('#pl-state').find("option:selected").val()
    let flag = $('#exportCSV').data('flag')

    // 是否展开扩展查询   默认为true 隐藏
    let isSpread = $('#extendQueryCondition').hasClass('hidden')
    let data = {
        'p':1,
        'code':code,
        'name':name,
        'pinlei':pinlei,
        'chargers':chargerIds,
        'suppliers':suppilerIds,
        'suppilerVal':suppilerVal,
        'jibie':jibie,
        'start':start,
        'end':end,
        'state':state,
        'flag':flag,
    }
    $('#exportCSV').data('flag',0)

    // 统一执行这个函数 导出csv
    exportCsvBase(urlQuery,data,flag)


}
/****************************** */


// 评审弹出框
function fenAndDianBtnClick(event) {  
    let pid = $(event).data('id')
    let code = $(event).data('code')
    let name = $(event).data('name')
    let charger = $(event).data('charger')
    let c_date = $(event).data('c_date')
    let e_date = $(event).data('e_date')
    let desc = $(event).data('desc')

    $('#purchaseIndexGoodId').val(pid)
    $('#purchaseIndexGoodCode').val(code)
    $('#purchaseIndexGoodName').val(name)
    $('#purchaseIndexGoodPurchaser').val(charger)
    $('#purchaseIndexGoodPdate').val(c_date)
    $('#purchaseIndexGoodEdate').val(e_date)
    $('#purchaseIndexGoodDesc').val(desc)
    $('#purchaseIndexModal').modal('show')
    $('#purchaseIndexButtonComfirm').text('保存')
    $('#purchaseIndexButtonComfirm').removeClass('disabled')

}

// 点货分货弹出框结束
function dianAndFenModalClose(event) {  
    if($('#purchaseIndexButtonComfirm').hasClass('disabled')){
        return 
    }
    let purchaseIndexGoodId = $('#purchaseIndexGoodId').val()
    // 负责人  点货结果 备注 是否级联到入库
    let purchaseIndexGoodPurchaser = $('#goodDianhuoUser').find("option:selected").val()
    let goodDianhuoDetail = $('#goodDianhuoDetail').find("option:selected").val()
    let GoodDianhuoDesc = $('#GoodDianhuoDesc').val()
    let purchaseIndexGoodRealArrivaldate = $('#purchaseIndexGoodRealArrivaldate').val()
    let GoodDianhuoAndYanhuo = $('#GoodDianhuoAndYanhuo').is(':checked')

    // 实际到货日期必须填写
    if(purchaseIndexGoodRealArrivaldate== ''){
            window.messageBox.show('请填写实际到货日期')
            $('#purchaseIndexGoodRealArrivaldate').focus()
            return false
    }
    
    // 新加的逻辑判断   如果点货结果为缺货 发错货 其他 desc必须填写
    if(goodDianhuoDetail!= '0'){
        if(GoodDianhuoDesc==''){
            window.messageBox.show('请填写备注信息')
            $('#GoodDianhuoDesc').focus()
            return false
        }
    }

    let data = {
        'csrfmiddlewaretoken': $("input[name='csrfmiddlewaretoken']").val(),
        'good_id':purchaseIndexGoodId,
        'state':goodDianhuoDetail,
        'puser_id':purchaseIndexGoodPurchaser,
        'is_checked':GoodDianhuoAndYanhuo,
        'desc':GoodDianhuoDesc,
        'real_arrival_date':purchaseIndexGoodRealArrivaldate,
    }

    ReloadAjax('post',data,"/purchase/fen_dian/",'purchaseIndexButtonComfirm','purchaseIndexModal') 

}

