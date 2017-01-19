<template>
  <div>
    <h2>Kirjautuminen</h2>
		<div class="form-group">
        <input
          type="text"
          class="form-control"
          placeholder="Käyttäjä"
          v-model="credentials.username"
          v-on:keyup.enter="login"
        >
      </div>
      <div class="form-group">
        <input
          type="password"
          class="form-control"
          placeholder="Salasana"
          v-model="credentials.password"
          v-on:keyup.enter="login"
        >
      </div>
      <button class="btn btn-primary" @click="login()">Sisään</button>
  </div>
</template>

<script>
  import auth from '../auth'
  export default {
    data() {
      return {
        credentials: {
          username: '',
          password: ''
        }
      }
    },
    methods: {
      login() {
        var credentials = {
          email: this.credentials.username,
          password: this.credentials.password
        }
        auth.login(this, credentials, '/')
      }
    }
  }
</script>
