$(document).ready(function($) {
	// 初始化日期对话框
    $('#purchaseIndexGoodPdate').cxCalendar()
    $('#purchaseIndexGoodEdate').cxCalendar()
});

// 评审弹出框
function purchaseIndexBtnClick(event) {  
    let pid = $(event).data('id')
    let code = $(event).data('code')
    let name = $(event).data('name')
    $('#purchaseIndexGoodId').val(pid)
    $('#purchaseIndexGoodCode').val(code)
    $('#purchaseIndexGoodName').val(name)
    $('#purchaseIndexGoodPdate').val('')
    $('#purchaseIndexGoodEdate').val('')
    $('#purchaseIndexModal').modal('show')
    $('#purchaseIndexButtonComfirm').text('保存')
    $('#purchaseIndexButtonComfirm').removeClass('disabled')

}

// 采购弹出框结束
function purchaseIndexModalClose(event) {  
    if($('#purchaseIndexButtonComfirm').hasClass('disabled')){
        return 
    }
    let purchaseIndexGoodId = $('#purchaseIndexGoodId').val()
    let purchaseIndexGoodPdate = $('#purchaseIndexGoodPdate').val()
    let purchaseIndexGoodEdate = $('#purchaseIndexGoodEdate').val()
    let purchaseIndexGoodDesc = $('#purchaseIndexGoodDesc').val()
    // 负责人
    let purchaseIndexGoodPurchaser = $('#purchaseIndexGoodPurchaser').find("option:selected").val()
    if(purchaseIndexGoodEdate == ''){
        $('#purchaseIndexGoodEdate').siblings('.alertMsg').text('必须选择预计到货日期!')
        return false
    }
    $('#purchaseIndexGoodEdate').siblings('.alertMsg').text('')
    let data = {
        'csrfmiddlewaretoken': $("input[name='csrfmiddlewaretoken']").val(),
        'good_id':purchaseIndexGoodId,
        'p_date':purchaseIndexGoodPdate,
        'e_date':purchaseIndexGoodEdate,
        'puser_id':purchaseIndexGoodPurchaser,
        'desc':purchaseIndexGoodDesc,
    }
    $('#purchaseIndexButtonComfirm').addClass('disabled')
    $('#purchaseIndexButtonComfirm').text('操作中...')
    
    ReloadAjax('post',data,"/purchase/purchase/",'purchaseIndexButtonComfirm','purchaseIndexModal') 


}


function exeQueryCaigou(event) {  
    
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

    let flag = $('#exportCSV').data('flag')
 
    let data = {
        'code':code,
        'name':name,
        'pinlei':pinlei,
        'chargers':chargerIds,
        'suppliers':suppilerIds,
        'suppilerVal':suppilerVal,
        'jibie':jibie,
        'start':start,
        'end':end,
        'flag':flag,
    }
    $('#exportCSV').data('flag',0)

    // 统一执行这个函数 导出csv
    exportCsvBase(urlQuery,data,flag)


}