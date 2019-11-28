$(document).ready(function($) {
	// 初始化模态对话框
    // $('#rukuGoodPdate').cxCalendar()
    $('#rukuGoodRealArrivaldate').cxCalendar()
});

// 鼠标悬停显示备注
function yanhuoDescExpend(event) {  
    $(event).popover('show')
}
function yanhuoDescReduce(event) {  
    $(event).popover('hide')
}



// 入库的的条件查询
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
    let dianhuo =$('#pl-dianhuo').find("option:selected").val()
    let yanhuo =$('#pl-yanhuo').find("option:selected").val()
    let flag = $('#exportCSV').data('flag')


    // 是否展开扩展查询   默认为true 隐藏
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
        'dianhuo':dianhuo,
        'yanhuo':yanhuo,
        'flag':flag,
    }
    $('#exportCSV').data('flag',0)

    // 统一执行这个函数 导出csv
    exportCsvBase(urlQuery,data,flag)
 

}
/****************************** */


// 入库弹出框
function rukuBtnClick(event) {  
    let pid = $(event).data('id')
    $('#rukuGoodId').val(pid)
    $('#rukuModal').modal('show')
    $('#yanhuoContainer').addClass('hidden')

    
    $.ajax({
        type: "get",
        url: "/purchase/ruku_get_detail/",
        data: {'good_id':pid},
        success: function (response) {
            $('#rukuButtonComfirm').removeClass('disabled')
            $('#rukuButtonComfirm').text('保存')
            if(response['code']=='0'){
                let good = response['good']
                let caigou = response['caigou']
                let dianhuo = response['dianhuo']
                let yanhuo = response['yanhuo']
                // 插入数据到对话框
                $('#rukuGoodCode').val(good['code'])
                $('#rukuGoodName').val(good['name'])
                $('#rukuGoodProductCharger').val(good['charger'])
                $('#rukuGoodCreateDate').val(good['created_at'])
                $('#rukuGoodSupplier').val(good['supplier'])
                $('#rukuGoodjibie').val(good['jibie'])
                // 采购
                $('#rukuGoodPurchaser').val(caigou['charger'])
                $('#rukuGoodPdate').val(caigou['purchase_date'])
                $('#rukuGoodPurchaseDesc').data('content',caigou['desc'])
                $('#rukuGoodEdate').val(caigou['expected_data'])
                // 点货
                $('#rukuGoodRealdate').val(dianhuo['real_arrival_date'])
                $('#goodDianhuoUser').val(dianhuo['charger'])
                $('#goodDianhuoDetail').val(dianhuo['state'])
                $('#goodDianhuoDesc').data('content',dianhuo['desc'])
                // 验货
                if (yanhuo['result']){
                    $('#yanhuoContainer').removeClass('hidden')
                    $('#goodYanhuoDesc').data('content',yanhuo['desc'])
                    $('#goodYanhuoDetail').val(yanhuo['result'])
                    $('#rukuGoodYanhuoCharger').val(yanhuo['charger'])
                    if(yanhuo['video'].length>30){
                        $('#goodYanhuoVideoA').attr('href',yanhuo['video'])
                    }else{
                        $('#goodYanhuoVideo').addClass('hidden')
                    }
                    let imgArray = yanhuo['images']
                    let htmlStr= ''
                    imgArray.forEach(element => {
                        htmlStr += `
                        <div class="out">
                        <img src="`+element+`" alt="" onmouseenter="skuImageExpend(this)" onmouseleave="skuImageReduce(this)">
                        </div>
                        `
                    });
                    $('#yanhuoImageContainer').html(htmlStr)
                }

                
            }else{
                // $('#rukuGoodEdate').siblings('.alertMsg').text()
                window.messageBox.show(response['msg'])
            }
        },error:function (response) {  
            window.messageBox.show('服务端错误!请刷新重试或者联系管理员！')
            // $('#rukuGoodEdate').siblings('.alertMsg').text('')

        }
    });

}

// 入库弹出框结束
function rukuModalClose(event) {  
    if($('#rukuButtonComfirm').hasClass('disabled')){
        return 
    }
    let rukuGoodId = $('#rukuGoodId').val()
    // 负责人  点货结果 备注 是否级联到入库
    let goodRukucharger = $('#goodRukucharger').find("option:selected").val()
    let goodRukuDetail = $('#goodRukuDetail').find("option:selected").val()
    let GoodRukuDesc = $('#GoodRukuDesc').val()
    
    // 新加的逻辑判断   退货退款，补货换货必须填写入库备注进行说明。
    if(goodRukuDetail!= '0'){
        if(GoodRukuDesc==''){
            window.messageBox.show('请填写备注信息')
            $('#GoodRukuDesc').focus()
            return false
        }
    }
    let data = {
        'good_id':rukuGoodId,
        'charger':goodRukucharger,
        'result':goodRukuDetail,
        'desc':GoodRukuDesc,
        'csrfmiddlewaretoken': $("input[name='csrfmiddlewaretoken']").val()
    }

    ReloadAjax('post',data,"/purchase/ruku/",'rukuButtonComfirm','rukuModal') 

}


