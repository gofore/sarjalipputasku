<template>
  <div>
    <div class="ticket row" v-for="ticket in tickets">
      <div class="col-md-2 col-md-offset-3">
        <img v-bind:src="ticket.qr" />
      </div>
      <div class="col-md-4">
        <span>{{ ticket.src }} - {{ ticket.dest }}</span><br />
        Varattu: <span>{{ formatDate(ticket.reserved) }}</span><br />
        Hinta: <span>{{ ticket.price }} &euro; (alv 0%)</span><br />
        <span>{{ ticket.order_id }} - {{ ticket.vr_id }}</span><br />
      </div>
      <div class="col-md-2">
        <button class="btn btn-success" v-on:click="useTicket(ticket.id)" v-if="!ticket.used">Käytä</button>
        <button class="btn btn-warning" v-on:click="releaseTicket(ticket.id)" v-if="!ticket.used">Vapauta</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data () {
    return {
      tickets: [],
    }
  },
  mounted: function() {
    this.update()
  },
  methods: {
    formatDate: function(timestamp) {
      var date = new Date(timestamp);
      return date.getDate() + '.' + (date.getMonth() + 1) + '.' + date.getFullYear();
    },
    update: function () {
      this.$http.get('/api/v1/mytickets').then((response) => {
        // success callback
        this.tickets = response.body.tickets;
      }, (response) => {
        // error callback
        this.tickets = [];
      });
    },
    releaseTicket: function (id) {
      this.$http.put('/api/v1/routes/' + id, {
        used: false,
        reserved: false
      }).then((response) => {
        this.update()
      });
    },
    useTicket: function (id) {
      this.$http.put('/api/v1/routes/' + id, {
        used: true
      }).then((response) => {
        this.update()
      })
    }
  }
}

</script>

<style>
.ticket {
  padding-bottom: 1em;
}
</style>
