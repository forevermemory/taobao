
// 初始化日期插件
$(function () {  

    // $('#pl-zhizuo_end').cxCalendar()
    // $('#pl-zhizuo_start').cxCalendar()
    // $('#pl-ruku_end').cxCalendar()
    // $('#pl-ruku_start').cxCalendar()
    getShangjiaSkus()

})


// 鼠标悬停显示店铺列表
function shangjiaShopExpend(event) {  
    $(event).popover('show')
}
function shangjiaShopReduce(event) {  
    $(event).popover('hide')
}


/*************************** */
// 封存阶段条件查询
function exeFengcunQuery(event) {  

    let urlQuery = $(event).data('query-url')
    let code = $('#pl-code').val()
    let name = $('#pl-name').val()
    let pinlei = $('#pl-pinlei').val()
    let chargers = $('#pl-charger').find("option:selected").val()
    let suppilerIds = $('#pl-supplier').data('id')
    let suppilerVal = $('#pl-supplier').val()
    let jibie =$('#pl-tag-jibie').find("option:selected").val()
    
    // 新的查询条件   

    let fengcun_state =$('#pl-fengcun').find("option:selected").val()
    let flag = $('#exportCSV').data('flag')


    let data = {
        'code':code,
        'name':name,
        'pinlei':pinlei,
        'jibie':jibie,
        'chargers':chargers,
        'suppliers':suppilerIds,
        'suppiler_val':suppilerVal,
        'fengcun_state':fengcun_state,
        'flag':flag,
    }
    $('#exportCSV').data('flag',0)

    // 统一执行这个函数 导出csv
    exportCsvBase(urlQuery,data,flag)

}




// 点击封存 打开modal
function fengcunModalShowBtn(event) {  
    let good_id = $(event).data('id')
    $('#fengcunGoodId').val(good_id)
    $('#fengcunModal').modal('show')
}

// 封存确定事件
function fengcunSubmitButtonComfirmEvent() {  
    let good_id = $('#fengcunGoodId').val()
    if($('#fengcunSubmitButtonComfirm').hasClass('disabled')){
        return false
    }
    let data = {
        'good_id':good_id,
    }
    let url = '/sale/fengcun/'
    ReloadAjax('post',data,url,'fengcunSubmitButtonComfirm','fengcunModal')
}

// 启封 打开modal

function qifengModalShowBtn(event) {  
    let good_id = $(event).data('id')
    $('#qifengGoodId').val(good_id)
    $('#qifengModal').modal('show')
}

// 启封确定事件
function qifengSubmitButtonComfirmEvent() {  
    let good_id = $('#qifengGoodId').val()
    if($('#qifengSubmitButtonComfirm').hasClass('disabled')){
        return false
    }

    let data = {
        'good_id':good_id,
    }
    let url = '/sale/fengcun/'
    ReloadAjax('put',data,url,'qifengSubmitButtonComfirm','qifengModal')


}


// 封存阶段异步获取sku
function getShangjiaSkus() {  
    let goodIds = []
    $.each($('.good_id'), function (indexInArray, valueOfElement) { 
        goodIds.push($(valueOfElement).data('good_id'))
    });
    getAllGoodId({'good_ids':goodIds+'','kind':'skus'},function (res) {  
        
        $.each($('.good_id'), function (indexInArray, valueOfElement) { 
            let skus = res[indexInArray]['skus']
            if(skus.length > 0){
                // 存在sku  在当前的一行后面添加skus行  同时给当前 tr 的第一个td 添加下拉箭头

                var dropDown = `<span class="caret" data-to=`+res[indexInArray]['good_id']+` onclick="caretClick(this)" style="width:5px;height:10px;"></span>`
                $(valueOfElement).find('td:first-child').html(dropDown)

                var HTML = ''
                for (let k = 0; k < skus.length; k++) {
                    
                        HTML += `<tr class="addGoodSku`+res[indexInArray]['good_id']+`" style="display: none;">
                        <td class="text-center"><img src="`+skus[k]['sku_image']+`" alt="" style="width: 35px;height:35px;"></td>
                        <td class="text-center">`+res[indexInArray]['good_code']+`-`+skus[k]['sku_code']+`</td>
                        <td class="text-center">`+skus[k]['sku_name']+`</td>
                        <td class="text-center"></td>
                        <td class="text-center"></td>
                        <td class="text-center"></td>
                        <td class="text-center"></td>
                        <td class="text-center"></td>
                        <td class="text-center"></td>
                        <td class="text-center"></td>
                        <td class="text-center"></td>
                        <td class="text-center"></td>
                        <td class="text-center"></td>
                        <td class="text-center"></td>
                        <td class="text-center"></td>
                    </tr>`
                }
                $(valueOfElement).after(HTML)
            }
        });
    })
}

