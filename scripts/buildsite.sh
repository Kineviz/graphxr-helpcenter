#! /bin/zsh

export PLAYBOOK=$HOME/github/Kineviz/kineviz-docs/GraphXR-WEB/docs-site
cd $PLAYBOOK
pwd
echo ######
npx antora --fetch antora-playbook.yml