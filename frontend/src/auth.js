import router from './main'
const LOGIN_URL = '/api/v1/login'

export default {
  user: {
    authenticated: false
  },
  login(context, creds, redirect) {
    context.$http.post(LOGIN_URL, creds).then(
			(data) => {
				localStorage.setItem('token', data.body.token)
				this.user.authenticated = true
				console.log("authenticated")
				if(redirect) {
					router.push(redirect)
				}
			},
			(err) => {
      	context.error = err
    	})
	},
	logout() {
    localStorage.removeItem('token')
    this.user.authenticated = false
		router.push('/login')
  },
	isAuthenticated() {
    var jwt = localStorage.getItem('token')
    if(jwt) {
      this.user.authenticated = true
    }
    else {
      this.user.authenticated = false
    }
		return this.user.authenticated
  },
	getAuthHeader() {
    return {
      'Authorization': 'Bearer ' + localStorage.getItem('token')
    }
  }
}


