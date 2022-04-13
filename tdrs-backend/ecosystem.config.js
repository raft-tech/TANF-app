console.log("This is PM2")
module.exports = {
    apps : [
        {
            name:"tdrs-backend-web",
            script: "./pm2_start.sh",
            // watch_delay: 10000,
            // kill_timeout:10000,
            // watch: ["./django-admin-508/admin_interface"]
        },
        // {
        //     name:"tdrs-backend-pytest",
        //     script: "watch-test.js",
        //     env:{
        //         "USE_LOCALSTACK":1,
        //     }
        //     // watch_delay: 10000,
        //     // kill_timeout:10000,
        //     // watch: ["./django-admin-508/admin_interface"]

        // },
        {
            name:"tdrs-backend-pytest",
            script: "ptw.sh",
            env:{
                "USE_LOCALSTACK":1,
            }
            // watch_delay: 10000,
            // kill_timeout:10000,
            // watch: ["./django-admin-508/admin_interface"]

        }
    ],

};
