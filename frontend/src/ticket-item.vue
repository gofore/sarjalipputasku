<template>
  <div>
    <h2>Lippusi</h2>
    <span>{{ ticket.src }} - {{ ticket.dest }}</span><br />
    <span>{{ ticket.id }}</span><br />
    Voimassa: <span>{{ formatDate(ticket.expiration_date) }}</span>
    <img v-bind:src="ticket.qr" />
    <p v-if="!reservedOk">
      <button v-on:click="reserveTicket(ticket.id)">Varaa lippu</button>
    </p>
    <p>
      <span v-if="reservedOk">Varattu</span>
      <span v-if="reservedNok">Ei onnistunut. Hae uusi lippu.</span>
    </p>
    <p v-if="reservedOk && !releasedOk">
      <button v-on:click="releaseTicket(ticket.id)">Vapauta lippu</button>
    </p>
    <p>
      <span v-if="releasedOk">Vapautettu</span>
      <span v-if="releasedNok">Ei onnistunut.</span>
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
      reservedNok: false,
      releasedOk: false,
      releasedNok: false
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
    },
    releaseTicket: function (id) {
      this.$http.put('/api/v1/routes/' + id, {
        reserved: false
      }).then((response) => {
        this.releasedOk = true;
        this.releasedNok = false;
      }, (response) => {
        this.releasedOk = false;
        this.releasedNok = true;
      });
    }
  }
}
</script>
