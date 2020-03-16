var ICE_config = {
    'iceServers': [{
            'urls': 'stun:stun.l.google.com:19302'
        },
        {
            'urls': [
                'turn:192.158.29.39:3478?transport=udp',
                'turn:192.158.29.39:3478?transport=tcp'
            ],
            'credential': 'JZEOEt2V3Qb0y27GRntt2u2PAYA=',
            'username': '28224511:1379330808'
        }
    ]
}


var peer_mixin = {
    data: function () {
        return {
            peer: {},
            name: "",
            room: "ee-559",
            messages: [],
            remote_peer_id: "",
            remote_peer_name: "",
            local_stream_mode: "audio",
            remote_stream_mode: "audio",
            current_call: null,
            current_chat: null,
            audio_track: null,
            video_track: null,
            wide_chat: false,
            canvas: document.createElement('canvas'),
            audio_ringtone: new Audio('static/assets/notification.mp3'),
        }
    },
    computed: {
        in_call: function () {
            return this.current_call != null;
        }
    },
    watch: {
        name: function () {
            localStorage.setItem("name", this.name);
        },
    },
    methods: {
        launch_call: async function (peer_id) {
            console.log("Launching a call");
            this.audio_ringtone.play();

            let local_stream = await this.get_initial_stream();
            let call = this.peer.call(peer_id, local_stream);
            this.init_call(call);
        },
        receive_call: async function (call) {
            if (this.in_call) return;

            console.log("Receiving a call");
            this.audio_ringtone.play();

            this.init_call(call);
            let local_stream = await this.get_initial_stream();
            call.answer(local_stream);
        },
        get_initial_stream: async function () {
            draw();

            var canvas = document.querySelector('canvas');
            var stream = canvas.captureStream(25);
            var track = stream.getTracks()[0];

            let local_stream = await navigator.mediaDevices.getUserMedia({
                audio: true
            });
            this.audio_track = local_stream.getTracks()[0];
            local_stream.addTrack(track);

            return local_stream;
        },
        init_call: async function (call) {
            this.remote_peer_id = call.peer;
            this.current_call = call;
            this.local_stream_mode = "audio";

            call.on('stream', async (remote_stream) => {
                console.log("Receiving a stream")
                document.querySelector("#videoRemote").srcObject = remote_stream;

                // Multiple draw call for different network speed (best guess)
                setTimeout(draw, 500);
                setTimeout(draw, 1000);
                setTimeout(draw, 3000);
            });

            call.on('close', () => {
                console.warn("Closing call connection");
                this.clean_up();
            });

            call.on('error', (e) => {
                console.warn("Error on call connection:", e);

                $.notify({
                    title: '<span class="font-weight-bold">Call Error:</span><br />',
                    message: `
                        It seems the call ended unexpectedly. Click below to relaunch the call.
                        <button class="btn btn-danger mt-2" onclick="app.relaunch()">Restart call</button>
                    `
                }, {
                    type: 'danger',
                    delay: 10000
                });
            });

        },
        setup_audio: async function () { // TO DELETE -- NOT USED ANYMORE
            this.local_stream_mode = "audio";
            let audio_stream = await navigator.mediaDevices.getUserMedia({
                audio: true
            });
            let audio_track = audio_stream.getAudioTracks()[0];
            this.audio_track.stop();
            this.audio_track = audio_track;
            let sender = this.current_call.peerConnection.getSenders()[0];
            sender.replaceTrack(audio_track);
        },
        change_stream_mode: async function (mode) {
            var stream_getter = {
                "audio": () => document.querySelector('canvas').captureStream(25),
                "video": (constraints) => navigator.mediaDevices.getUserMedia(constraints),
                "screen": (constraints) => navigator.mediaDevices.getDisplayMedia(constraints),
            } [mode];

            let video_stream = await stream_getter({
                video: true,
                audio: false
            });

            let video_track = video_stream.getVideoTracks()[0];
            this.video_track = video_track;

            let sender = this.current_call.peerConnection.getSenders()[1];
            sender.track.stop()
            sender.replaceTrack(video_track);

            this.$nextTick(() => document.querySelector('#videoLocal').srcObject = video_stream);
            this.local_stream_mode = mode;
            this.send_info("change_mode", mode);
            (mode == "audio") && draw();
        },
        relaunch: function () {
            this.launch_call(this.remote_peer_id);
            this.launch_chat(this.remote_peer_id);
        },
        end_call: function () {
            this.send_info("end_call");
            this.close_call();
        },
        close_call: function () {
            if (this.current_call && this.current_call.open) {
                this.current_call.close();
            } else {
                // "close" event does not fire if current call is closed before being open
                console.log("Force clean-up");
                this.clean_up();
            }
        },
        clean_up: function () {
            // Without timeout, it prevents the sending of end_call message ...
            this.current_chat && setTimeout(this.current_chat.close.bind(this.current_chat), 500);

            this.audio_track && this.audio_track.stop();
            this.video_track && this.video_track.stop();
            this.audio_track = null;
            this.video_track = null;
            this.current_call = null;
            this.current_chat = null;
            this.remote_peer_name = "";
            this.remote_stream_mode = "audio";
            this.messages = [];
        },
        launch_chat: function (peer_id) {
            let conn = this.peer.connect(peer_id);
            this.init_chat(conn);
        },
        init_chat: function (conn) {
            this.current_chat = conn;

            conn.on('open', () => {
                console.log("Data connection open");
                this.send_info("peer_name", this.name);
            });

            conn.on('data', (data) => {
                console.log("Receiving data: ", data);

                if (data.type == "message") {
                    this.add_message(data);
                } else if (data.type == "info") {
                    switch (data.detail.key) {
                        case "end_call":
                            this.close_call();
                            break;

                        case "change_mode":
                            this.remote_stream_mode = data.detail.value;
                            break;

                        case "peer_name":
                            this.remote_peer_name = data.detail.value;
                            break;
                    }
                }

            });

            conn.on('error', (e) => {
                console.warn("Error on data connection : ", e);
            });

            conn.on('close', () => {
                console.warn("Data connection closed");
            });
        },
        send_info: function (key, value) {
            let detail = {
                key,
                value,
            };

            this.send_data("info", detail);
        },
        send_message: function (message, code) {
            if (message == "") return;

            message = code ? message : this.sanitize_message(message);

            let detail = {
                message,
                code,
            };

            let data = this.send_data("message", detail);
            this.add_message(data);
        },
        send_data: function (type, detail) {
            let data = {
                sender_id: this.peer.id,
                sender_name: this.name,
                type: type,
                timestamp: new Date(),
                detail: detail
            };

            this.current_chat.send(data);
            return data;
        },
        add_message: function (data) {
            this.messages.push(data);
            this.$nextTick(() => $('#chat-messages').scrollTop($('#chat-messages')[0].scrollHeight));
            this.$nextTick(Rainbow.color);
        },
        sanitize_message: function (message) {
            const regex = /(http|ftp|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])?/igm;
            const options = {
                allowedTags: ['br', 'a'],
                allowedAttributes: {
                    'a': ['href', 'target']
                }
            };

            let matches = message.match(regex);
            if (matches)
                message = matches.reduce((str, link) => str.replace(link, `<a href='${link}' target="_blank">${link}</a>`), message);
            message = message.replace(/\n/g, '<br />');

            return sanitizeHtml(message, options);
        }
    },
    created: function () {
        this.name = localStorage.getItem("name") || "";
        let peer_id = sessionStorage.getItem("peer_id") || null;

        let peer = this.peer = new Peer(peer_id, {
            config: ICE_config
        });

        this.peer.on('open', (id) => {
            console.log('Peer Connected with ID : ' + id);
            sessionStorage.setItem("peer_id", id);
            this.peer = {}
            this.peer = peer;
        });

        this.peer.on('connection', this.init_chat);
        this.peer.on('call', this.receive_call);
        this.peer.on('error', (e) => {
            console.error("! Fatal !\n Error on Peer connection:", e);
        });
    }
};


function draw() { // TODO:  Make it fake (virtual dom ?)
    var canvas = document.getElementById('canvas');
    if (canvas.getContext) {
        var ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.fillRect(0, 0, 0, 0);
        // ctx.clearRect(0, 0, canvas.width, canvas.height);
        // ctx.fillRect(0, 0, 0, 0);
        // ctx.fillStyle = "white";
        // ctx.textAlign = "center";
        // ctx.font = "20px Arial";
        // ctx.fillText("No video input", canvas.width / 2, canvas.height / 2);
    }
}