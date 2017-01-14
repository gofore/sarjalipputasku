<template>
  <div>
    <h2>Lippusi</h2>
    <span>{{ ticket.src }} - {{ ticket.dest }}</span><br />
    <span>{{ ticket.id }}</span><br />
    Voimassa: <span>{{ formatDate(ticket.expiration_date) }}</span>
  </div>
</template>

<script>
export default {
  props: {
    ticket: {
      type: Object,
      required: true
    }
  },
  methods: {
    formatDate: function(timestamp) {
      var date = new Date(timestamp);
      return date.getDate() + '.' + (date.getMonth() + 1) + '.' + date.getFullYear();
    }
  }
}
</script>
