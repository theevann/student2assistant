

var app = new Vue({
    el: "#vue-app",
    mixins: [peer_mixin],
    data: {
        input_message: "",
        call_requested: false,
        index: -1
    },
    methods: {
        request_call: function () {
            if (this.name == "")
                return;

            $.ajax("/request-call", {
                data: JSON.stringify({
                    id: this.peer.id,
                    name: this.name,
                    room: this.room,
                }),
                method: "POST",
                contentType: "application/json",
                success: this.get_request_status
            });
            this.call_requested = true;
            this.index = null;
        },
        get_request_status: function () {
            $.get("/get-request-status", {
                name: this.name,
                id: this.peer.id
            }).done(({
                index,
                assistant_id
            }) => {
                this.index = index;
                if (assistant_id) {
                    console.log("Got an assistant id:", assistant_id);
                    this.launch_call(assistant_id);
                    this.launch_chat(assistant_id);
                    this.call_requested = false;
                } else if (index == -1) {
                    this.call_requested = false;
                }
            });
        },
        setTimeoutStatus: function () {
            setTimeout(() => {
                this.get_request_status();
            }, 5000);
        },
        cancel_request: function () {
            $.get("/cancel-request", {
                id: this.peer.id,
                name: this.name
            });
            this.call_requested = false;
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
        setInterval(() => {
            if (this.call_requested)
                this.get_request_status();
        }, 5000);
    }
});

window.addEventListener("unload", function (e) {
    if (app.call_requested) {
        app.cancel_request();
        (e || window.event).returnValue = null;
        return "You will lose you position in the queue";
    }
    return null;
});