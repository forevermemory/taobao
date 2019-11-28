$(function () {
    // 点击出现选择仪表盘

    // 是否是品类管理
    var isAddCate = $('#isAddCate').val()
    var data = {}
    isAddCate == '1' ? data['is_cate'] = 1 : data['is_cate'] = ''

    // sessionStorage.removeItem('liandongPathIdArray')
    $(".qrm-input-border").click(function () {
            $(".qrm-pinming-panel").show();

            if (isAddCate !=''){
                var MarLeft = $('.qrm-pinming-panel').width() / 2 - $('#p-pinlei').width() / 2
                $(".qrm-pinming-panel").css('left','-'+MarLeft+'px')
            }
            
            // 查询所有的一级分类
            $.ajax({
                type: "get",
                url: "/select/cpm_category/",
                data: data,
                success: function (response) {
                    $('.qrm-lev-1').html('')
                    sessionStorage.setItem('firstCategory',response['items'])
                    let items = JSON.parse(response['items'])
                    // console.log(items.length)
                    items.forEach(element => {
                        $('.qrm-lev-1').append(
                            ` <li class="" data-first-id=`+element.pk+` id=`+element.pk+` >
                                    <span style="vertical-align: inherit;">`+element.fields.name+`</span>
                                    <i class="qrm-arrow-right"></i>
                                    <ul class="li-zi-1" style="display:none">
                                        
                                    </ul>
                                </li>`
                        )
                    });

                    /*下面是新增*/
                    if(isAddCate){
                        console.log('is cate')
                        var cateId = $('#isAddCateId').val()
                        firstLiandongAutoScroll(cateId)
                    }
                    // 是否需要点击
                    let liandongPathIdArray = JSON.parse(sessionStorage.getItem('liandongPathIdArray'))
                    if(liandongPathIdArray){
                        liandongAutoScroll(1,liandongPathIdArray[0])
                        if(liandongPathIdArray.length>1){
                            $('#'+liandongPathIdArray[0]).click()
                        }
                    }
                    return false
              
                }
            });

    });
    var lev1;
    var lev2;
    var lev3;
    var lev4;

    // 一级点击
    $("body").on("click",".qrm-lev-1>li",function () {
        // 为自己添加背景样式
        $(this).addClass("active").siblings("li").removeClass("active");
        lev1="";
        lev2="";
        lev3="";
        lev4="";
        var html1 = ''
        // 根据 id 去查询二级分类
        let firstId = $(this).data('first-id')
        let that = $(this)

        var isAddCate = $('#isAddCate').val()
        var data = {}
        isAddCate == '1' ? data['is_cate'] = 1 : data['is_cate'] = ''
        data['first'] = firstId
        
        $.ajax({
            type: "get",
            url: "/select/cpm_category/",
            data: data,
            success: function (response) {
                // sessionStorage.setItem('secondCategory',response['items'])
                let items = JSON.parse(response['items'])
                // 判断有没有二级分类
                if (items.length==0){
                    lev1=that.children("span").text();
                    $(".qrm-input").val(lev1);
                    $(".qrm-input").data('final-id',firstId)
                    $(".qrm-input").data('all-id',firstId)
                    $(".qrm-pinming-panel").hide();
                    return false
                }
                items.forEach(element => {
                    html1 +=
                        ` <li class="" data-second-id=`+element.pk+` id=`+element.pk+`>
                                <span style="vertical-align: inherit;">`+element.fields.name+`</span>
                                <i class="qrm-arrow-right"></i>
                                <ul class="li-zi-2" style="display:none">
                                    
                                </ul>
                            </li>`
                    
                });
                $(".qrm-lev-2").html(html1);
                $(".qrm-lev-3").html("");
                $(".qrm-lev-4").html("");
                lev1=that.children("span").text();
                $(".qrm-input").val(lev1)
                $(".qrm-input").data('all-id',firstId)
                // 是否需要点击
                let liandongPathIdArray = JSON.parse(sessionStorage.getItem('liandongPathIdArray'))
                if(liandongPathIdArray){
                    liandongAutoScroll(2,liandongPathIdArray[1])
                    if(liandongPathIdArray.length>2){
                        $('#'+liandongPathIdArray[1]).click()
                    }
                }
                return false
            }  // ajax结束
        });
    });
    // 二级点击
    $("body").on("click",".qrm-lev-2>li",function () {
        $(this).addClass("active").siblings("li").removeClass("active");
        let secondId = $(this).data('second-id')
        let that = $(this)
        var html2=''

        var isAddCate = $('#isAddCate').val()
        var data = {}
        isAddCate == '1' ? data['is_cate'] = 1 : data['is_cate'] = ''
        data['second'] = secondId

        $.ajax({
            type: "get",
            url: "/select/cpm_category/",
            data: data,
            success: function (response) {
                // sessionStorage.setItem('thirdCategory',response['items'])
                let items = JSON.parse(response['items'])
                // 判断有没有三级分类
                if (items.length==0){
                    lev2=that.children("span").html();
                    $(".qrm-input").val(lev1+"/"+lev2);
                    $(".qrm-input").data('final-id',secondId)
                    $(".qrm-input").data('all-id',$(".qrm-input").data('all-id')+'-'+secondId)
                    $(".qrm-pinming-panel").hide();
                    return false
                }
                items.forEach(element => {
                    html2 +=
                        ` <li class="" data-third-id=`+element.pk+` id=`+element.pk+`>
                                <span style="vertical-align: inherit;">`+element.fields.name+`</span>
                                <i class="qrm-arrow-right"></i>
                                <ul class="li-zi-3" style="display:none">
                                    
                                </ul>
                            </li>`
                    
                });
                lev2=that.children("span").html();
                $(".qrm-lev-3").html(html2);
                $(".qrm-lev-4").html("");
                $(".qrm-input").val(lev1+"/"+lev2)
                $(".qrm-input").data('all-id',$(".qrm-input").data('all-id')+'-'+secondId)

                let liandongPathIdArray = JSON.parse(sessionStorage.getItem('liandongPathIdArray'))
                if(liandongPathIdArray){
                    liandongAutoScroll(3,liandongPathIdArray[2])
                    if(liandongPathIdArray.length>3){
                        $('#'+liandongPathIdArray[2]).click()
                    }
                }
            }
        });
    });
    // 三级点击
    $("body").on("click",".qrm-lev-3>li",function () {
        $(this).addClass("active").siblings("li").removeClass("active");
        let that = $(this)
        let thirdId = $(this).data('third-id')
        var html3=''

        var isAddCate = $('#isAddCate').val()
        var data = {}
        isAddCate == '1' ? data['is_cate'] = 1 : data['is_cate'] = ''
        data['third'] = thirdId

        $.ajax({
            type: "get",
            url: "/select/cpm_category/",
            data:data,
            success: function (response) {
                // sessionStorage.setItem('fouthCategory',response['items'])
                let items = JSON.parse(response['items'])
                // 判断有没有四级分类
                if (items.length==0){
                    lev3=that.children("span").html();
                    $(".qrm-input").val(lev1+"/"+lev2+"/"+lev3);
                    $(".qrm-input").data('final-id',thirdId)
                    $(".qrm-input").data('all-id',$(".qrm-input").data('all-id')+'-'+thirdId)
                    $(".qrm-pinming-panel").hide();
                    return false
                }
                items.forEach(element => {
                    html3 +=
                        ` <li class="" data-forth-id=`+element.pk+` id=`+element.pk+`>
                                <span style="vertical-align: inherit;">`+element.fields.name+`</span>
                                <ul class="li-zi-4" style="display:none">
                                    
                                </ul>
                            </li>`
                    
                });
     
                lev3=that.children("span").html();
                $(".qrm-lev-4").html(html3);
                $(".qrm-input").val(lev1+"/"+lev2+"/"+lev3)
                $(".qrm-input").data('all-id',$(".qrm-input").data('all-id')+'-'+thirdId)

                let liandongPathIdArray = JSON.parse(sessionStorage.getItem('liandongPathIdArray'))
                if(liandongPathIdArray){
                    liandongAutoScroll(4,liandongPathIdArray[3])
                }
            }
        });
    });
    // 四级
    $("body").on("click",".qrm-lev-4>li",function () {
        $(this).addClass("active").siblings("li").removeClass("active");
        let that = $(this)
        let forthId = $(this).data('forth-id')
        lev4=$(this).children("span").html();
        console.log(lev4)
        $(".qrm-input").data('final-id',forthId)
        $(".qrm-input").data('all-id',$(".qrm-input").data('all-id')+'-'+forthId)
        $(".qrm-input").val(lev1+"/"+lev2+"/"+lev3+"/"+lev4);
        $(".qrm-pinming-panel").hide();

    });

    // $("body").on("click",".qrm-lev>li",function () {
    //     if($(this).parent().parent().next().children(".qrm-lev").html()==""){
    //         $(".qrm-pinming-panel").hide();
    //         $(".qrm-pinming").css("background-image","url(/static/images/product/qrm-arrow-down.png)");
    //     }

    // })
});



function liandongAutoScroll(indexparam,$Id) {  
    // let firstCategory = JSON.parse(sessionStorage.getItem('firstCategory'))
    $.each($('.qrm-lev-'+indexparam+' li'), function (index, value) { 
        if($(value).attr('id') == $Id){
            // $(value).siblings().removeClass('active')
            $(value).addClass('active')
            // $(value).addClass('active').siblings().removeClass('active')
            var sTop = (index-1)*40
            var nowScrollTop=$('.qrm-lev-'+indexparam).scrollTop();//当前已经滚动了多少
            $('.qrm-border'+indexparam).stop(true).animate({"scrollTop":sTop+nowScrollTop},400);
            return
        }
    });
}


