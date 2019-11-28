
$(document).ready(function($) {
    // 初始化双向选择框
    $('#multiselect').multiselect();

});

//  双向选择对话框 modal 打开获取数据事件
function ProductAddModelOpenEvent(event) {
    $('#ProductListMultiSelectModel').modal('show')
    let name = $(event).attr('name')
    $("#multiselect").empty()
    $("#multiselect_to").empty()
    $('#modalTitleQuery').text('')
    $('#supplierSearch').addClass('hidden')
    $.ajax({
        type: "get",
        url: "/select/add_one_type/",
        data: {'kind':name},
        success: function (response) {
            if(response['code'] == undefined){
                let kind = response['kind']
                if(kind=='supplier'){
                    // 增加查询功能
                    var width = $('#modalContent').width()
                    $('#supplierSearch').css('left',(width/2-75)+'px')
                    $('#supplierSearch').removeClass('hidden')

                    var suppliers = JSON.parse(response['suppliers'])
                    $('#modalTitleQuery').text('供应商')
                    
                    suppliers.forEach(element => {
                        $("#multiselect").append("<option value='" + element.pk + "'>" + element.fields.name + "</option>");
                    });
                    $('#ProductQueryModelHiddenInput').val('supplier')
                    
                }else if(kind == 'charger'){
                    let chargers = response['chargers']
                    $('#modalTitleQuery').text('负责人')
                    chargers.forEach(element => {
                        $("#multiselect").append("<option value='" + element.id + "'>" + element.name + "</option>");
                    });
                    $('#ProductQueryModelHiddenInput').val('charger')
                    
                }else if(kind == 'dingwei'){
                    let dingweis = JSON.parse(response['dingweis'])
                    $('#modalTitleQuery').text('定位')
                    dingweis.forEach(element => {
                        $("#multiselect").append("<option value='" + element.pk + "'>" + element.fields.name + "</option>");
                    });
                    $('#ProductQueryModelHiddenInput').val('dingwei')
                    
                }else if(kind =='changjing'){
                    let changjings = JSON.parse(response['changjings'])
                    $('#modalTitleQuery').text('场景')
                    changjings.forEach(element => {
                        $("#multiselect").append("<option value='" + element.pk + "'>" + element.fields.name + "</option>");
                    });
                    $('#ProductQueryModelHiddenInput').val('changjing')
                    
                }
            }
        }
    });
    
    
}


// 双向选择对话框 modal关闭事件
function ProductAddModelCloseEvent(params) {
    let kind = $('#ProductQueryModelHiddenInput').val()
    let DestVal = ''
    let DestText = ''
    $("#multiselect_to option").each((i,item)=> {
        DestVal += $(item).val()+','
        DestText += $(item).text() + ','
    })
    $('input[name="'+kind+'"]').val(DestText)
    $('input[name="'+kind+'"]').data('id',DestVal)
    $('#ProductListMultiSelectModel').modal('hide')
}


// 将价格转成两位小数
function getMoneyFloat(x){
    if (x != '.'){
      var f = Math.round(x ) / 100;
      var s = f.toString();
      var rs = s.indexOf('.');
      if (rs <= 0) {
        rs = s.length;
        s += '.';
      }
      while (s.length <= rs + 2) {
        s += '0';
      }
      return s;
    }else{
      return '0.00';
    }

}


// 鼠标悬停......显示详情
function skuDescExpend(event) {  
    $(event).popover('show')
}
function skuDescReduce(event) {  
    $(event).popover('hide')
}


// 为左侧下拉添加鼠标经过和离开事件
// onmouseenter="expendDropDown(this)" onmouseleave="reduceDropDown(this)"
    
    function expendDropDown(event) {  
       if( $(event).parent().hasClass('open')){
           setTimeout(() => {
               
               $(event).parent().removeClass('open')
           }, 200);
       }else{

           setTimeout(() => {
               
               $(event).parent().addClass('open')
           }, 200);
       }
    }
    
    function reduceDropDown(event) {  
        // setTimeout(() => {
            
        //     $(event).removeClass('open')
        // }, 200);
    }




    // 鼠标悬停放大图片
    // 
    function skuImageExpend(event) {  
        let x = $(event)[0]['x']
        let y = $(event)[0]['y']
        console.log(x)
        console.log(y)
        
    
        let imgSrc = $(event).attr('src')
        $('#sku-img-expend img').attr('src',imgSrc)
        $('#sku-img-expend').css('z-index',99999)
        $('#sku-img-expend').css('position','fixed')
        $('#sku-img-expend').css('top',0)
        $('#sku-img-expend').css('left',x+50)
        // 图片是否缩放
        $('#sku-img-expend').css('width','auto')
        $('#sku-img-expend').css('height','auto')
        $('#sku-img-expend img').css('height','100%')
        $('#sku-img-expend img').css('width','auto')
        $('#sku-img-expend img').css('max-height',document.body.clientHeight)
        $('#sku-img-expend').css('display','')
    }
    


// 鼠标离开图片
function skuImageReduce() {  
    $('#sku-img-expend').css('display','none')
    $('#sku-img-expend').children('img').attr('src','')
}
  


// 下拉箭头点击事件
function caretClick(event) {  
    let goodId = $(event).data('to')
    let $temp = '.addGoodSku'+goodId+''
    if(!$(event).hasClass('down')){
        $(event).addClass('down')
        // $($temp).removeClass('hidden')
        $($temp).fadeIn('slow')
    }else{
        $(event).removeClass('down')
        // $($temp).addClass('hidden')
        $($temp).fadeOut('slow')
    }

}



// 获取当前页面上所有的good_id
function getAllGoodId(data,callback) {  


    $.ajax({
        type: "post",
        url: "/query/",
        data: data,
        success: function (response) {
            if(response['code'] == '0'){
                callback(response['res'])
            }
        }
    });
}


// 导出csv
function exportCSV() {  
    $('#exportCSV').data('flag',1)
    
    $('#queryBtn').click()
}


// $('#multiselect').stop(true).animate({"scrollTop":'500px'},400)  20px
// background-color: rgb(38, 156, 255);

// 多选框为供应商时候出现搜索框的键盘抬起事件
$('#MultiSelectSearch').keyup(function (e) { 
    if (e.keyCode == 16 || e.keyCode == 13){
        return false
    }
    
    var value = $('#MultiSelectSearch').val().trim()
    var options = $('#multiselect').find('option')
    
    $.each($(options), function (indexInArray, valueOfElement) { 
        if($(valueOfElement).text().indexOf(value) != -1){
            $(valueOfElement).addClass('active')
            var sTop = (indexInArray-1)*20
            var nowScrollTop=$('#multiselect').scrollTop();//当前已经滚动了多少
            $('#multiselect').stop(true).animate({"scrollTop":sTop},400);
            return false
        }
        
    });
});