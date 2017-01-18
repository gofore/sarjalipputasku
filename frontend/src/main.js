import Vue from 'vue'
import VueResource from 'vue-resource'
import VueRouter from 'vue-router'
import App from './App.vue'
import Login from './components/Login.vue'
import Upload from './components/Upload.vue'
import Search from './components/Search.vue'
import auth from './auth'

Vue.use(VueResource);
Vue.use(VueRouter)

Vue.http.interceptors.push((request, next) => {
    console.log(request)
		next((response) => {
			if (response.status === 401) {
				auth.logout()			
			}
  })
})

var router = new VueRouter({
	routes: [
	  { path: '/login',  component: Login },
		{ path: '/', 
			component: Search, 
			meta: { auth: true }
		},
 		{ path: '/upload',
			component: Upload,
			meta: { auth: true }
		}
]})

router.beforeEach(function (to, from, next) {
	if (to.meta.auth && !auth.isAuthenticated()) {
		next('/login')
	} else {
		next()
	}
})

const app = new Vue({
  router,
	render: h => h(App)
}).$mount('#app')

auth.isAuthenticated()

export default router
