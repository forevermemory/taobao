
// checkIsEditOrAdd 的value  0第一次上架  1编辑
// 初始化日期插件
$(function () {  

    $('#pl-zhizuo_end').cxCalendar()
    $('#pl-zhizuo_start').cxCalendar()
    $('#pl-ruku_end').cxCalendar()
    $('#pl-ruku_start').cxCalendar()
    getShangjiaSkus()

})


// 鼠标悬停显示店铺列表
function shangjiaShopExpend(event) {  
    $(event).popover('show')
}
function shangjiaShopReduce(event) {  
    $(event).popover('hide')
}


// 点击上架弹出modal 渲染产品的skus
function shangjiaModalShowBtn(event) {  
    $('#checkIsEditOrAdd').val('0')
    let good_id = $(event).data('id')
    let code = $(event).data('code')
    let name = $(event).data('name')
    $('#shangjiaGoodId').val(good_id)
    $('#shangjiaGoodCode').val(code)
    $('#shangjiaGoodName').val(name)
    $('#shangjiamodalTitleQuery').text(''+name+'' + '店铺上架操作')
    $('#shangjiaModal').modal('show')

    getAllShop(function () {  
        $.ajax({
            type: "get",
            url: "/sale/get_good_sku/",
            data: {'good_id':good_id},
            success: function (response) {
                if(response['code']=='0'){
                    let skusArr = JSON.parse(response['skus'])
                    let domain = response['domain']
    
                    let shops = JSON.parse(sessionStorage.getItem('shops'))
                    let shopLength = shops.length

                    // 表格一行的 checkbox
                    let tbodyCheckbox = ''
                    // 表头
                    let theadCpmRawHtml = `
                        <th class="text-center">缩略图</th>
                        <th class="text-center">SKU编码</th>
                        <th class="text-center">SKU名称</th>
                    `
                    shops.forEach(element => {
                        theadCpmRawHtml +=`
                        <th onclick="cpmShopAddSkuSelectAllorNotAll(this)" class="text-center cpmShopTitle" data-shop_id=`+element['pk']+`>`+element['fields']['name']+`

                        </th>
                        `
                        tbodyCheckbox += `
                            <td class="text-center sku-shop">
                                <input data-shop_id="`+element['pk']+`" class="form-check-input shop__`+element['pk']+`" type="checkbox" value="0">
                            </td>
                        `
                    });
                    // 表头
                    $('#theadCpm').html(theadCpmRawHtml)
    
                    let skuHtml =''
                    skusArr.forEach(skuElement => {
                        let sku =  skuElement['fields']
                        let sku_id =  skuElement['pk']
                        skuHtml += `
                        <tr class="tbody_tr" data-sku_id="`+sku_id+`">
                            <td class="text-center"><img src="`+domain+sku['sku_image']+`" style="width:30px;height:30px;"></td>
                            <td class="text-center">`+sku['sku_code']+`</td>
                            <td class="text-center">`+sku['sku_name']+`</td>
                            `+tbodyCheckbox+`
                        </tr>
                        `
    
                        // 表格内容
                        $('#tbodyCpm').html(skuHtml)
                    });
                    // 循环渲染数据
                }else{
                    window.messageBox.show(response['msg'])
                }
            },
            error:function (response) {  
            }
        });
    })

    // // 获取所有店铺
    


}

