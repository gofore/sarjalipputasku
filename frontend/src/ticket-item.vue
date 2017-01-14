<template>
  <div>
    <h2>Lippusi</h2>
    <span>{{ ticket.src }} - {{ ticket.dest }}</span><br />
    <span>{{ ticket.id }}</span><br />
    Voimassa: <span>{{ new Date(ticket.expiration_date) }}</span>
  </div>
</template>

<script>
export default {
  props: {
    ticket: {
      type: Object,
      required: true
    }
  }
}
</script>
