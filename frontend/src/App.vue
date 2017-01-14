<template>
  <div id="app">
    <h1>{{ msg }}</h1>
    <form>
      <label for="from">Mistä</label>
      <input type="text" name="from" id="from" placeholder="Mistä" :value="value" @input="onInput"></input>
      <label for="to">Minne</label>
      <input type="text" name="to" id="to" placecholder="Minne"></input>
      <input type="button" name="submit" id="submit" value="Hae lippu"></input>
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
