// $(document).ready(function($) {
// });

$(function () {
    // 初始化日期弹框
    $('#photoStartGoodJdate').cxCalendar()
    $('#photoStartGoodEdate').cxCalendar()

    // 拍摄准备的校验
    $('#photoStartForm').bootstrapValidator({
        message: 'This value is not valid',
    　feedbackIcons: {
            valid: 'glyphicon glyphicon-ok',
            invalid: 'glyphicon glyphicon-remove',
            validating: 'glyphicon glyphicon-refresh'
        },
        fields: {
            'good_id': {
                validators: {
                    notEmpty: {
                        message: '编码不能为空'
                    },
                }
            },
        },
        submitHandler: function (validator, form, submitButton) {
            console.log("submit")
        }
    })
    .on('success.form.bv', function (e) { //点击提交验证通过之后
        e.preventDefault();
        $('button[type="submit"]').removeAttr("disabled")
        if($('#photoStartGoodEdate').val()==''){
            window.messageBox.show('预计完成日期不能为空')
            return false
        }
        // var flag = $('#form').data("bootstrapValidator").isValid();//校验合格
        var $form = $(e.target)
        // var bv = $form.data('bootstrapValidator')  data('bootstrapValidator')
        var data = $form.serialize()  // 用于不附带文件直接上传

        ReloadAjax('post',data,"/photo/start/",'photoStartButtonComfirm','photoStartModal') 

 

    })


    // 
    
})

// 拍摄准备弹出框
function photoStartIndexBtnClick(event) {  
    let pid = $(event).data('id')
    let code = $(event).data('code')
    let name = $(event).data('name')
    $('#photoStartGoodId').val(pid)
    $('#photoStartGoodCode').val(code)
    $('#photoStartGoodName').val(name)
    $('#photoStartModal').modal('show')
    $('#photoStartButtonComfirm').text('保存')
    $('#photoStartButtonComfirm').removeClass('disabled')

}
// 不拍摄弹出框
function photoNotStartBtnClick(event) {  
    let pid = $(event).data('id')
    let code = $(event).data('code')
    let name = $(event).data('name')
    $('#photoStartGoodId2').val(pid)
    $('#photoStartGoodCode2').val(code)
    $('#photoStartGoodName2').val(name)
    $('#photoNotPhotoStartModal').modal('show')
    $('#photoNotStartButtonComfirm').text('确定')
    $('#photoNotStartButtonComfirm').removeClass('disabled')
    
}
// 不拍摄确定事件
function photoNotPhotoStartModalClose() {
    if($('#photoNotStartButtonComfirm').hasClass('disabled')){
        return false
    }
    let good_id = $('#photoStartGoodId2').val()
    let data =  {
        'good_id':good_id,
        'csrfmiddlewaretoken': $("input[name='csrfmiddlewaretoken']").val()
    }
    ReloadAjax('delete',data,"/photo/start/",'photoNotStartButtonComfirm','photoNotPhotoStartModal') 

    
}




// 拍摄准备的条件查询
function exeQueryPaisheZhunbei(event) {  
    
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
        // 'p':1,
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