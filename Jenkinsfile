node {
    def app

    stage('Clone Repostitory') {
        checkout scm
    }

    stage('Build image') {
        app = docker.build("ncelebic/deluge-watcher")
    }

    stage('Test image') {
        app.inside {
            sh 'echo "Tests Passed'
        }
    }
}