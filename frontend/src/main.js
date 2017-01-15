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

const Foo = { template: '<div>foo</div>' }

export var router = new VueRouter({
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

//new Vue({
//  el: '#app',
//  render: h => h(App)
//})
