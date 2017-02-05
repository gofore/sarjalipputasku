<template>
  <div>
    <form class="form-horizontal">
      <div class="form-group">
        <label class="col-sm-2 control-label" for="from">Mistä</label>
        <div class="col-sm-10">
         <input type="text" class="form-control" name="from" id="from" v-model="from" v-on:keyup.enter="search" autofocus />
        </div>
      </div>
      <div class="form-group">
        <label class="col-sm-2 control-label" for="to">Minne</label>
        <div class="col-sm-10">
          <input type="text" class="form-control" name="to" id="to" v-model="to" v-on:keyup.enter="search"/> 
        </div>
      </div>
      <input type="button" class="btn btn-primary" name="submit" id="submit" value="Hae lippu" v-on:click="search"></input>
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
        }
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


