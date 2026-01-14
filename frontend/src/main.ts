import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import Dashboard from './views/Dashboard.vue'
import ExecutionDetail from './views/ExecutionDetail.vue'

const app = createApp(App)

// Pinia store
app.use(createPinia())

// Vue Router
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'dashboard', component: Dashboard },
    { path: '/executions/:id', name: 'execution-detail', component: ExecutionDetail }
  ]
})

app.use(router)

app.mount('#app')
