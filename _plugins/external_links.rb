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
        
        # Check if rel already exists
        if attrs_after.include?('rel="')
          attrs_after = attrs_after.gsub(/rel="([^"]*)"/) do |rel_match|
            rel_content = $1
            rel_content += ' nofollow' unless rel_content.include?('nofollow')
            rel_content += ' noopener' unless rel_content.include?('noopener')
            "rel=\"#{rel_content}\""
          end
        else
          attrs_after += ' rel="nofollow noopener"'
        end
        
        "<a#{attrs_before}href=\"#{href}\"#{attrs_after}>"
      end
    end
  end
end

Jekyll::Hooks.register :site, :post_render do |site|
  Jekyll::ExternalLinks.new(site).generate(site)
end