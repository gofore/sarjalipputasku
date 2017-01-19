<template>
  <div>
    <h2>Lippusi</h2>
    <span>{{ ticket.src }} - {{ ticket.dest }}</span><br />
    Voimassa: <span>{{ formatDate(ticket.expiration_date) }}</span><br />
    Hinta: <span>{{ ticket.price }} &euro; (alv 0%)</span><br />
    <span>{{ ticket.vr_id }}</span><br />
    <p>
      <img v-bind:src="ticket.qr" />
    </p>
    <p>
      <span v-if="error">{{ error }}</span>
    </p>
    <p v-if="!reserved">
      <button class="btn btn-default" v-on:click="reserveTicket(ticket.id)">Varaa lippu</button>
    </p>
    <p>
      <span v-if="reserved && !used">Varattu</span>
      <span v-if="used">Käytetty</span>
    </p>
    <p v-if="reserved && !used">
      <button class="btn btn-warning" v-on:click="releaseTicket(ticket.id)">Vapauta lippu (peru käyttö)</button>
    </p>
    <p v-if="reserved && !used">
      <button class="btn btn-success" v-on:click="useTicket(ticket.id)">Merkitse käytetyksi</button>
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
      reserved: false,
      used: false,
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
        this.reserved = true;
      }, (response) => {
        console.log("error")
        this.error = 'Lipun varaaminen ei onnistunut';
      });
    },
    releaseTicket: function (id) {
      this.$http.put('/api/v1/routes/' + id, {
        reserved: false,
        used: false
      }).then((response) => {
        this.reserved = undefined;
      }, (response) => {
        this.error = 'Lipun vapauttaminen ei onnistunut';
      });
    },
    useTicket: function (id) {
      this.$http.put('/api/v1/routes/' + id, {
        used: true
      }).then((response) => {
        this.used = true;
      }, (response) => {
        this.error = 'Lipun merkitseminen käytetyksi ei onnistunut';
      });
    }
  }
}
</script>
