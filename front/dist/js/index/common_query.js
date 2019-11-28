$(document).ready(function($) {
    // 初始化日期选择框
    $('#end_salePhase').cxCalendar()
    $('#start_salePhase').cxCalendar()
    $('#end_newAndMakePhase').cxCalendar()
    $('#start_newAndMakePhase').cxCalendar()

    // 获取品类名称
    let goodIds = []
    $.each($('.good_id'), function (indexInArray, valueOfElement) { 
        goodIds.push($(valueOfElement).data('good_id'))
    });

    // 分开查询查询
    getIndexQuerySkus(goodIds)
    getIndexQueryCates(goodIds)
    getIndexQueryMakeData(goodIds)
    getIndexQuerySaleData(goodIds)
    getIndexQueryDianpuData(goodIds)
});


// 鼠标悬停显示店铺列表
function shangjiaShopExpend(event) {  
    $(event).popover('show')
}
function shangjiaShopReduce(event) {  
    $(event).popover('hide')
}

// 首页通用查询 的条件查询
function exeQueryCommon(event) {  
    let urlQuery = $(event).data('query-url')
    let code = $('#pl-code').val()
    let name = $('#pl-name').val()
    let pinlei = $('#pl-pinlei').val()
    let chargers = $('#pl-charger').find("option:selected").val()
    let suppilerIds = $('#pl-supplier').data('id')
    let suppilerVal = $('#pl-supplier').val()
    let jibie =$('#pl-tag-jibie').find("option:selected").val()

    // 上新阶段
    let shangxinType = $('#newAndMakePhase').val()
    let shangxinStart = $('#start_newAndMakePhase').val()
    let shangxinEnd = $('#end_newAndMakePhase').val()
    // 销售阶段
    let saleType = $('#salePhase').val()
    let saleStart = $('#start_salePhase').val()
    let doShop = $('#pl-do_shop').val()
    let saleEnd = $('#end_salePhase').val()
    let flag = $('#exportCSV').data('flag')

    let data = {
        'code':code,
        'name':name,
        'pinlei':pinlei,
        'chargers':chargers,
        'suppliers':suppilerIds,
        'suppilerVal':suppilerVal,
        'jibie':jibie,
        'shangxin_type':shangxinType,
        'shangxin_start':shangxinStart,
        'shangxin_end':shangxinEnd,
        'sale_type':saleType,
        'sale_start':saleStart,
        'sale_end':saleEnd,
        'do_shop':doShop,

        'flag':flag,
    }
    $('#exportCSV').data('flag',0)

    // 统一执行这个函数 导出csv
    exportCsvBase(urlQuery,data,flag)

}


// function removeAllQueryConditions() {  
//     window.location.href = '/query'
// }



function getIndexQuerySkus(goodIds) {  
    getAllGoodId({'good_ids':goodIds+'','kind':'skus'},function (res) {  
        // $.each($('.cate_name'), function (indexInArray, valueOfElement) { 
        //     $(valueOfElement).text(res[indexInArray]['cate_name'])
        // });
        $.each($('.good_id'), function (indexInArray, valueOfElement) { 
            let skus = res[indexInArray]['skus']
            if(skus.length > 0){
                // 存在sku  在当前的一行后面添加skus行  同时给当前 tr 的第一个td 添加下拉箭头

                let dropDown = `<span class="caret" data-to=`+res[indexInArray]['good_id']+` onclick="caretClick(this)" style="width:5px;height:10px;"></span>`
                $(valueOfElement).find('td:first-child').html(dropDown)
                var HTML = ''
                for (let k = 0; k < skus.length; k++) {
                    
                        HTML +=`<tr class="addGoodSku`+res[indexInArray]['good_id']+`" style="display: none;">
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

function getIndexQueryCates(goodIds) {  
    getAllGoodId({'good_ids':goodIds+'','kind':'cates'},function (res) {  
        console.log('skus')
        $.each($('.cate_name'), function (indexInArray, valueOfElement) { 
            $(valueOfElement).text(res[indexInArray]['cate_name'])
        });
    })
}

function getIndexQueryMakeData(goodIds) {  
    getAllGoodId({'good_ids':goodIds+'','kind':'make'},function (res) {  
        console.log('Make')
        let caigous = $('.indexCaigou')
        let fendians = $('.indexFendian')
        let rukus = $('.indexRuku')
        let rukuStates = $('.indexRukuState')
        let paishes = $('.indexPaishe')
        let zhizuos = $('.indexZhizuo')
        let zhizuoStates = $('.indexzhizuoState')
        for (let k = 0; k < res.length; k++) {
            $(caigous[k]).text(res[k]['caigou']['date'])
            $(fendians[k]).text(res[k]['fendian']['date'])
            $(rukus[k]).text(res[k]['ruku']['date'])
            $(rukuStates[k]).text(res[k]['ruku']['state'])
            $(paishes[k]).text(res[k]['paishe']['date'])
            $(zhizuos[k]).text(res[k]['zhizuo']['date'])
            $(zhizuoStates[k]).text(res[k]['zhizuo']['state'])
        }
    })
}
function getIndexQuerySaleData(goodIds) {  
    getAllGoodId({'good_ids':goodIds+'','kind':'sale'},function (res) {  
        console.log('Sale')
        let shangjias = $('.indexShangjia')
        let fengcuns = $('.indexFengcun')
        let taotais = $('.indexTaotai')
        let tuishis = $('.indexTuishi')

        for (let k = 0; k < res.length; k++) {
            $(shangjias[k]).text(res[k]['shangjia']['date'])
            if (res[k]['good_state_sale'] != '11'){
                $(fengcuns[k]).text(res[k]['fengcun']['date'])
                $(taotais[k]).text(res[k]['taotai']['date'])
                $(tuishis[k]).text(res[k]['tuishi']['date'])

            }

        }
    })
}
function getIndexQueryDianpuData(goodIds) {  
    getAllGoodId({'good_ids':goodIds+'','kind':'dianpu'},function (res) {  
        console.log('dianpu')
        // console.log(res)
        let indexShangjiaStates = $('.indexShangjiaState')
        for (let k = 0; k < res.length; k++) {
            let shops = res[k]['shops']
            if(shops.length > 0){
                let names = ''
                let subNames = ''
                for (let l = 0; l < shops.length; l++) {
                    names += shops[l]['name'] +','
                    subNames += shops[l]['sub_name'] +','
                    
                }
                let dianpus = `<td class="text-center"  data-container="body" data-toggle="popover" data-placement="top" data-content="`+names+`"  onmouseenter="shangjiaShopExpend(this)" onmouseleave="shangjiaShopReduce(this)">`+subNames+`</td>`
                // $(indexShangjiaStates[k]).after(dianpus)
                $(indexShangjiaStates[k]).siblings('.indexDianpus').remove()
                $(indexShangjiaStates[k]).after(dianpus)
            }else{
                // $(indexShangjiaStates[k]).after('<td class="text-center"></td>')
            }


        }
    })
}

