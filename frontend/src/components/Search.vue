<template>
  <div>
    <form>
      <p>
        <label for="from">Mistä</label><br />
        <input type="text" name="from" id="from" v-model="from" autofocus />
      </p>
      <p>
        <label for="to">Minne</label><br />
        <input type="text" name="to" id="to" v-model="to" />
      </p>
      <input type="button" name="submit" id="submit" value="Hae lippu" v-on:click="search"></input>
    </form>

    <div>
      <ticket-item
        v-for="ticket in tickets"
        :ticket="ticket"
        :key="ticket.id"
        />
    </div>
    <div v-show="tickets === null">
      <p>
        Ei käyttämättömiä sarjalippuja tälle välille
      </p>
    </div>
  </div>
</template>

<script>
import TicketItem from './ticket-item.vue';
import auth from '../auth';

export default {
  components: {
    TicketItem
  },
  data () {
    return {
      tickets: [],
    }
  },
  methods: {
    search: function () {
      this.$http.get('/api/v1/routes', {
        params: {
          src: from.value,
          dest: to.value
        },
        headers: auth.getAuthHeader()
      }).then((response) => {
        // success callback
        this.tickets = response.body.tickets;
      }, (response) => {
        // error callback
        this.tickets = [];
      });
    }
  }
}
</script>


