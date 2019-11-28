$(document).ready(function($) {
    // console.log(1)
    // $('#reservation').daterangepicker()
    // $('#reservation').val('')
});



$('#mimportNext').click(function (e) { 
    e.preventDefault()
    // 判断文件名称和类型是否正确 
    var fileNameArray = ['供应商信息模板.xlsx','商品信息模板.xlsx']
    var fileObj = $('#mImportFile')[0].files[0]
    if(fileObj == undefined){
        window.messageBox.showError('请先上传模板!')
        return false
    }
    var fileName = fileObj['name']
    if(!(fileNameArray.indexOf(fileName) > -1)){
        window.messageBox.showError('上传文件名和模板名不匹配！')
        return false
    }

    $('#mulStep1Form').submit()
    // href="{% url 'basic:add_multi' %}?step=2" 
    // window.location.href = $(this).attr('href')
});





// 确认新增品类
function addCateCloseEvent(event) {  
    if($("#p-pinlei").data('final-id') == ''){
        window.messageBox.showError('请先选择品类!')
        return false
    }
    if($('#addCateCloseBtn').hasClass('disabled')){
        return false
    }
    var finalId = $('#p-pinlei').data('final-id')
    var pathId = $('#p-pinlei').data('all-id')
    var data = {
        'final_id':finalId,
        'path_id':pathId,
    }
    let url = '/basic/cate/'
    ReloadAjax('put',data,url,'addCateCloseBtn','selectCate')
}