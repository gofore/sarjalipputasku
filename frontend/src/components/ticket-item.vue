<template>
  <div>
    <h2>Lippusi</h2>
    <span>{{ ticket.src }} - {{ ticket.dest }}</span><br />
    Voimassa: <span>{{ formatDate(ticket.expiration_date) }}</span><br />
    <span>{{ ticket.vr_id }}</span><br />
    <p>
      <img v-bind:src="ticket.qr" />
    </p>
    <p v-if="!reservedOk">
      <button v-on:click="reserveTicket(ticket.id)">Varaa lippu</button>
    </p>
    <p>
      <span v-if="reservedOk">Varattu</span>
      <span v-if="reservedNok">Ei onnistunut. Hae uusi lippu.</span>
    </p>
    <p v-if="reservedOk && !usedOk && !releasedOk">
      <button v-on:click="releaseTicket(ticket.id)">Vapauta lippu (peru käyttö)</button>
    </p>
    <p>
      <span v-if="releasedOk">Vapautettu</span>
      <span v-if="releasedNok">Ei onnistunut</span>
    </p>
    <p v-if="reservedOk && !usedOk && !releasedOk">
      <button v-on:click="useTicket(ticket.id)">Merkitse käytetyksi</button>
    </p>
    <p>
      <span v-if="usedOk">Käytetty</span>
      <span v-if="usedNok">Ei onnistunut</span>
    </p>
  </div>
</template>

<script>
import auth from '../auth'
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
      releasedNok: false,
      usedOk: false,
      usedNok: false
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
      }, {
        headers: auth.getAuthHeader()
      }
      ).then((response) => {
        this.reservedOk = true;
        this.reservedNok = false;
      }, (response) => {
        this.reservedOk = false;
        this.reservedNok = true;
      });
    },
    releaseTicket: function (id) {
      this.$http.put('/api/v1/routes/' + id, {
        reserved: false,
        used: false
      }, {
        headers: auth.getAuthHeader()
      }).then((response) => {
        this.releasedOk = true;
        this.releasedNok = false;
      }, (response) => {
        this.releasedOk = false;
        this.releasedNok = true;
      });
    },
    useTicket: function (id) {
      this.$http.put('/api/v1/routes/' + id, {
        used: true
      }, {
        headers: auth.getAuthHeader()
      }).then((response) => {
        this.usedOk = true;
        this.usedNok = false;
      }, (response) => {
        this.usedOk = false;
        this.usedNok = true;
      });
    }
  }
}
</script>
