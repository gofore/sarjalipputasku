<template xmlns:v-on="http://www.w3.org/1999/xhtml">
  <div>
    <form class="form-horizontal">
      <div class="form-group">
        <label class="col-sm-2 control-label" for="from">Mistä</label>
        <div class="col-sm-10">
         <input type="text" class="form-control" name="from" id="from"
                v-model="query.from" v-on:keyup.enter="search" autofocus />
        </div>
      </div>
      <div class="form-group">
        <label class="col-sm-2 control-label" for="to">Minne</label>
        <div class="col-sm-10">
          <input type="text" class="form-control" name="to" id="to" v-model="query.to" v-on:keyup.enter="search"/>
        </div>
      </div>
      <div class="form-group">
        <label class="col-sm-2 control-label" for="to">Lipputyyppi</label>
        <div class="col-sm-10">
          <label class="radio-inline pull-left">
            <input type="radio" name="inlineRadioType" id="inlineRadioTypeBoth"
                   v-model="query.type" value="" v-on:keyup.enter="search">Ei väliä
          </label>
          <label class="radio-inline pull-left">
            <input type="radio" name="inlineRadioType" id="inlineRadioTypeEko"
                   v-model="query.type" value="EKO" v-on:keyup.enter="search"> Eko
          </label>
          <label class="radio-inline pull-left">
            <input type="radio" name="inlineRadioType" id="inlineRadioTypeEkstra"
                   v-model="query.type" value="EKSTRA" v-on:keyup.enter="search"> Ekstra
          </label>
        </div>
      </div>

      <input type="button" class="btn btn-primary" name="submit" id="submit" value="Hae lippu"
             v-on:click="search">
    </form>

    <div>
      <ticket-item
        v-for="ticket in tickets"
        :ticket="ticket"
        :key="ticket.id"></ticket-item>
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
      query: {},
      tickets: []
    }
  },
  methods: {
    search: function () {
      var payload = {
        src: this.query.from,
        dest: this.query.to
      };
      if (this.query.type) {
        payload['type'] = this.query.type;
      }
      this.$http.get('/api/v1/routes', {
        params: payload
      }).then((response) => {
        // success callback
        this.tickets = response.body.tickets;
      }, (response) => {
        // error callback
        this.tickets = [];
      })
    }
  }
}
</script>


