// main.ts
import { createApp } from 'vue'

import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import '@fortawesome/fontawesome-free/css/all.css'
import Toast from "vue-toastification";
import "vue-toastification/dist/index.css";
import './axios-config'

// Importing Font Awesome libraries
import { library } from '@fortawesome/fontawesome-svg-core'
import { faUserLock } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'

import 'core-js/stable'
import 'regenerator-runtime/runtime'
import './assets/css/style.css'
// Add the icons to the library, so you can use it in your Vue app
library.add(faUserLock)

const app = createApp(App)
// Global registration of FontAwesomeIcon component
app.component('font-awesome-icon', FontAwesomeIcon)

for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component)
}
app.use(ElementPlus)


const options = {
    // You can set your default options here
};
app.use(Toast, options);
app.mount('#app')
