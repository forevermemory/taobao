import Vue from 'vue'
import App from './App.vue'

// mui
import MintUI from 'mint-ui'
import 'mint-ui/lib/style.css'
Vue.use(MintUI)

import ElementUI from 'element-ui';
import 'element-ui/lib/theme-chalk/index.css';
Vue.use(ElementUI);

// router
import router from  './common/router.js'

// vue-resource
import VueResource from "vue-resource";
Vue.use(VueResource)



Vue.config.productionTip = false

new Vue({
    router,
  render: h => h(App),
}).$mount('#app')
