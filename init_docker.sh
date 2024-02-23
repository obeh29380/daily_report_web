sudo yum update -y
sudo yum -y install docker
sudo systemctl start docker
sudo systemctl enable docker

sudo mkdir -p /usr/local/lib/docker/cli-plugins
cd /usr/local/lib/docker/cli-plugins
sudo curl -OL https://github.com/docker/compose/releases/download/v2.24.6/docker-compose-linux-aarch64
sudo mv docker-compose-linux-aarch64 docker-compose
sudo chmod +x docker-compose
sudo ln -s /usr/local/lib/docker/cli-plugins/docker-compose /usr/bin/docker-compose
