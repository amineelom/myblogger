module Jekyll
  class ExternalLinks
    def initialize(site)
      @site = site
    end

    def generate(site)
      site.pages.each { |page| process_page(page) }
      site.posts.each { |post| process_page(post) }
    end

    private

    def process_page(page)
      return unless page.output
      
      page.output = page.output.gsub(/<a(.*?)href=["'](https?:\/\/[^"']*)["'](.*?)>/i) do |match|
        attrs_before = $1
        href = $2
        attrs_after = $3
        
        # Skip internal links
        next match if href.include?('markereviews.com')

        # Affiliate/tracking links should also carry rel="sponsored" (set here,
        # server-side, so search engines actually see it — JS-set rel is unreliable).
        affiliate = href.match?(/(\baff\b|\bref\b|utm_|tag=|shareasale|impact|partner|r=\d+)/i)

        # Build the required rel tokens for this link.
        needed = %w[nofollow noopener]
        needed << 'sponsored' if affiliate

        if attrs_after.include?('rel="')
          attrs_after = attrs_after.gsub(/rel="([^"]*)"/) do
            rel_content = $1
            needed.each { |tok| rel_content += " #{tok}" unless rel_content.include?(tok) }
            "rel=\"#{rel_content.strip}\""
          end
        else
          attrs_after += " rel=\"#{needed.join(' ')}\""
        end
        
        "<a#{attrs_before}href=\"#{href}\"#{attrs_after}>"
      end
    end
  end
end

Jekyll::Hooks.register :site, :post_render do |site|
  Jekyll::ExternalLinks.new(site).generate(site)
end