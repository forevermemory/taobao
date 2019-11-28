
import Vue from 'vue'
import VueRouter from 'vue-router'

Vue.use(VueRouter) 



import Login from '../components/Login.vue'
import Image from '../components/Image.vue'
import Query from '../components/Query.vue'
// import HelloWorld from '../components/HelloWorld.vue'


const routes = [
    {path:'/login',component:Login},
    {path:'/image',component:Image},
    // {path:'/query',component:HelloWorld},
    {path:'/query',component:Query},
    { path: '*', redirect: '/login'} 
]
const router = new VueRouter({
    routes, // 相当于routes:routes,
})


export default router