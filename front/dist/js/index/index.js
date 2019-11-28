
$(document).ready(function($) {
    // 初始化日期选择框
    // $('#caigouDateInput').cxCalendar()
    $('#caigouDateInput').daterangepicker()
    $('#saleDateInput').daterangepicker()

    // ajax渲染首页总览数据 
    renderIndexStatistics()

    // 默认显示前七天的统计
    getCaigouAndSaleData({'caigouDay7':'1'},'caigouDay7',(response)=>{
        drawCaigouBar(response,'caigouDay7')
        drawSaleBar(response,'saleDay7')
    })
    $('#caigouDay7').tab('show')
    $('#saleDay7').tab('show')

});

// 初始化采购的tab切换
$('#indexShangxinTab a').click(function (event) {
    var isDateRange = $(event.target).attr('id')

    // caigouDateInput
    if (isDateRange == undefined){

        let type = $(this).attr('aria-controls')
        let data = {}
        data[type] = '1'
        getCaigouAndSaleData(data,type,(response)=>{
            drawCaigouBar(response,type)
        })
        $(type).tab('show')
    }
})


// 初始化销售的tab切换
$('#indexSaleTab a').click(function (event) {
    let type = $(this).attr('aria-controls')
    type = type.replace('sale','caigou')
    let data = {}
    data[type] = '1'

    getCaigouAndSaleData(data,type,(response)=>{
        drawSaleBar(response,type)
    })
    $(type).tab('show')
})

// 新品看板日期内容变化事件
$('#caigouDateInput').change(function (e) { 
    e.preventDefault();
    console.log('get data')
    // 去服务端拿数据
    var value = $('#caigouDateInput').val()

    let data = {}
    data['dayRange'] = value
    getCaigouAndSaleData(data,'caigouCurrentDailyDiv',(response)=>{
        drawCaigouBar(response,'caigouCurrentDailyDiv')
    })
    $('#caigouCurrentDailyDiv').tab('show')


});
// 新品看板日期内容变化事件
$('#saleDateInput').change(function (e) { 
    e.preventDefault();
    console.log('get data')
    // 去服务端拿数据
    var value = $('#saleDateInput').val()

    let data = {}
    data['dayRange'] = value
    getCaigouAndSaleData(data,'saleCurrentDailyDiv',(response)=>{
        drawSaleBar(response,'saleCurrentDailyDiv')
    })
    $('#saleCurrentDailyDiv').tab('show')


});


// 采购订单
// 上架


/***********************采购的图 start******************************* */
// 获取采购阶段的数据
function getCaigouAndSaleData(data,type,callback) {  

    $.ajax({
        type: "get",
        url: "/get_caigou_echart/",
        data: data,
        success: function (response) {
            if(response['code']=='0'){
                // sessionStorage.setItem(type,JSON.stringify(response))
                setTimeout(() => {
                    
                    callback(response)
                }, 500);
            }
        },error:function () { 

        }
    });
}



// 绘制采购的条形图
function drawCaigouBar(res,elementEle) {  
    // console.log(res.data)
    // console.log(elementEle)
    let myChart = echarts.init(document.getElementById(elementEle))

    let app = {};
    option = null;
    // app.title = '堆叠柱状图';
    
    // 柱的宽度
    let BARWIDTH = 30
    if (elementEle == 'caigouDay30' || elementEle == 'caigouCurrentDailyDiv' || elementEle == 'saleCurrentDailyDiv'){
        BARWIDTH = 6
    }

    let xAxisData = []
    let caigou = []
    let ruku = []
    let paishe = []
    let zhizuo = []
    let shangjia = []
    let caigou_exceed = []
    let ruku_exceed = []
    let paishe_exceed = []
    let zhizuo_exceed = []

    // 以周或者月份为尺度
    if (res['month_week'] != undefined){
        
        JSON.parse(res.data).forEach((element,i) => {
            if (res['month_week'] == 'month'){
                xAxisData.push(element['year'] + '-' + element['month'])
            }else if (res['month_week'] == 'week'){
                xAxisData.push(element['date'])

            }
            caigou.push(element['caigou'])
            ruku.push(element['ruku'])
            paishe.push(element['paishe'])
            zhizuo.push(element['zhizuo'])
            shangjia.push(element['shangjia'])
            caigou_exceed.push(element['caigou_exceed'])
            ruku_exceed.push(element['ruku_exceed'])
            paishe_exceed.push(element['paishe_exceed'])
            zhizuo_exceed.push(element['zhizuo_exceed'])
        });

    }else{
        JSON.parse(res.data).forEach((element,i) => {
            xAxisData.push(element['fields']['date'].substr(5))
            caigou.push(element['fields']['caigou'])
            ruku.push(element['fields']['ruku'])
            paishe.push(element['fields']['paishe'])
            zhizuo.push(element['fields']['zhizuo'])
            shangjia.push(element['fields']['shangjia'])
            caigou_exceed.push(element['fields']['caigou_exceed'])
            ruku_exceed.push(element['fields']['ruku_exceed'])
            paishe_exceed.push(element['fields']['paishe_exceed'])
            zhizuo_exceed.push(element['fields']['zhizuo_exceed'])
        });
    }



    option = {
        tooltip : {
            trigger: 'axis',
            axisPointer : {            // 坐标轴指示器，坐标轴触发有效
                type : 'shadow'        // 默认为直线，可选为：'line' | 'shadow'
            }
        },
        legend: {
            data:['待采购','待入库','待拍摄','待制作','待上架','待采购超期','待入库超期','待拍摄超期','待制作超期']
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
        },
        xAxis : [
            {
                type : 'category',
                data : xAxisData,
                // 横坐标全部显示
                axisLabel : {
                    show:true,
                    interval: 0,
                    rotate: 45,
                }
            },
        ],
        yAxis : [
            {
                type : 'value'
            }
        ],
        series : [
            {
                name:'待采购',
                type:'bar',
                barWidth : BARWIDTH,
                stack: '正常',
                data:caigou
            },
            {
                name:'待入库',
                type:'bar',
                stack: '正常',
                data:ruku
            },
            {
                name:'待拍摄',
                type:'bar',
                stack: '正常',
                data:paishe
            },
            {
                name:'待制作',
                type:'bar',
                stack: '正常',
                data:zhizuo
            },
            {
                name:'待上架',
                type:'bar',
                stack: '正常',
                data:shangjia
            },
            // 第二柱
            {
                name:'待采购超期',
                type:'bar',
                barWidth : BARWIDTH,
                stack: '超期',
                data:caigou_exceed
            },
            {
                name:'待入库超期',
                type:'bar',
                stack: '超期',
                data:ruku_exceed
            },
            {
                name:'待拍摄超期',
                type:'bar',
                stack: '超期',
                data:paishe_exceed
            },
            {
                name:'待制作超期',
                type:'bar',
                stack: '超期',
                data:zhizuo_exceed
            }
        ]
    };
    ;
    if (option && typeof option === "object") {
        myChart.setOption(option, true);
    }
    // $(window).resize(myChart.resize);



}