/*********************************************************** */
// 编辑 非第一次上架
function reshangjiaModalShowBtn(event) {  
    $('#checkIsEditOrAdd').val('1')

    let good_id = $(event).data('id')
    let is_multi_export = $(event).data('is_multi_export')

    let code = $(event).data('code')
    let name = $(event).data('name')
    $('#shangjiaGoodId').val(good_id)
    $('#shangjiaGoodCode').val(code)
    $('#shangjiaGoodName').val(name)
    $('#shangjiamodalTitleQuery').text(''+name+'' + '店铺上架操作')
    $('#shangjiaModal').modal('show')


    // TODO
    // 暂时没有sku和店铺的关系  所以点击修改没有数据出现

    // $('#tbodyCpm').html('')
    getAllShopAndskus(good_id,function () {  
        $.ajax({
            type: "get",
            url: "/sale/get_good_sku/",
            data: {'good_id':good_id},
            success: function (response) {
                if(response['code']=='0'){
                    // let skusArr = JSON.parse(response['skus'])
                    let domain = response['domain']
    
                    let shops = JSON.parse(sessionStorage.getItem('shops_skus'))
                    // sessionStorage.removeItem('shops_skus')
                    let shopLength = shops.length

                    // 表格一行的 checkbox
                    let tbodyCheckbox = ''
                    // 表头
                    let theadCpmRawHtml = `
                        <th class="text-center">缩略图</th>
                        <th class="text-center">SKU编码</th>
                        <th class="text-center">SKU名称</th>
                    `
                    shops.forEach(element => {
                        theadCpmRawHtml +=`
                        <th onclick="cpmShopAddSkuSelectAllorNotAll(this)" class="text-center cpmShopTitle" data-shop_id=`+element['shop_id']+`>`+element['shop_name']+`

                        </th>
                        `

                        let tbodyCheckboxData = ''
                        for (let o = 0; o < element['shop_skus'].length; o++) {
                            tbodyCheckboxData+=`
                                data-`+o+`__sku_id = "`+element['shop_skus'][o]['sku_id']+`" data-`+o+`__sku_in_shop_state = "`+element['shop_skus'][o]['sku_in_shop_state']+`"   data-`+o+`__shop2_id = "`+element['shop_skus'][o]['shop2_id']+`"
                            `
                        }
                        // data-shop2_id = "`+element['shop_skus'][0]['shop2_id']+`"
                        tbodyCheckbox += `
                            <td class="text-center sku-shop">
                                <input `+tbodyCheckboxData+`  data-shop_id="`+element['shop_id']+`" data-shop2_id="" class="cpm_is_checked form-check-input shop__`+element['shop_id']+`" type="checkbox" value="0">
                            </td>
                        `
                    });
                    // 表头 end
                    $('#theadCpm').html(theadCpmRawHtml)
    
                    // 处理中间的checkbox
                    let skuHtml =''
                    let skus =  shops[0]['shop_skus']

                    // console.log(skus)
                    for (let k = 0; k < skus.length; k++) {
                        skuHtml += `
                        <tr class="tbody_tr" data-sku_id="`+skus[k]['sku_id']+`" data-index="`+k+`">
                            <td class="text-center"><img src="`+domain+skus[k]['sku_image']+`" style="width:30px;height:30px;"></td>
                            <td class="text-center">`+skus[k]['sku_code']+`</td>
                            <td class="text-center">`+skus[k]['sku_name']+`</td>
                            `+tbodyCheckbox+`
                        </tr>
                            `
                    }
                    // 表格内容
                    $('#tbodyCpm').html(skuHtml)

                    // 循环判断每个checkbox是否应该被选中
                    $.each($('.cpm_is_checked'), function (indexInArray, valueOfElement) { 
                         let currentSkuid = $(valueOfElement).parent().parent().data('sku_id')
                         let currentSkuIndex = $(valueOfElement).parent().parent().data('index')
                        //  dataObj = {shop_id: 1, cpm_1__sku_in_shop_state: 10, cpm_1__sku_id: 23, cpm_0__sku_in_shop_state: 10, cpm_0__sku_id: 22}
                        let dataObj = $(valueOfElement).data()
                        Object.keys(dataObj).forEach(function(key){

                            // console.log(key,dataObj[key])
                            
                            // shop_id 1
                            // 1__sku_in_shop_state 10
                            // 1__sku_id 23
                            // 1__shop2_id 16
                            // 0__sku_in_shop_state 10
                            // 0__sku_id 22
                            // 0__shop2_id 12
                            if(key.split('__').length == 2){
                                let tem_index = key.split('__')[0]   //  0/1 /...
                                if (tem_index == currentSkuIndex){
                                    // 是否选中
                                    if(key.split('__')[1].indexOf('shop_state')!= -1){
                                        if(dataObj[key] == 10){

                                        }else if(dataObj[key] == 11){
                                            $(valueOfElement).prop('checked','true')
                                        }
                                    }else if(key.split('__')[1].indexOf('shop2_id')!= -1){
                                        // console.log(dataObj[key])
                                        $(valueOfElement).data('shop2_id',dataObj[key])
                                    }
                                }
                            }
                       });


                    });

                }else{
                    window.messageBox.show(response['msg'])
                }
            },
            error:function (response) {  
            }
        });
    })

    // // 获取所有店铺
    


}
/*********************************************************** */
// 获取所有的店铺列表，用于第一次上架
function getAllShop(callback) {  
    $.ajax({
        type: "post",
        url: "/sale/get_good_sku/",
        success: function (response) {
            if(response['code']=='0'){
                sessionStorage.setItem('shops',response['shops'])
                callback()
            }else{
                // window.messageBox.show(response['msg'])
            }
        },
        error:function (response) {  
        }
    });
}
// 获取所有的店铺列表，用于后续的修改上架
function getAllShopAndskus(good_id,callback) {  
    $.ajax({
        type: "put",
        url: "/sale/get_good_sku/",
        data: {'good_id':good_id},
        success: function (response) {
            // console.log(response)
            if(response['code']=='0'){
                sessionStorage.setItem('shops_skus',response['shops'])
                callback()
            }else{
                // window.messageBox.show(response['msg'])
            }
        },
        error:function (response) {  
        }
    });
}


