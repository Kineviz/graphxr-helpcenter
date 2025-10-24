#! /bin/zsh

KINEVIZ_UI_BASE=~/bitbucket/kineviz-2024/graphxr-docs/GraphXR-WEB
KINEVIZ_UI_BUILD=$KINEVIZ_UI_BASE/build
cd $KINEVIZ_UI_BASE

# See https://docs.antora.org/antora/latest/install-and-run-quickstart/ for details of the build process
cd ~/bitbucket/kineviz-2024/antora-ui-graphxr
pwd

echo ##############
git --version
# nvm alias default 16
# nvm install 16
# nvm use 16
# nvm --version
# node --version
# npm --version
# npx --version
which gulp
echo ##############
# Petrel password needed for sudo commands
# npm install -g gulp-cli
# npm install gulp-install
gulp --version
gulp bundle
gulp preview
# Ctrl C to stop preview
