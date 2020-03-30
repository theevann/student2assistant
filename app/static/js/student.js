

var app = new Vue({
    el: "#vue-app",
    mixins: [peer_mixin],
    data: {
        request_id: null,
        index: null,
        input_message: "",
    },
    computed: {
        call_requested: function () {
            return this.request_id != null;
        }
    },
    methods: {
        start_update_stream: function (source) {
            source.addEventListener("rank_update", ({ data }) => {
                data = JSON.parse(data);
                if (this.call_requested && data.request_rank < this.index)
                    this.index--;
            });
            source.addEventListener("match_request", ({ data }) => {
                data = JSON.parse(data);
                this.remote_peer_id = data.assistant_peer_id;
                this.remote_zoom_id = data.assistant_zoom_id;

                this.request_id = null;
                this.launch_chat(this.remote_peer_id);
                console.log("match_request");
            });
        },
        request_call: async function () {
            if (this.name == "")
                return;

            if (!this.registered)
                await this.register_on_server("student");

            $.ajax("/request", {
                data: JSON.stringify({
                    user_id: this.user_id,
                    room: this.room,
                    request: "assistant",
                }),
                method: "POST",
                contentType: "application/json",
                success: ({ request_id, index }) => {
                    this.request_id = request_id;
                    this.index = index;
                },
                error: (e) => {
                    console.error("Error: ", e);
                }
            });

        },
        get_request_status: function () {
            $.get("/queue/", {
                user_id: this.user_id,
                request_id: this.request_id,
            }).done(({
                index,
                assistant_id
            }) => {
                this.index = index;
                if (assistant_id) {
                    console.log("Got an assistant id:", assistant_id);
                    this.launch_call(assistant_id);
                    this.launch_chat(assistant_id);
                    this.request_id = null;
                    this.index = null;
                }
            });
        },
        cancel_request: function () {
            $.ajax("/request", {
                data: JSON.stringify({
                    user_id: this.user_id,
                    request_id: this.request_id,
                }),
                method: "DELETE",
                contentType: "application/json",
            });
            
            this.request_id = null;
            this.index = null;
        },
        send_input_message: function (code = false) {
            this.send_message(this.input_message, code)
            this.input_message = "";
            this.$nextTick(() => $('#chat-messages').scrollTop($('#chat-messages')[0].scrollHeight));
        },
        set_full_screen: function () {
            if (document.fullscreenEnabled) {
                document.querySelector('#videosContainer > video').requestFullscreen();
            }
        }
    },
    mounted: function () {

    }
});

// window.addEventListener("beforeunload", function (e) {
//     if (app.call_requested) {
//         app.cancel_request();
//         (e || window.event).returnValue = null;
//         return "You will lose you position in the queue";
//     }
//     return null;
// });