set shell := ["zsh", "-cu"]

watch_paths := "-w GraphXR-WEB/asciidoc -w GraphXR-WEB/docs-site/antora-playbook.yml -w GraphXR-WEB/docs-site/ui.yml -w supplemental-ui -w ui/gulp.d -w ui/gulpfile.js -w ui/preview-src -w ui/src"
watch_exts := "adoc,yml,yaml,hbs,css,js,png,jpg,jpeg,svg,ico"

default:
    @just --list

# Build the UI bundle and full Antora documentation site.
build:
    sh build.sh

# Build only the Antora UI bundle and copy it into the docs site.
build-ui:
    cd ui && npm install && npm run build
    cp ui/build/ui-bundle.zip GraphXR-WEB/docs-site/ui-bundle.zip

# Build only the Antora site from the current docs and UI bundle.
build-site:
    cd GraphXR-WEB/docs-site && npm install && npx antora --fetch antora-playbook.yml

# Serve the compiled site locally. Usage: just preview 5253
preview port="5252":
    python3 -m http.server {{port}} -d GraphXR-WEB/docs-site/build/site

# Rebuild the site when docs, playbook, or UI source files change.
watch:
    @command -v watchexec >/dev/null || { echo "watchexec is required for watch mode. Install it with: brew install watchexec"; exit 1; }
    watchexec -c --debounce 750ms {{watch_paths}} -e {{watch_exts}} --ignore-file .watchexecignore -- just build
