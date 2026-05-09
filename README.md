# Academic & Research Website

A clean, minimal Jekyll site for an academic profile and a technical blog,
built to be hosted for free on GitHub Pages.

## What's here

```
.
├── _config.yml              ← site-wide settings (edit your name, links, etc.)
├── _data/
│   ├── publications.yml     ← edit to add papers
│   └── projects.yml         ← edit to add projects
├── _includes/               ← header, footer, head — small reusable bits
├── _layouts/                ← page templates
├── _posts/                  ← blog posts (new ones go here)
├── assets/css/main.css      ← all the styles
├── assets/img/              ← images (replace profile-placeholder.svg with your photo)
├── index.html               ← About / home page
├── publications.md          ← Publications page
├── projects.md              ← Projects page
├── blog.html                ← Blog listing page
├── cv.md                    ← CV page
├── contact.md               ← Contact page
└── 404.html                 ← Not-found page
```

---

## Quick start: deploy to GitHub Pages

The fastest path to a live site at `https://YOURUSERNAME.github.io`.

### 1. Create a repository

GitHub Pages has two flavors — pick one:

- **User site** (recommended for a personal profile): create a repo named
  exactly `YOURUSERNAME.github.io`. The site will live at
  `https://YOURUSERNAME.github.io`. Leave `baseurl: ""` in `_config.yml`.
- **Project site**: create any repo (e.g. `academic-site`). The site will
  live at `https://YOURUSERNAME.github.io/academic-site`. Set
  `baseurl: "/academic-site"` in `_config.yml`.

### 2. Push this folder to the repo

From inside this folder:

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOURUSERNAME/YOURREPO.git
git push -u origin main
```

### 3. Enable GitHub Pages

On GitHub, go to **Settings → Pages**:

- **Source**: "Deploy from a branch"
- **Branch**: `main` · **Folder**: `/ (root)`
- Click **Save**.

GitHub will build and publish your site within a minute or two. The Pages
section will show the live URL once it's ready.

### 4. Customize

Open `_config.yml` and replace placeholders with your real info:

```yaml
title: "Your Name"
author:
  name: "Your Name"
  affiliation: "Your University / Lab"
  position: "PhD Student / Postdoc / Professor"
  email: "you@example.com"

links:
  email: "you@example.com"
  github: "yourusername"
  scholar: "https://scholar.google.com/citations?user=XXXXX"
  orcid: "0000-0000-0000-0000"
  linkedin: "yourusername"
  twitter: "yourusername"
  cv_pdf: "/assets/cv.pdf"   # optional — drop a PDF in /assets to enable
```

Then edit:

- `index.html` — your bio, news, recent writing
- `_data/publications.yml` — your papers
- `_data/projects.yml` — your projects
- `cv.md` — your CV
- `contact.md` — your contact info
- `assets/img/profile-placeholder.svg` — replace with your photo (`profile.jpg`),
  then update the `<img src=...>` in `index.html`

---

## Writing a blog post

Create a new file in `_posts/` named `YYYY-MM-DD-your-slug.md`:

```markdown
---
title: "Your post title"
subtitle: "Optional one-liner under the title."
date: 2026-05-15
tags: [research, machine-learning]
math: true   # only needed if your post uses LaTeX math
---

Your post content goes here, in standard markdown.

## A heading

Some prose, with `inline code` and:

​```python
def hello():
    print("world")
​```

Math when you need it: $E = mc^2$
```

The post will appear automatically on the home page (most recent 3) and the
blog listing.

---

## Local preview (optional)

You don't need this — GitHub Pages will build the site for you. But if you
want to preview locally:

```bash
# Install Ruby (macOS: brew install ruby; Ubuntu: apt install ruby-full build-essential)
gem install bundler
bundle install
bundle exec jekyll serve
```

Then open http://localhost:4000.

---

## Custom domain (optional)

If you own a domain like `yourname.com`:

1. Create a `CNAME` file in this folder with one line: `yourname.com`
2. In your DNS provider, add an `A` record pointing to GitHub's Pages IPs
   (185.199.108.153, .109.153, .110.153, .111.153) or a `CNAME` from
   `www` to `YOURUSERNAME.github.io`.
3. In **Settings → Pages → Custom domain**, enter your domain and check
   "Enforce HTTPS" once the certificate is issued.

---

## Updating the site

Push to `main`. GitHub Pages rebuilds automatically. That's it.

```bash
git add .
git commit -m "New post on X"
git push
```

You can also edit files directly on github.com — handy for fixing a typo from
your phone.
