DOC_SITE_DIR=./GraphXR-WEB/docs-site
UI_DIR=./ui

# Build the UI
cd $UI_DIR
npm install
npm run build
cd -

# Copy the UI bundle to the documentation site directory
cp $UI_DIR/build/ui-bundle.zip $DOC_SITE_DIR/ui-bundle.zip

# Build the site
cd $DOC_SITE_DIR
npm install
npx antora --fetch antora-playbook.yml