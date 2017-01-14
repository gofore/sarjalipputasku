<template>
  <div id="app">
    <h1>{{ msg }}</h1>
    <form>
      <p>
        <label for="from">Mistä</label><br />
        <input type="text" name="from" id="from" v-model="from" />
      </p>
      <p>
        <label for="to">Minne</label><br />
        <input type="text" name="to" id="to" v-model="to" />
      </p>
      <input type="button" name="submit" id="submit" value="Hae lippu" v-on:click="search"></input>
    </form>
  </div>
</template>

<script>
export default {
  name: 'app',
  data () {
    return {
      msg: 'Sarjalipputasku'
    }
  },
  methods: {
    search: function () {
      // TODO send search parameters to backend
      this.$http.get('/api/v1/routes', {
        params: {
          src: from.value,
          dest: to.value
        }
      }).then((response) => {
        // success callback
        console.log(response);
      }, (response) => {
        // error callback
      });
    }
  }
}
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}

h1, h2 {
  font-weight: normal;
}

ul {
  list-style-type: none;
  padding: 0;
}

li {
  display: inline-block;
  margin: 0 10px;
}

a {
  color: #42b983;
}
</style>
