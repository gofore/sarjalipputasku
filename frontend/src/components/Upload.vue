<template>
  <div>
    <h2>Lataa sarjalippu</h2>
    <p><input type="file" @change="upload"></p>
    <p>{{ uploadMessage }}</p>
  </div>
</template>

<script>
export default {
  data () {
    return {
      uploadMessage: ""
    }
  },
  methods: {
    upload(e) {
      var files = e.target.files || e.dataTransfer.files;
      if (!files.length)
        return;

      var formData = new FormData();
      formData.append('file', files[0]);
      this.uploadMessage = "Ladataan...";
      this.$http.post('/api/v1/upload', formData).then((response) => {
        this.uploadMessage = "Lataus onnistui";
      }, (response) => {
        if (response.status === 422) {
          this.uploadMessage = "Lataus epäonnistu (sarjalippua ei voitu jäsentää)";
        }
        this.uploadMessage = "Lataus epäonnistui";
      });
    }
  }
}
</script>
