module.exports = {
  apps: [{
    name: 'hockey-practice-planner',
    script: 'npm',
    args: 'start',
    cwd: '/Users/emilyfehr8/CascadeProjects/hockey-practice-planner',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'production',
      PORT: 3000
    },
    error_file: './logs/err.log',
    out_file: './logs/out.log',
    log_file: './logs/combined.log',
    time: true
  }]
}
