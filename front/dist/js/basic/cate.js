$(document).ready(function($) {

});




//




// 修改源码  给span添加点击事件
function cpmCateDel(event){
    var that = $(event)
    var cateIdTree = that.siblings('a').attr('href').replace('#','').split(',')
    var cateId = cateIdTree[cateIdTree.length-1]

    if(that.text() == '删除'){
        $('#deleteCateModal').modal('show')
        $('#confirmDelCateHidId').data('id',cateId)
        
    }else if(that.text() == '添加品类'){
        $('#selectCate').modal('show')
        $(".qrm-pinming-panel").hide()
        $("#p-pinlei").val('')
        $("#p-pinlei").data('all-id','')
        $("#p-pinlei").data('final-id','')
        $('#isAddCateId').val(cateId)
        sessionStorage.setItem('liandongPathIdArray',JSON.stringify(cateIdTree))
    }
}

// 确认删除
function deleteCateConfirmEvent(){
    if($('#deleteCateConfirm').hasClass('disabled')){
        return false
    }
    
    let data = {
        'cate_id':$('#confirmDelCateHidId').data('id'),
    }
    let url = '/basic/cate/'
    ReloadAjax('delete',data,url,'deleteCateConfirm','deleteCateModal')
}
 

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

$('#downloadCateCSV').click(function (e) { 
    e.preventDefault()
    window.location.href = window.location.pathname + '?is_export=1'
});