//  控制全选和全部选
function cpmShopAddSkuSelectAllorNotAll(event) {  
    let shop_id = $(event).data('shop_id')
    if($(event).hasClass('add')){
        $('.shop__'+shop_id).prop('checked','')
        $(event).removeClass('add')
    }else{
        $(event).addClass('add')
        $('.shop__'+shop_id).prop('checked','true')
    }
    
}

// $('.1a22a2a').prop('checked')

// 上架确认事件
function shangjiaModalClose(event) {  
    if($('#shangjiaButtonComfirm').hasClass('disabled')){
        return false
    }
    // 是第一次上架还是编辑  0 1
    let checkIsEditOrAdd = $('#checkIsEditOrAdd').val()

    let good_id = $('#shangjiaGoodId').val()

    // 构造sku与店铺的关系
    let finallArray = []
    $.each($('#tbodyCpm .tbody_tr'), function (indexInArray, value) { 
        let finallyObj = {}
        let sku_id = $(value).data('sku_id')
        // let finallyObj = {'sku_id':sku_id}
        let shopArray = []
        $.each($(value).find('td'), function (indexInArray2, valueOfElement) { 
            if($(valueOfElement).hasClass('sku-shop')){
                let shopObj = {}
                let is_checked = $(valueOfElement).children('input').prop('checked')  // true false
                let shop_id = $(valueOfElement).children('input').data('shop_id')
                let shop2_id = $(valueOfElement).children('input').data('shop2_id')
                shopObj['is_checked'] = is_checked
                shopObj['shop_id'] = shop_id
                shopObj['shop2_id'] = shop2_id
                shopArray.push(shopObj)
            }
        })
        finallyObj['sku_id'] = sku_id
        finallyObj['result'] = shopArray
        finallArray.push(finallyObj)
    })

    let csrfTokenValue = $("input[name='csrfmiddlewaretoken']").val()
    let data = {
        'good_id':good_id,
        'sku_shop':JSON.stringify(finallArray),
        'csrfmiddlewaretoken':csrfTokenValue,
    }

    // console.log(data)
    if(checkIsEditOrAdd == 0){
        ReloadAjax('post',data,"/sale/shangjia/",'shangjiaButtonComfirm','shangjiaModal')
    }else if(checkIsEditOrAdd == 1){
        ReloadAjax('post',data,"/sale/shangjia_edit/",'shangjiaButtonComfirm','shangjiaModal')
    }

}



/*************************** */
// 上架条件查询
function exeShangjiaQuery(event) {  

    let urlQuery = $(event).data('query-url')
    let code = $('#pl-code').val()
    let name = $('#pl-name').val()
    let pinlei = $('#pl-pinlei').val()
    let chargers = $('#pl-charger').find("option:selected").val()
    let suppilerIds = $('#pl-supplier').data('id')
    let suppilerVal = $('#pl-supplier').val()
    let jibie =$('#pl-tag-jibie').find("option:selected").val()
    
    // 新的查询条件   入库
    let ruku_start = $('#pl-ruku_start').val()
    let ruku_end = $('#pl-ruku_end').val()
    let ruku_state =$('#pl-ruku_state').find("option:selected").val()
    // 制作
    let zhizuo_start = $('#pl-zhizuo_start').val()
    let zhizuo_end = $('#pl-zhizuo_end').val()
    let zhizuo_state =$('#pl-zhizuo_state').find("option:selected").val()

    // 店铺上架
    let un_shop =$('#pl-un_shop').find("option:selected").val()
    let do_shop =$('#pl-do_shop').find("option:selected").val()
    let never_shangjia =$('#pl-never_shangjia').prop('checked')  // true false
    let flag = $('#exportCSV').data('flag')

    let data = {
        'code':code,
        'name':name,
        'pinlei':pinlei,
        'jibie':jibie,
        'chargers':chargers,
        'suppliers':suppilerIds,
        'suppiler_val':suppilerVal,
        'ruku_start':ruku_start,
        'ruku_end':ruku_end,
        'ruku_state':ruku_state,
        'zhizuo_start':zhizuo_start,
        'zhizuo_end':zhizuo_end,
        'zhizuo_state':zhizuo_state,
        'un_shop':un_shop,
        'do_shop':do_shop,
        'never_shangjia':never_shangjia,
        'flag':flag,
    }

    $('#exportCSV').data('flag',0)

    // 统一执行这个函数 导出csv
    exportCsvBase(urlQuery,data,flag)

}



function getShangjiaSkus() {  
    let goodIds = []
    $.each($('.good_id'), function (indexInArray, valueOfElement) { 
        goodIds.push($(valueOfElement).data('good_id'))
    });
    console.log(goodIds)
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