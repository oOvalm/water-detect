// import './assets/main.css'

import {createApp} from 'vue'
import App from './App.vue'
import router from '@/router'
//引入cookies
import VueCookies from 'vue-cookies'
//引入element plus
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

//图标 图标在附件中
import '@/assets/icon/iconfont.css'
import '@/assets/base.scss'


//引入代码高亮
import HljsVuePlugin from '@highlightjs/vue-plugin'
import "highlight.js/styles/atom-one-light.css";
import 'highlight.js/lib/common'

import Message from '@/utils/Message'
import Confirm from '@/utils/Confirm'
import Verify from '@/utils/Verify'
// import Utils from '@/utils/Utils'


const app = createApp(App)
app.use(ElementPlus);
app.use(HljsVuePlugin);
app.use(router)

app.config.globalProperties.Message = Message;
app.config.globalProperties.Confirm = Confirm;
app.config.globalProperties.Verify = Verify;
// app.config.globalProperties.Utils = Utils;

app.config.globalProperties.VueCookies = VueCookies;

app.mount('#app')
