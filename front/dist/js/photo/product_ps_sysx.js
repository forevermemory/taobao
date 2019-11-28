// $(document).ready(function($) {
// });

$(function () {
    // 初始化日期弹框
    $('#photoSYSXGoodJdate').cxCalendar()
    $('#photoSYSXGoodRealdate').cxCalendar()

   
    
})


// 摄影摄像的条件查询
function exeQuerySYSX(event) {  
    let urlQuery = $(event).data('query-url')
    let code = $('#pl-code').val()
    let name = $('#pl-name').val()
    let pinlei = $('#pl-pinlei').val()
    let genzonger = $('#pl-charger').find("option:selected").val()
    let suppilerIds = $('#pl-supplier').data('id')
    let suppilerVal = $('#pl-supplier').val()
    let jibie =$('#pl-tag-jibie').find("option:selected").val()
    let start = $('#pl-start').val()
    let end = $('#pl-end').val()
    let flag = $('#exportCSV').data('flag')
 
    // 是否展开扩展查询   默认为true 隐藏
    let data = {
        'p':1,
        'code':code,
        'name':name,
        'pinlei':pinlei,
        'genzonger':genzonger,
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
/****************************** */

/*********************************** */
// 拍摄交付弹出框
function photoPSJFBtnClick(event) {  
    let pid = $(event).data('id')
    let code = $(event).data('code')
    let name = $(event).data('name')
    let photo_id = $(event).data('photo_id')
    let genzonger_name = $(event).data('genzonger_name')
    let good_photo_method_name = $(event).data('good_photo_method_name')
    let kuaidi_edate = $(event).data('kuaidi_edate')
    $('#photoSYSXGoodId').val(pid)
    $('#photoSYSXGoodPhotoId').val(photo_id)
    $('#photoSYSXGoodName').val(name)
    $('#photoSYSXGoodCode').val(code)
    $('#photoSYSXGoodTraker').val(genzonger_name)
    $('#photoSYSXGoodPhotoMethod').val(good_photo_method_name)
    $('#photoSYSXGoodExpectFinishDate').val(kuaidi_edate)
    $('#photoSYSXModal').modal('show')
    $('#photoSYSXButtonComfirm').text('保存')
    $('#photoSYSXButtonComfirm').removeClass('disabled')

}
// 拍摄交付弹出框确定事件
function photoSYSXButtonComfirmEvent(event) {
    if($('#photoSYSXButtonComfirm').hasClass('disabled')){
        return false
    }
    
    
    let desc = $('#photoSYSXGoodDesc').val()
    let good_id = $('#photoSYSXGoodId').val()
    let good_photo_id = $('#photoSYSXGoodPhotoId').val()
    let readDate = $('#photoSYSXGoodRealdate').val()
    if(readDate == ''){
        $('#photoSYSXGoodRealdate').focus()
        window.messageBox.show('请填写实际交付日期')
        return false
    }
    
    $('#photoSYSXButtonComfirm').text('操作中')
    $('#photoSYSXButtonComfirm').addClass('disabled')
    let csrfTokenValue = $("input[name='csrfmiddlewaretoken']").val()

    let data = {
        'csrfmiddlewaretoken':csrfTokenValue,
        'desc':desc,
        'real_date':readDate,
        'good_id':good_id,
        'good_photo_id':good_photo_id,
    }

    ReloadAjax('post',data,"/photo/sysx/",'photoSYSXButtonComfirm','photoSYSXModal') 



}