// 绘制销售的条形图
function drawSaleBar(res,elementEle) {  
    elementEle = elementEle.replace('caigou','sale')
    let myChart2 = echarts.init(document.getElementById(elementEle))
    let app = {};
    let option2 = null;
    // app.title = '堆叠柱状图';
    
    // 柱的宽度
    let BARWIDTH = 30
    if (elementEle == 'saleDay30' || elementEle == 'saleCurrentDailyDiv'){
        BARWIDTH = 6
    }

    let xAxisData = []

    let shangjia_done = []
    let taotai = []
    let fengcun = []
    let fengcun_done = []
    let tuishi_done = []

    // 以周或者月份为尺度
    if (res['month_week'] != undefined){
        
        JSON.parse(res.data).forEach((element,i) => {
            if (res['month_week'] == 'month'){
                xAxisData.push(element['year'] + '-' + element['month'])
            }else if (res['month_week'] == 'week'){
                xAxisData.push(element['date'])
            }
            shangjia_done.push(element['shangjia_done'])
            taotai.push(element['taotai'])
            fengcun.push(element['fengcun'])
            fengcun_done.push(element['fengcun_done'])
            tuishi_done.push(element['tuishi_done'])
        });

    }else{
        JSON.parse(res.data).forEach((element,i) => {
            xAxisData.push(element['fields']['date'].substr(5))
            shangjia_done.push(element['fields']['shangjia_done'])
            taotai.push(element['fields']['taotai'])
            fengcun.push(element['fields']['fengcun'])
            fengcun_done.push(element['fields']['fengcun_done'])
            tuishi_done.push(element['fields']['tuishi_done'])
        });
    }


    option2 = {
        tooltip : {
            trigger: 'axis',
            axisPointer : {            // 坐标轴指示器，坐标轴触发有效
                type : 'shadow'        // 默认为直线，可选为：'line' | 'shadow'
            }
        },
        legend: {
            data:['已上架','待淘汰','待封存','已封存','已退市']
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
        },
        xAxis : [
            {
                type : 'category',
                data : xAxisData,
                // 横坐标全部显示
                axisLabel : {
                    show:true,
                    interval: 0,
                    rotate: 45,
                }
            },
        ],
        yAxis : [
            {
                type : 'value'
            }
        ],
        series : [
            {
                name:'已上架',
                type:'bar',
                barWidth : BARWIDTH,
                stack: '正常',
                data:shangjia_done
            },
            {
                name:'待淘汰',
                type:'bar',
                stack: '正常',
                data:taotai
            },
            {
                name:'待封存',
                type:'bar',
                stack: '正常',
                data:fengcun
            },
            {
                name:'已封存',
                type:'bar',
                stack: '正常',
                data:fengcun_done
            },
            {
                name:'已退市',
                type:'bar',
                stack: '正常',
                data:tuishi_done
            },
        ]
    };
    ;
    if (option2 && typeof option2 === "object") {
        myChart2.setOption(option2, true);
    }
    
}

/***********************采购的图 end******************************* */



/********************日期区间选择************* */
// 获取首页统计信息
function getIndexPurAndSaleData(callback) {  
    $.ajax({
        type: "post",
        url: "/get_caigou_echart/",
        success: function (response) {
            if(response['code'] == '0'){
                callback(response)
            }
        }
    });
}

function renderIndexStatistics() {  
    getIndexPurAndSaleData(function (res) {  
        $('#indexCaigou').text(res['caigou'])
        $('#indexRuku').text(res['ruku'])
        $('#indexPaishe').text(res['paishe'])
        $('#indexZhizuo').text(res['zhizuo'])
        $('#indexShangjia').text(res['shangjia'])
        $('#indexShangjiaDone').text(res['shangjia_done'])
        $('#indexTaotai').text(res['taotai'])
        $('#indexFengcun').text(res['fengcun'])
        $('#indexFengcunDone').text(res['fengcun_done'])
        $('#indexTuishiDone').text(res['tuishi_done'])
        $('#indexCaigouExceed').text(res['caigou_exceed'])
        $('#indexRukuExceed').text(res['ruku_exceed'])
        $('#IndexPaisheExceed').text(res['paishe_exceed'])
        $('#IndexZhizuoExceed').text(res['zhizuo_exceed'])
    })
}