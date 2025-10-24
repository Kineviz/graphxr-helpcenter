#! /bin/zsh

export PLAYBOOK=~/bitbucket/kineviz-2024/graphxr-docs/GraphXR-WEB/docs-site
cd $PLAYBOOK
pwd
echo ######
npx antora --fetch antora-playbook.yml