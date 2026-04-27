chmod +x ./toolkit/rm-cache.sh
bash ./toolkit/rm-cache.sh

git add .
git commit -m "upd: lazy push"
git push --force
