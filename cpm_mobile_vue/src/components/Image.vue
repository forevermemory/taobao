<template>
    <div class="hello">

        <div class="header">
            <div class="open_camera">

                点击打开相册
                <input type="file" name="iamge" style="opacity:0 ;" value="点击打开相册" id="imageInput">
            </div>
            <div class="upload_file" @click="searchImage($event)" :logining="image.logining">
                点击搜索
            </div>
        </div>

        <div class="demo-image__placeholder display-content">
            <div class="block">
                <div class="good">
                    <span class="demonstration">产品编码:&nbsp;{{image.code}}</span>
                    <span class="demonstration">产品名称:&nbsp;{{image.name}}</span>
                </div>
                <div class="sku">

                    <span class="demonstration">sku编码:&nbsp;{{image.sku_code}}</span>
                    <span class="demonstration">sku名称:&nbsp;{{image.sku_name}}</span>
                </div>
            </div>
            <div class="img_out">
                <div class="two"  v-for="(item,index) in list" :key="index" >

                    <el-image :src="item.url" :data-sku_id="item.sku_id"  @click="skuImage($event)"></el-image>
                </div>
                <!-- <div class="two" v-for="(item,index) in 4" :key="index" >

                    <el-image src="http://tbcdn.tajansoft.com/1567997948.350368-19002-001.jpg" :data-sku_id="index"  @click="skuImage($event)"></el-image>
                </div> -->
            </div>
            
        </div>
        <!-- <mt-actionsheet
        :actions="actions"
        v-model="sheetVisible">
        </mt-actionsheet>

        <div class="button">
            <mt-button type="primary" size="large"  @click.native="actionEvent" :disabled="image.logining">{{image.buttonValue}}</mt-button>
        </div> -->
    </div>
</template>

<script>
import { Toast } from 'mint-ui';

import GLOBAL from "../common/base.js";
// import { Actionsheet } from 'mint-ui';
// Vue.component(Actionsheet.name, Actionsheet);
// http://www.luyixian.cn/javascript_show_168389.aspx
export default {
    data(){
        return{
            sheetVisible:false,
            actions:[
                {name:'拍照',method: this.photo}
            ],
            list:[],
            image:{
                logining:false,
                buttonValue:'正在搜索中',
                code:'',
                name:'',
                good_id:'',
                score:'',
                sku_code:'',
                sku_id:'',
                sku_name:'',
                url:'',
            },
            datas: new FormData(),
        }
    },
    methods:{
        skuImage(e){
            console.log(e.srcElement.dataset.sku_id)
            this.image.sku_id = e.srcElement.dataset.sku_id
            this.list.forEach(element => {
                if(element.sku_id == this.image.sku_id ){
                    this.image.code = element.code
                    this.image.name = element.name
                    this.image.sku_code = element.sku_code
                    this.image.sku_name = element.sku_name
                }
            });
        },
        searchImage(e){
            if(this.image.logining){
                Toast({
                    message: '请稍后...',
                    position: 'top',
                    duration: 3000
                });
                return false
            }
            if(document.getElementById('imageInput').files[0] == undefined){
                Toast({
                    message: '请上传图片',
                    position: 'top',
                    duration: 2000
                });
                return false
            }
            var fileExt = document.getElementById('imageInput').files[0]['name'].split('.').pop()
            if(!/^(jpg|jpeg|png|JPG|PNG|JPEG)$/.test(fileExt)){
                Toast({
                    message: '图片格式只支持jpg,png,jpeg',
                    position: 'top',
                    duration: 2000
                });
                return false
            }
            this.datas.append('image', document.getElementById('imageInput').files[0])

            e.srcElement.innerText='正在搜索中...'
            this.image.logining = true
            // 设置状态
            this.$http.post(GLOBAL.BASE_URL+'image/',this.datas).then(success=>{
                e.srcElement.innerText='点击搜索'
                this.image.logining = false
                if(success.body.code=='0'){
                    console.log(success.body)
                    var resArray = success.body.res
                    this.list = resArray
                    // code: 19006
                    // good_id: 1
                    // name: "手链"
                    // score: "0.58"
                    // sku_code: "003"
                    // sku_id: 9
                    // sku_name: "水晶手链"
                    // url: "http://tbcdn.tajansoft.com//1568272117.838193-19006-003.jpg"
                    // {code: "0", msg: "ok", res: Array(4)}
                }else{
                    Toast({
                        message: success.body.msg,
                        position: 'top',
                        duration: 3000
                    });
                }
            })
        },
        
        // photo(){
        //     console.log('拍照')
        //     this.getImage()

        // },
        // actionEvent(){
        //     this.sheetVisible = !this.sheetVisible
        // },
        // //调用手机摄像头并拍照
        // getImage() {
        //     let cmr = plus.camera.getCamera();
        //         cmr.captureImage(function(p) {
        //             plus.io.resolveLocalFileSystemURL(p, function(entry) {
        //             compressImage(entry.toLocalURL(),entry.name);
        //         }, function(e) {
        //             plus.nativeUI.toast("读取拍照文件错误：" + e.message);
        //         });
        //     }, function(e) {
        //         }, {
        //             filter: 'image'
        //     });
        // },
        // //从相册选择照片
        // galleryImgs() {
        //     plus.gallery.pick(function(e) {
        //         let name = e.substr(e.lastIndexOf('/') + 1);
        //         compressImage(e,name);
        //         }, function(e) {
        //         }, {
        //         filter: "image"
        //     });
        // },
    },
    beforeRouteEnter(to, from, next){
        var user = sessionStorage.getItem('user')
        if(user==undefined){
            Toast({
                message: '请先登录',
                position: 'top',
                duration: 3000
            });
        }else{
            next()
            
        }
    }
}
</script>


<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
        // 图片展示
    .display-content{
        margin-top: 20px;
        .block{
            .good{
            display: flex;
            justify-content: space-around;

            }
            .sku{
                margin-top: 10px;
                margin-bottom: 10px;
            display: flex;
            justify-content: space-around;
            }
        }

        // 图片
        .img_out{
            // display: flex;
            width: 100%;
            .two{
                float: left;
                margin-right: 5px;
                width: 48%;
            }
        }
    }
        
        // 底部按钮
    .button{
        width: 100%;
        position: fixed;
        left: 0;
        bottom: 45px;
    }
    //头部样式
    .header{
        display: flex;

        .open_camera{
            width: 48%;
            position: relative;
            height: 50px;
            color: white;
            font-size: 18px;
            line-height: 50px;
            // background-color: #ccc;
            background-color: #26a2ff;
            // display: block;
            input{
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                display: block;
            }

        }

        .upload_file{
            margin-left: 10px;
            width: 48%;
            height: 50px;
            color: white;
            font-size: 18px;
            line-height: 50px;
            // background-color: #aaa;
            background-color: #26a2ff;

        }


    }
</style>
