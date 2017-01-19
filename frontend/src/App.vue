 <template>
	<div id="app">
		<h1>Sarjalipputasku</h1>
		<nav class="navbar navbar-default">
			<div class="container">
				<ul class="nav nav-justified">
					<li><router-link to="/" v-if="user.authenticated" class="btn btn-lg">Lippuhaku</router-link></li>
					<li><router-link to="/mytickets" v-if="user.authenticated" class="btn btn-lg">Omat liput</router-link></li>
					<li><router-link to="/upload" v-if="user.authenticated" class="btn btn-lg">Lisää sarjalippu</router-link></li>
					<li><a v-if="user.authenticated" @click="logout()" class="btn btn-lg" >Kirjaudu ulos</a></li>
				</ul>
			</div>    
		</nav>
		<div class="container">
			<router-view></router-view>
		</div>
	</div>
</template>

<script>

import auth from './auth'
export default {
	data() {

		return {
			user: auth.user
		}
	},
	methods: {
		logout() {
			auth.logout()
		}
	}
}
</script>
