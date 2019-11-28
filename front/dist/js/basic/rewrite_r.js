$(document).ready(function($) {
    // console.log(1)
    // $('#reservation').daterangepicker()
    // $('#reservation').val('')
});



// 点击分析
$('#Analyse').click(function (e) { 
    var that = $(this)
    that.text('正在分析中,请稍后。。')
    
    setTimeout(() => {
        that.text('点击分析')
        $('#AnalyseSuccess').removeClass('hidden')
        that.addClass('hidden')
        
    }, 3000);
});

// 四个按钮点击加或者减
$('#buttonP1').click(function (e) { 
    var value = $('#param1').val()
    var intValue = parseInt(value)
    if (intValue == NaN){
        intValue = 1
    }
    intValue++
    $('#param1').val(intValue)
});
$('#buttonP2').click(function (e) { 
    var value = $('#param1').val()
    var intValue = parseInt(value)
    if (intValue == NaN){
        intValue = 1
    }
    intValue--
    if(intValue<=0){
        intValue = 1
    }
    $('#param1').val(intValue)
    
});
$('#buttonN1').click(function (e) { 
    var value = $('#param2').val()
    var intValue = parseInt(value)
    if (intValue == NaN){
        intValue = 0
    }
    intValue++
    $('#param2').val(intValue)
    
});
$('#buttonN2').click(function (e) { 
    var value = $('#param2').val()
    var intValue = parseInt(value)
    if (intValue == NaN){
        intValue = 0
    }
    intValue--
    if(intValue<=0){
        intValue = 0
    }
    $('#param2').val(intValue)
});

// 两个输入框失去焦点事件
$('#param1').blur(function (e) { 
    isNaN(parseInt($(this).val())) ? $(this).val('1') : $(this).val(parseInt($(this).val()))
});
$('#param2').blur(function (e) { 
    isNaN(parseInt($(this).val())) ? $(this).val('2') : $(this).val(parseInt($(this).val()))
});