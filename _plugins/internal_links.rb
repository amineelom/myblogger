# Auto internal linking.
#
# At build time, scans each post's body and turns the first mention of another
# post's topic phrase into a link to that post. Distributes internal link
# authority and improves crawl/dwell — with guardrails against over-optimization:
#
#   * phrases are derived from each post's `tags` (years/parentheticals stripped)
#     plus any explicit `link_keywords:` front matter
#   * a phrase that points at more than one post is dropped (ambiguous)
#   * never links a post to itself
#   * at most `max_per_page` links, each target used at most once, first match only
#   * skips text inside existing <a>, headings, <code>/<pre>, <script>/<style>
#   * only the article body is processed (stops at the share/related blocks)
#
# Config (optional, _config.yml):
#   auto_internal_links:
#     enabled: true
#     max_per_page: 4
#     min_words: 2
#     min_chars: 10
module Jekyll
  class InternalLinker
    PROTECT = %w[a code pre h1 h2 h3 h4 h5 h6 script style].freeze
    # Phrases too generic to be useful anchors (also usually collide and get dropped).
    STOP = [
      "web development", "machine learning", "artificial intelligence",
      "programming languages", "cloud computing", "data science",
      "software development", "web design", "front end", "back end"
    ].freeze

    def initialize(site)
      @site = site
      cfg = site.config["auto_internal_links"] || {}
      @enabled   = cfg.fetch("enabled", true)
      @max       = (cfg["max_per_page"] || 4).to_i
      @min_words = (cfg["min_words"] || 2).to_i
      @min_chars = (cfg["min_chars"] || 10).to_i
    end

    def run
      return unless @enabled
      @map = build_map
      return if @map.empty?
      @site.posts.docs.each { |doc| process(doc) }
    end

    private

    def clean_phrase(raw)
      s = raw.to_s.downcase.strip
      s = s.gsub(/\([^)]*\)/, " ")   # drop parentheticals
      s = s.gsub(/\b20\d\d\b/, " ")  # drop years like 2025
      s = s.gsub(/[^a-z0-9 +#.\-]/, " ")
      s.squeeze(" ").strip
    end

    # phrase => url, only for phrases that unambiguously map to a single post.
    # Returned as an array of [phrase, url] sorted longest-first so the most
    # specific anchor wins within a given text node.
    def build_map
      claims = Hash.new { |h, k| h[k] = [] }
      @site.posts.docs.each do |doc|
        sources = Array(doc.data["tags"]) + Array(doc.data["link_keywords"])
        sources.each do |raw|
          p = clean_phrase(raw)
          next if p.split.length < @min_words
          next if p.length < @min_chars
          next if STOP.include?(p)
          claims[p] << doc.url unless claims[p].include?(doc.url)
        end
      end
      map = []
      claims.each do |p, urls|
        next unless urls.length == 1
        # Precompile the regex ONCE per phrase (huge speedup vs compiling it for
        # every text node of every post).
        re = /(?<![A-Za-z0-9])(#{Regexp.escape(p)})(?![A-Za-z0-9])/i
        map << [p, urls.first, re]
      end
      map.sort_by { |entry| -entry[0].length }
    end

    def process(doc)
      html = doc.output
      return if html.nil?
      start = html.index("<article")
      return if start.nil?
      # Match class substrings (no quotes) so this survives HTML minification,
      # which may strip attribute quotes.
      cut = html.index("social-sharing", start) ||
            html.index("related-articles", start) ||
            html.length
      head = html[0...start]
      body = html[start...cut]
      tail = html[cut..] || ""
      @used = {}
      doc.output = head + transform(body, doc.url) + tail
    end

    def transform(fragment, page_url)
      protect = 0
      count = 0
      tokens = fragment.split(/(<[^>]+>)/)
      tokens.map! do |tok|
        if tok.start_with?("<")
          name = tok[/\A<\/?\s*([a-zA-Z0-9]+)/, 1]
          if name && PROTECT.include?(name.downcase)
            if tok.start_with?("</")
              protect -= 1 if protect > 0
            elsif !tok.end_with?("/>")
              protect += 1
            end
          end
          tok
        elsif protect > 0 || count >= @max || tok.strip.empty?
          tok
        else
          linked, count = link_one(tok, page_url, count)
          linked
        end
      end
      tokens.join
    end

    # At most ONE replacement per text node (avoids matching inside freshly
    # inserted markup), respecting the per-page budget.
    def link_one(text, page_url, count)
      @map.each do |_phrase, url, re|
        next if url == page_url || @used[url]
        if text =~ re
          text = text.sub(re, "<a href=\"#{url}\" class=\"auto-link\">\\1</a>")
          @used[url] = true
          return [text, count + 1]
        end
      end
      [text, count]
    end
  end
end

Jekyll::Hooks.register :site, :post_render do |site|
  Jekyll::InternalLinker.new(site).run
end
