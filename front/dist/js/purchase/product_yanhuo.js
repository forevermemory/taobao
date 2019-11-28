$(document).ready(function($) {
	// 初始化日期插件
    $('#yanhuoGoodRealArrivaldate').cxCalendar()
});


// 鼠标悬停显示备注
function yanhuoDescExpend(event) {  
    $(event).popover('show')
}
function yanhuoDescReduce(event) {  
    $(event).popover('hide')
}


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


// 验货弹出框
function yanhuoBtnClick(event) {  
    let pid = $(event).data('id')
    let code = $(event).data('code')
    let name = $(event).data('name')
    let charger = $(event).data('charger')
    let c_date = $(event).data('c_date')
    let desc = $(event).data('caigou_desc')

    $('#yanhuoGoodId').val(pid)
    $('#yanhuoGoodCode').val(code)
    $('#yanhuoGoodName').val(name)
    $('#yanhuoGoodPurchaser').val(charger)
    $('#yanhuoGoodCdate').val(c_date)
    $('#yanhuoGoodDesc').val(desc)
    $('#yanhuoModal').modal('show')
    $('#yanhuoButtonComfirm').text('保存')
    $('#yanhuoButtonComfirm').removeClass('disabled')

}

// 点货分货弹出框结束
function yanhuoModalClose(event) {  
    if($('#yanhuoButtonComfirm').hasClass('disabled')){
        return 
    }

    let yanhuoGoodId = $('#yanhuoGoodId').val()
    let yanhuoGoodPurchaser = $('#goodyanhuoUser').find("option:selected").val()
    // 验货结果
    let goodyanhuoDetail = $('#goodyanhuoDetail').find("option:selected").val()
    let GoodyanhuoDesc = $('#GoodyanhuoDesc').val()

    var GoodyanhuoPicture = $('#GoodyanhuoPicture')[0].files
    var GoodyanhuoVideo = $('#GoodyanhuoVideo')[0].files
    // 新加的逻辑判断   如果点货结果为缺货 发错货 其他 desc必须填写
    if(goodyanhuoDetail== '2'){
        if(GoodyanhuoDesc==''){
            window.messageBox.show('请填写备注信息')
            $('#GoodyanhuoDesc').focus()
            return false
        }
        if(GoodyanhuoVideo['length'] != 0 ){
            checkUploadVideoIsVaild(GoodyanhuoVideo)
        }
        
        if(GoodyanhuoPicture['length'] != 0){
            checkUploadImagesIsVaild(GoodyanhuoPicture)
        }
        if(GoodyanhuoPicture['length'] != 0 && GoodyanhuoVideo['length'] != 0){
            checkUploadVideoIsVaild(GoodyanhuoVideo)
            checkUploadImagesIsVaild(GoodyanhuoPicture)
        }

    }else if(goodyanhuoDetail== '1'){
        // 不合格 必须要上传图片或者视频
        if(GoodyanhuoVideo['length'] == 0 && GoodyanhuoPicture['length'] == 0 ){
            window.messageBox.show('不合格时候,请上传图片或者视频')
            return false
        }
        if(GoodyanhuoVideo['length'] != 0 ){
            checkUploadVideoIsVaild(GoodyanhuoVideo)
        }
        
        if(GoodyanhuoPicture['length'] != 0){
            checkUploadImagesIsVaild(GoodyanhuoPicture)
        }
        if(GoodyanhuoPicture['length'] != 0 && GoodyanhuoVideo['length'] != 0){
            checkUploadVideoIsVaild(GoodyanhuoVideo)
            checkUploadImagesIsVaild(GoodyanhuoPicture)
        }
     
    }


    // 构建带文件的ajax
    var formData = new FormData()
    formData.append('csrfmiddlewaretoken', $("input[name='csrfmiddlewaretoken']").val())
    for (let l = 0; l <GoodyanhuoPicture['length']; l++) {
        formData.append('images', GoodyanhuoPicture[l])
    }
    formData.append('video', GoodyanhuoVideo[0])
    formData.append('desc', GoodyanhuoDesc)
    formData.append('charger', yanhuoGoodPurchaser)
    formData.append('good_id', yanhuoGoodId)
    formData.append('yanhuo_result', goodyanhuoDetail)

    FileAjax('post',formData,"/purchase/yanhuo/",'yanhuoButtonComfirm','yanhuoModal') 


}

// 检查上传图片是否合理
function checkUploadImagesIsVaild(skuImageObj) {
    // console.log()  //FileList {0: File, 1: File, 2: File, length: 3}
    let length = skuImageObj['length']
    if(parseInt(length)>5){
        window.messageBox.show('最多上传五张图片')
        return false
    }
    for (let j = 0; j < length; j++) {
        let extName = skuImageObj[j]['name'].split('.').pop()
        if(!/^(jpg|jpeg|png|JPG|PNG|JPEG)$/.test(extName)){
            window.messageBox.show('图片类型只能为jpg,png,jpeg')
            return false
        }
    }

}

function checkUploadVideoIsVaild(video) {
    let extName = video[0]['name'].split('.').pop()
    if(extName !='mp4'){
        window.messageBox.show('只支持mp4格式的视频文件')
        return false
    }
}

