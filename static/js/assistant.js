

var app = new Vue({
    el: "#vue-app",
    mixins: [peer_mixin],
    data: {
        input_message: "",
        status: "busy",
        registered: false,
    },
    methods: {
        update_status: function (status) {
            $.ajax("/set-assistant-status", {
                data: JSON.stringify({
                    id: this.peer.id,
                    name: this.name,
                    status: status
                }),
                method: "POST",
                contentType: "application/json"
            });
            this.status = status;
        },
        get_status: async function () {
            let response = await $.get("/get-assistant-status", {
                name: this.name,
                id: this.peer.id
            }).promise();

            return response.status;
        },
        register_on_server: function (status) {
            $.ajax("/register-assistant", {
                data: JSON.stringify({
                    id: this.peer.id,
                    name: this.name,
                    room: this.room,
                    status: "busy"
                }),
                method: "POST",
                contentType: "application/json",
                success: () => this.registered = true
            });
        },
        send_input_message: function (code = false) {
            this.send_message(this.input_message, code)
            this.input_message = "";
        },
        set_full_screen: function () {
            if (document.fullscreenEnabled) {
                document.querySelector('#videosContainer > video').requestFullscreen();
            }
        }
    },
    mounted: function () {
        this.peer.on("call", () => this.status = "busy");
        
        setInterval(async () => {
            if (!this.in_call && this.registered) {
                let status = await this.get_status();
                if (status == "busy" && this.status == "free") {
                    setTimeout(async () => {
                        let status = await this.get_status();
                        if (status == "busy") this.update_status("free");
                    }, 10000);
                }
            }
        }, 30000);

    }
});

window.addEventListener("unload", function (e) {
    if (app.status == 'free') {
        app.update_status('busy');
        (e || window.event).returnValue = null;
        return "";
    }
    return null;
});