# Files served from the site root

Antora publishes generated pages under `user-guides/`, and the UI under `_/`.
Anything that has to sit at the very top of the domain — ownership-verification
files, and anything similar in future — goes in this directory instead. The
publish workflow copies it verbatim into the built site.

Do not put anything here that Antora already generates. `robots.txt` and
`sitemap.xml` come from `site.robots` and `site.url` in `antora-playbook.yml`,
and a stray copy here would silently overwrite them.

## Current contents

- `google20ee5d6efbc94aeb.html` — Google Search Console ownership verification
  for helpcenter.kineviz.com. Google re-checks periodically, so this must stay
  in place; deleting it un-verifies the property and Search Console stops
  reporting.
