Deploy:
#locally
cd mysite
git archive --format zip --output ~/Downloads/deploy.zip main 

#remotely
mv mysite mysite.prevdeploy
mkdir mysite
cd mysite

unzip ../deploy.zip 

pip3.9 install -r requirements.txt

python3.9 -m flask_app