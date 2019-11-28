$(document).ready(function($) {
    // 获取品类名称
    let goodIds = []
    $.each($('.good_id'), function (indexInArray, valueOfElement) { 
        goodIds.push($(valueOfElement).data('good_id'))
    });
    getAllGoodId({'good_ids':goodIds+'','kind':'cates'},function (res) {  
        $.each($('.cate_name'), function (indexInArray, valueOfElement) { 
            $(valueOfElement).text(res[indexInArray]['cate_name'])
        });
    })
    // 获取是否有sku
    getNewProductSkus(goodIds)
});


function getNewProductSkus(goodIds) {  
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
                for (let k = 0; k < skus.length; k++) {
                    $(valueOfElement).after(
                        `<tr class="addGoodSku`+res[indexInArray]['good_id']+`" style="display: none;">
                        <td class="text-center"><img src="`+skus[k]['sku_image']+`" alt="" style="width: 35px;height:35px;"></td>
                        <td class="text-center">`+res[indexInArray]['good_code']+`-`+skus[k]['sku_code']+`</td>
                        <td class="text-center">`+skus[k]['sku_name']+`</td>
                        <td class="text-center">`+skus[k]['sku_weight']+`</td>
                        <td class="text-center">`+skus[k]['sku_v']+`</td>
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
                    )
                }
            }
        });
    })
}
