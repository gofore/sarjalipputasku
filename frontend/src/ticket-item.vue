<template>
  <div>
    <h2>Lippusi</h2>
    <span>{{ ticket.src }} - {{ ticket.dest }}</span><br />
    <span>{{ ticket.id }}</span><br />
    Voimassa: <span>{{ formatDate(ticket.expiration_date) }}</span>
    <p>
      <button v-on:click="reserveTicket(ticket.id)">Varaa lippu</button>
    </p>
    <p>
      <span v-if="reservedOk">Varattu</span>
      <span v-if="reservedNok">Ei onnistunut. Hae uusi lippu.</span>
    </p>
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
  data () {
    return {
      reservedOk: false,
      reservedNok: false
    }
  },
  methods: {
    formatDate: function(timestamp) {
      var date = new Date(timestamp);
      return date.getDate() + '.' + (date.getMonth() + 1) + '.' + date.getFullYear();
    },
    reserveTicket: function (id) {
      this.$http.put('/api/v1/routes/' + id, {
        reserved: true
      }).then((response) => {
        this.reservedOk = true;
        this.reservedNok = false;
      }, (response) => {
        this.reservedOk = false;
        this.reservedNok = true;
      });
    }
  }
}
</script>
