<template></template>
<script>
  import auth from '../auth'
  export default {
    data() {
      return {}
    },
    mounted() {
      console.log("ready")
      auth.tokenLogin(this.$route.query.token)
      this.$router.push('/')
    },
    methods: {
    }
  }

</script>
