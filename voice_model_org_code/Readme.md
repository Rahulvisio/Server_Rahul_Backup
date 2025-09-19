
# Visio
Use instruction below to run stt model inference


## Installation


```bash
conda install python==3.10.12
aws s3 cp s3://gabbar-model/model.zip .
unzip model.zip
pip install -r requirements.txt

```

```bash
 sudo apt-get update
 sudo apt-get install ffmpeg

```
```bash
 mv model/model_config/ .
 mv model/gabbar_model/ .

```

```bash
gunicorn -b :8080 -t 0 app:app

```
```bash
sudo nano /etc/systemd/system/helloworld.service

```

```bash
[Unit]
Description=Gunicorn instance for a simple hello world app
After=network.target
[Service]
User=root
Group=www-data
WorkingDirectory=/home/rahul/Gabbar-V2-Server/abcd
ExecStart=/opt/conda/bin/gunicorn -b localhost:8080 -t 0 app:app
Restart=always
[Install]
WantedBy=multi-user.target

```

```bash
sudo systemctl daemon-reload
sudo systemctl start helloworld
sudo systemctl enable helloworld

```


```bash
curl localhost:8000

```

```bash
sudo apt-get install nginx

```


```bash
sudo systemctl start nginx
sudo systemctl enable nginx

```


```bash
sudo nano /etc/nginx/sites-available/default

```

```bash
upstream flaskhelloworld {
server 127.0.0.1:8000;
}

```

```bash
location / {
proxy_pass http://flaskhelloworld;
proxy_redirect http://localhost:8000/ /;
proxy_read_timeout 60s;
#try_files $uri $uri/ =404;
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}

```
