# Article thumbnails

Drop a thumbnail image here for each post and reference it from the post's
front matter. Recommended size **800×450** (16:9), JPG or PNG, < ~150 KB.

## How to use

1. Add the image file here, ideally named after the post slug, e.g.
   `what-is-fine-tuning-custom-ai-models-2025.jpg`
2. Reference it in the post's front matter:

   ```yaml
   thumbnail: /assets/images/thumbnails/what-is-fine-tuning-custom-ai-models-2025.jpg
   ```

## Fallback behaviour

If a post has no `thumbnail:`, templates fall back to the post's `image:`
(the social/OG image), and finally to `default.png` in this folder. So nothing
ever renders broken — but real, unique thumbnails per article look far better in
the home/article listings and help click-through.

`thumbnail:` is used for on-page listing cards; `image:` is used for the
social/Open Graph preview. You can set both, or just `image:` to reuse one image
for everything.
