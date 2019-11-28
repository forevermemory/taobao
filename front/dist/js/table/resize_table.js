/**
 * 
 * description
 * Reset the table width according to history
 * depend on  colResizable-1.6.min.js
 */


$(document).ready(function($) {

    // 表格可拖动
    $(".cpmTable").colResizable({
        liveDrag:true, 
        gripInnerHtml:"<div class='grip'></div>", 
        draggingClass:"dragging", 
        postbackSafe: true,//刷新后保留之前的拖拽宽度
        resizeMode:'fit',
        onResize:onSampleResized,   // 执行拖拽后回调函数,记录该用户在该页面的表格信息
    })
    // 重置当前表格的宽度
    resizeTableWidth()

});


// 初始化根据历史重新规划表格宽度
function resizeTableWidth() {  
    let user_id = $('#base_user_id').data('user_id')
    let pathname = location.pathname

    let widthObj =  JSON.parse(localStorage.getItem(pathname+user_id))
    if (widthObj == undefined){
        return false
    }
    let ths = $('.cpmTable').find('thead').find('th')


    $.each($(ths), function (indexInArray, valueOfElement) { 
        $(valueOfElement).attr('style',widthObj[indexInArray])
    })
}

// 执行拖拽后回调函数
function onSampleResized() {  
    let ths = $('.cpmTable').find('thead').find('th')
    let user_id = $('#base_user_id').data('user_id')
    let pathname = location.pathname

    let widthObj = {}
    $.each($(ths), function (indexInArray, valueOfElement) { 
        widthObj[indexInArray] = $(valueOfElement).attr('style')
    });
    localStorage.setItem(pathname+user_id,JSON.stringify(widthObj))
}
