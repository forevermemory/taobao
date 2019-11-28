<template>
    <div class="hello">
        <div class="login">
            <mt-field label="用户名:" placeholder="请输入用户名" v-model="user.username" ></mt-field>
            <mt-field label="密码:" placeholder="请输入密码" type="password" v-model="user.password"></mt-field>
        </div>
        <div class="button">
            <mt-button type="primary" size="large"  @click.native="loginEvent" :disabled="user.logining">{{user.buttonValue}}</mt-button>
        </div>
    </div>
</template>

<script>
import { Toast } from 'mint-ui';

import GLOBAL from "../common/base.js";
export default {
    data(){
        return{
            user:{
                username:'',
                password:'',
                logining:false,
                buttonValue :'登录',
            }
        }
    },
    methods:{
        loginEvent(){
            // 先校验
            if (this.user.username == ''){
                Toast({
                    message: '请输入用户名',
                    position: 'bottom',
                    duration: 3000
                });
                return false
            }
            if (this.user.password == ''){
                Toast({
                    message: '请输入密码',
                    position: 'bottom',
                    duration: 3000
                });
                return false
            }

            this.user.logining = true
            this.user.buttonValue = '登录中...'

            let data = {
                username:this.user.username,
                password:this.user.password
            }
            this.$http.post(GLOBAL.BASE_URL+'login/',data,{emulateJSON:true}).then(success=>{
                console.log(success.body)
                this.user.logining = false
                this.user.buttonValue = '登录'
                if(success.body.code=='0'){
                    // 登陆成功 存到session 表示登陆成功
                    sessionStorage.setItem('user','user')
                    // 路由跳转
                    this.$router.push({ path: 'query' })
                    Toast({
                        message: '登陆成功',
                        position: 'top',
                        duration: 3000
                    });
                    var loginCom = document.getElementById('loginComponent').parentNode
                    loginCom.parentNode.remove()
                }else{
                    Toast({
                        message: success.body.msg,
                        position: 'top',
                        duration: 3000
                    });
                }
            })
        },

    },

    beforeRouteEnter(to, from, next){
        console.log(from)
        next()
    },


}
</script>


<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
    .button{
        margin-top: 20px;
    }
</style>
