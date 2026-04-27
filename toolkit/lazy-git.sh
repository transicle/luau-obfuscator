chmod +x ./toolkit/rm-cache.sh
chmod +x ./toolkit/upd-readme.sh

bash ./toolkit/upd-readme.sh
bash ./toolkit/rm-cache.sh

git add .
git commit -m "upd: lazy push"
git push --force
