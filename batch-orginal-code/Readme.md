
# Bach Code




## Deployment

To deploy this project run


```bash
   git clone   https://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@github.com/Gabbar-V2-Server/gabbar-v2_batch_code.git
```
```bash
  sudo apt install nodejs
  sudo apt install npm
  npm install nodemon
  sudo npm i -g pm2

```



```bash
   cd dist/src

```
Open utils.js and replace url with model instance url

```bash
   nano utils.js

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
server 127.0.0.1:8080;
}

```

```bash
location / {
proxy_pass http://flaskhelloworld;
proxy_redirect http://localhost:8080/ /;
proxy_read_timeout 60s;
#try_files $uri $uri/ =404;
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}

```


Start index.js file

```bash
   pm2 start index.js

```
