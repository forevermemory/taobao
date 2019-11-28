

$(document).ready(function($) {
    // 初始化日期选择框
    $('#pl-start-fp').cxCalendar()
    $('#pl-end-fp').cxCalendar()
    $('#pl-start-tj').cxCalendar()
    $('#pl-end-tj').cxCalendar()
    $('#photoMGZZGoodFenpeiMakerDate').cxCalendar()
});

// 分货点货的条件查询
function exeQueryMGZZ(event) {  
    let urlQuery = $(event).data('query-url')
    let code = $('#pl-code').val()
    let name = $('#pl-name').val()
    let pinlei = $('#pl-pinlei').val()
    let chargers = $('#pl-charger').find("option:selected").val()
    let suppilerIds = $('#pl-supplier').data('id')
    let suppilerVal = $('#pl-supplier').val()
    let jibie =$('#pl-tag-jibie').find("option:selected").val()
    
    // 新的查询条件   分配 提交
    let start_fp = $('#pl-start-fp').val()
    let end_fp = $('#pl-end-fp').val()
    let start_tj = $('#pl-start-tj').val()
    let end_tj = $('#pl-end-tj').val()
    
    // 详情制作人 美工 
    let meigong =$('#pl-mk-detailer').find("option:selected").val()
    let mk_state =$('#pl-mk-state').find("option:selected").val()

    let flag = $('#exportCSV').data('flag')

    let data = {
        'code':code,
        'name':name,
        'pinlei':pinlei,
        'chargers':chargers,
        'suppliers':suppilerIds,
        'suppilerVal':suppilerVal,
        'start_fp':start_fp,
        'end_fp':end_fp,
        'start_tj':start_tj,
        'end_tj':end_tj,
        'jibie':jibie,
        'meigong':meigong,
        'mk_state':mk_state,
        'flag':flag,
    }
    $('#exportCSV').data('flag',0)
    // 统一执行这个函数 导出csv
    exportCsvBase(urlQuery,data,flag)


}
/****************************** */

/*********************************** */
// 分配弹出框
function photoPSJFBtnClick(event) {  
    let pid = $(event).data('id')
    let code = $(event).data('code')
    let name = $(event).data('name')
    $('#photoMGZZGoodIdFenpeiMake').val(pid)
    $('#photoMGZZGoodNameFenpeiMake').val(name)
    $('#photoMGZZGoodCodeFenpeiMake').val(code)


    $('#photoMGZZFenpeiMakerModal').modal('show')
    $('#photoMGZZFenpeiMakerButtonComfirm').text('确认')
    $('#photoMGZZFenpeiMakerButtonComfirm').removeClass('disabled')

}
// 分配弹框结束事件
function photoMGZZFenpeiMakerButtonComfirmEvent() {  
    if($('#photoMGZZFenpeiMakerButtonComfirm').hasClass('disabled')){
        return false
    }
    let good_id = $('#photoMGZZGoodIdFenpeiMake').val()
    let maker = $('#photoStartGoodFenpeiMaker').find("option:selected").val()
    let fenpei_date = $('#photoMGZZGoodFenpeiMakerDate').val()
    let fenpei_desc = $('#photoMGZZGoodFenpeiMakerDesc').val()
    // 校验数据是否合理
    if(maker==''){
        $('#photoStartGoodFenpeiMaker').focus()
        window.messageBox.show('请选择制作人')
        return false
    }


    // 整合数据
    let data = {
        'good_id':good_id,
        'maker':maker,
        'fenpei_desc':fenpei_desc,
        'fenpei_date':fenpei_date,
    }
    ReloadAjax('get',data,"/photo/mgzz_fenpei/",'photoMGZZFenpeiMakerButtonComfirm','photoMGZZFenpeiMakerModal') 

 


}
/**************************************************** */
// 提交弹框
function photoPSJFSubmitBtnClick(event) {  
    let good_id = $(event).data('id')
    let mgzz_id = $(event).data('mgzz_id')

    $('#mgzz2GoodId').val(good_id)
    $('#mgzz2MGZZID').val(mgzz_id)

    $('#photoMGZZSubmitModal').modal('show')
    $('#photoMGZZSecondSubmitButtonComfirm').text('确认')
    $('#photoMGZZSecondSubmitButtonComfirm').removeClass('disabled')
}


// 提交弹框结束事件
function photoMGZZSecondButtonComfirmEvent() {  

    if($('#photoMGZZSecondSubmitButtonComfirm').hasClass('disabled')){
        return false
    }
    let good_id = $('#mgzz2GoodId').val()
    let mgzz_id = $('#mgzz2MGZZID').val()
    let csrfTokenValue = $("input[name='csrfmiddlewaretoken']").val()
    let data = {
        'csrfmiddlewaretoken':csrfTokenValue,
        'good_id':good_id,
        'mgzz_id':mgzz_id,
    }

    ReloadAjax('post',data,"/photo/mgzz_fenpei/",'photoMGZZSecondSubmitButtonComfirm','photoMGZZSubmitModal') 

 


}
/***************************************************** */
// 审核弹框
function photoPSJFCheckBtnClick(event) {  
    let good_id = $(event).data('id')
    let code = $(event).data('code')
    let name = $(event).data('name')
    let mgzz_id = $(event).data('mgzz_id')

    $('#photoMGZZCheckGoodId').val(good_id)
    $('#photoMGZZMGZZGoodId').val(mgzz_id)
    $('#photoMGZZCheckGoodCode').val(code)
    $('#photoMGZZCheckGoodName').val(name)



    $('#photoMGZZCheckModal').modal('show')
    $('#photoMGZZCheckButtonComfirm').text('确认')
    $('#photoMGZZCheckButtonComfirm').removeClass('disabled')
}

//审核结束
function photoMGZZButtonComfirmEvent() {  

    if($('#photoMGZZCheckButtonComfirm').hasClass('disabled')){
        return false
    }

    let good_id = $('#photoMGZZCheckGoodId').val()
    let mgzz_id = $('#photoMGZZMGZZGoodId').val()
    let check = $('#photoGoodMGZZCheck').find("option:selected").val()
    let check_desc = $('#photoMGZZCheckGoodDesc').val()

    // 判断是否合理
    if(check == '1'){
        if(check_desc==''){
            $('#photoMGZZCheckGoodDesc').focus()
            window.messageBox.show('不通过时请填写说明')
            return false
        }
    }

    let data = {
        'good_id':good_id,
        'mgzz_id':mgzz_id,
        'check':check,
        'check_desc':check_desc,
    }
    ReloadAjax('put',data,"/photo/mgzz_fenpei/",'photoMGZZCheckButtonComfirm','photoMGZZCheckModal') 




}








