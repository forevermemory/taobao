<template>
    <div id="app">

        <div class="tab-container">
            <router-view></router-view>
        </div>
        <div class="tab">
            <mt-tabbar v-model="selected" >
                <mt-tab-item id="login" >
                    <router-link to="login" id="loginComponent">登录</router-link>
                    
                </mt-tab-item>
                <mt-tab-item id="query">
                    <router-link to="query">编码查询</router-link>
                        
                </mt-tab-item>
                <mt-tab-item id="image">
                    <!-- <img slot="icon" src="/assets/100x100.png"> -->
                    <router-link to="image">图像查询</router-link>
                    
                </mt-tab-item>
            </mt-tabbar>
        </div>
    </div>
</template>

<script>

export default {
    data(){
        return{
            selected:'',
            value:'',
        }
    },
    methods:{
    
        checkIsHidden(){
            var user = sessionStorage.getItem('user')
            if(user==undefined){
                this.$router.push({ path: 'login' })
            }else{
                var loginCom = document.getElementById('loginComponent').parentNode
                loginCom.parentNode.remove()
                this.$router.push({ path: 'query' })
            }
        }
    },
    mounted(){
        this.checkIsHidden()
    },

}
</script>

<style lang="scss">
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}



// 设置底部高度
#app .mint-tabbar{
    height: 45px;
    position: fixed;
    .mint-tab-item .mint-tab-item-label{ 
        font-size: 16px;
        line-height: 32px;;
    }

    a{
        text-decoration: none;
        display: block;
        height: 100%;
        width: 100%;
    }
}

</style>
