<template>
    <div class="hello">
        <div class="login">
            <el-form ref="form"  label-width="80px">
                <el-form-item label="产品编码:">
                    <el-input v-model="good.code" placeholder="例如：19002"></el-input>
                </el-form-item>
                <el-form-item label="sku编码:">

                    <template>
                        <el-select v-model="good.sku_code" size="medium" filterable remote reserve-keyword placeholder="例如：19002-001" :remote-method="remoteMethod" :loading="good.loading" @change="selectChange($event)">
                            <el-option  v-for="item in list" :key="item.sku_id" :label="item.sku_code" :value="item.sku_code">
                            </el-option>
                        </el-select>
                    </template>
                </el-form-item>
            </el-form>

        </div>
        <div class="button">
            <el-button type="primary" :loading="good.isButtonLoading"   @click.native="queryEvent" :disabled="good.operating">{{good.buttonValue}}</el-button>
        </div>

        <div class="demo-image__placeholder display-content">
            <div class="block">
                <span class="demonstration">产品名称:&nbsp;{{good.name}}</span>

                <span class="demonstration">sku名称:&nbsp;{{good.sku_name}}</span>
            </div>
            <el-image :src="good.sku_image"></el-image>
        </div>
    </div>
</template>

<script>
import { Toast } from 'mint-ui';

import GLOBAL from "../common/base.js";
export default {
    data(){
        return{
        options: [],
        list: [],
        states: ["Alabama", "Alaska", "Arizona",
        "Arkansas", "California", "Colorado",
        "Connecticut", "Delaware", "Florida",
        "Georgia"],
            flag:false,
            good:{
                code:'',
                name:'',
                skus:[],
                sku_code:'',
                sku_name:'',
                sku_image:'',
                loading:false,
                isButtonLoading:false,
                flag:true,
                buttonValue:'查询',
            },
            

        }
    },
    methods:{
        queryEvent(){
            // 检查是否为空
            if(this.good.code == ''){
                Toast({
                    message: '请输入产品编码',
                    position: 'top',
                    duration: 3000
                });
                return false
            }
            // 正则校验
            if(!/^[1,2][0-9]{4}$/.test(this.good.code)){
                Toast({
                    message: '请输入正确的产品编码',
                    position: 'top',
                    duration: 3000
                });
                return false
            }
            // 仅有 产品编码时候
            this.good.buttonValue = '查询中...'
            this.good.isButtonLoading = true
            this.$http.get(GLOBAL.BASE_URL+'query/?good_code='+this.good.code).then(success=>{
                this.good.buttonValue = '查询'
                this.good.isButtonLoading = false
                if(success.body.code=='0'){
                    // 查询成功
                    console.log(success.body)
                    this.good.name = success.body.good_name
                    this.good.skus = success.body.skus
                    this.good.sku_code = this.good.code +'-'+ success.body.skus[0].sku_code 
                    this.good.sku_name =   success.body.skus[0].sku_name
                    this.good.sku_image = success.body.skus[0].sku_image 
                    // 给list中添加值
                    this.list = success.body.skus.map(item => {
                        return { id: item.sku_id, sku_code: this.good.code+'-'+item.sku_code,sku_name: item.sku_name, sku_image: item.sku_image};
                    });
                }else{
                    Toast({
                        message: success.body.msg,
                        position: 'top',
                        duration: 3000
                    });
                }
            })

        },

        remoteMethod(query) {
            if (query !== '') {
                this.loading = true;
                setTimeout(() => {
                    this.loading = false;
                    this.options = this.list.filter(item => {
                    return item.label.toLowerCase()
                    .indexOf(query.toLowerCase()) > -1;
                });
                }, 200);
            } else {
                this.options = [];
            }
        },

        // 下拉的sku变化
        selectChange(val){
            // val  19002-002
            console.log(val)
            this.list.forEach(element => {
                if(element.sku_code == val){
                    this.good.sku_name = element.sku_name
                    this.good.sku_image = element.sku_image
                }
            });
        }
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
    },
    mounted() {
  
 
    },

}
</script>


<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
    .hidden{
        display: none;
    }
    .dropContent{
        position: relative;
    }
    .drop{
        position: absolute;
        top: 0;
        left: 0;
        z-index: 9999;
    }

    // 设置input+select宽度
    .el-form-item__content .el-select {
        width: 100%;
    }

    .display-content{
        margin-top: 20px;
        .block{
            display: flex;
            justify-content: space-around;
        }
    }
    

    .hello .button .el-button{
        width: 100%;
    }
</style>
