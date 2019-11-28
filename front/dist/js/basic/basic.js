
/************************************************ */
// 获取url 中的查询参数
function GetQueryString(name){
     var reg = new RegExp("(^|&)"+ name +"=([^&]*)(&|$)");
     var r = window.location.search.substr(1).match(reg);
     if(r!=null)return  unescape(r[2]); return null;
}

// 前面补0
function PrefixIntegerZero(num, length) {
    return (Array(length).join('0') + num).slice(-length);
}


/******************************************** */

/******************************************** */
/******************************************** */