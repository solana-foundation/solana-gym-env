# GitHub Pages Setup

This folder contains the documentation for Solana Gym, hosted on GitHub Pages.

## How to Enable GitHub Pages

1. Go to your repository settings on GitHub
2. Navigate to "Pages" in the left sidebar
3. Under "Source", select "Deploy from a branch"
4. Choose `main` (or `master`) branch
5. Select `/docs` folder
6. Click "Save"

Your site will be available at: `https://[your-username].github.io/solana-gym/`

## Local Preview

To preview the site locally:

```bash
# Install Jekyll (if not already installed)
gem install jekyll bundler

# Navigate to docs folder
cd docs

# Install dependencies
bundle install

# Serve locally
bundle exec jekyll serve

# View at http://localhost:4000
```

## Files

- `index.md` - Main blog content (same as blog.md)
- `_config.yml` - Jekyll configuration for GitHub Pages
- `README.md` - This file (setup instructions)