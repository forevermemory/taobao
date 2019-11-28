$(document).ready(function($) {
	// 初始化模态对话框

});

// 评审弹出框
function pingShenPhaseBtnClick(event) {  
    let pid = $(event).data('id')
    let hcode = $(event).data('hcode')
    $('#pingshenGoodId').val(pid)
    $('#pingshenGoodHcode').val(hcode)
    $('#pingshenButtonComfirm').removeClass('disabled')
    $('#pingShenPhaseModal').modal('show')
}

// 评审弹出框结束
function pingShenPhaseModalClose(event) {  
    $('#pingshenButtonComfirm').text('确定')
    if($('#pingshenButtonComfirm').hasClass('disabled')){
        return 
    }
    //  1 通过　0 待定　2 终止
    let pingshenRadio = $('input[name="radios"]:checked').val()
    let wait = $('#wait_reason').find("option:selected").val()
    let cancel = $('#cancel_reason').find("option:selected").val()

    let pid = $('#pingshenGoodId').val()
    let hcode = $('#pingshenGoodHcode').val()
    let desc = $('#pingshenDesc').val()
    if (pingshenRadio == undefined){
        $('#modalTitlePingshenAlert').text('请选择评审结果!')
        return false
    }
    let csrfTokenValue = $("input[name='csrfmiddlewaretoken']").val()
    let data = {
        'csrfmiddlewaretoken':csrfTokenValue,
        'pid':pid,
        'hcode':hcode,
        'desc':desc,
        'wait':wait,
        'cancel':cancel,
        'state':pingshenRadio,
    }
    ReloadAjax('post',data,"/select/pingshen/",'pingshenButtonComfirm','pingShenPhaseModal') 
    
}



// radio变化控制元素显示和隐藏
$('input[type="radio"]').change(function (e) { 
    e.preventDefault();

    let state = e.target.value
    console.log(state)
    if(state=='2'){
        // 终止
        $('#cancel_reason_div').removeClass('hidden')
        $('#wait_reason_div').addClass('hidden')
    }else if(state=='0'){
        // 待定
        $('#cancel_reason_div').addClass('hidden')
        $('#wait_reason_div').removeClass('hidden')
    }else{
        $('#wait_reason_div').addClass('hidden')
        $('#cancel_reason_div').addClass('hidden')
    }
});