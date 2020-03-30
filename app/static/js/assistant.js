

var app = new Vue({
    el: "#vue-app",
    mixins: [peer_mixin],
    data: {
        password: "",
        logged_in: false,
        input_message: "",
        assistants: {},
    },
    methods: {
        start_update_stream: function (source) {
            source.addEventListener("new_assistant", ({ data }) => {
                let {assistant} =  JSON.parse(data);
                this.assistants[assistant.id] = assistant;
            });
            source.addEventListener("delete_assistant", ({ data }) => {
                let {assistant} =  JSON.parse(data);
                delete this.assistants[assistant.id];
            });
            source.addEventListener("update_assistant", ({ data }) => {
                let {assistant} =  JSON.parse(data);
                this.assistants[assistant.id] = assistant;
            });
            source.addEventListener("match_request", ({ data }) => {
                let {callee_peer_id} =  JSON.parse(data);
                if (callee_peer_id == this.peer.id)
                    setTimeout(() => this.update_status(this.status), 15000);
            });
            // SET your own status...
        },
        check_login: function () {
            $.get("/login", ({ is_authenticated, room, role, user_id }) => {
                if (is_authenticated
                    && (room == this.room)
                    && (role == "assistant")
                    ) {
                    this.registered = true;
                    this.init_update_stream();
                }
            });
        },
        logout: function () {
            $.get("/logout", () => this.logged_in = false);
        },
        login: function () {
            this.register_on_server("assistant", this.password);
            this.password = "";
        },
        update_status: function (status) {
            $.ajax("/status", {
                data: JSON.stringify({
                    user_id: this.user_id,
                    status: status
                }),
                method: "POST",
                contentType: "application/json",
                success: () => {
                    this.status = status;
                }
            });
        },
        get_status: async function () {
            let response = await $.get("/status", {
                user_id: this.user_id,
            }).promise();

            return response.status;
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
        this.peer.on("connection", () => this.status = "busy");
        this.peer.on("call", () => this.status = "busy"); // TODO: to delete
        
        this.check_login();

        // setInterval(async () => {
        //     if (!this.in_call && this.registered) {
        //         let status = await this.get_status();
        //         if (status == "busy" && this.status == "free") {
        //             setTimeout(async () => {
        //                 let status = await this.get_status();
        //                 if (status == "busy") this.update_status("free");
        //             }, 10000);
        //         }
        //     }
        // }, 30000);
    }
});

// window.addEventListener("unload", function (e) {
//     if (app.status == 'free') {
//         app.update_status('busy');
//         (e || window.event).returnValue = null;
//         return "";
//     }
//     return null;
// });