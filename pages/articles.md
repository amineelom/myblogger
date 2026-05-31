---
title: All Articles
permalink: /articles/
description: "Browse every MarkeReviews article — honest tech reviews, comparisons, and tutorials. Search or filter by topic."
---
<h1>All Articles</h1>

<div class="article-filters">
  <input type="search" id="article-search" class="article-search" placeholder="Search articles…" aria-label="Search articles">
  <div class="category-chips" id="category-chips">
    <button type="button" class="chip is-active" data-cat="all">All</button>
    {% for cat in site.categories %}
      <button type="button" class="chip" data-cat="{{ cat[0] }}">{{ cat[0] | replace: '-', ' ' }} <span class="chip-count">{{ cat[1].size }}</span></button>
    {% endfor %}
  </div>
</div>

<p class="muted" id="article-count"></p>

<ul class="post-list" id="article-list">
  {% assign posts_sorted = site.posts | sort: "date" | reverse %}
  {% for post in posts_sorted %}
    <li class="article-item" data-title="{{ post.title | downcase | escape }}" data-cats="{% for c in post.categories %}{{ c }} {% endfor %}{% for t in post.tags %}{{ t | downcase }} {% endfor %}">
      <a class="article-thumb" href="{{ post.url | relative_url }}" aria-hidden="true" tabindex="-1">{% include thumb.html post=post class="thumb-sm" %}</a>
      <div class="article-item-body">
        <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
        <span class="muted"> · {{ post.date | date: "%b %d, %Y" }}</span>
      </div>
    </li>
  {% endfor %}
</ul>

<p class="muted" id="no-results" hidden>No articles match your search.</p>

<script>
(function(){
  var search = document.getElementById('article-search');
  var chips  = document.getElementById('category-chips');
  var items  = Array.prototype.slice.call(document.querySelectorAll('.article-item'));
  var countEl = document.getElementById('article-count');
  var noRes  = document.getElementById('no-results');
  var activeCat = 'all';
  var total = items.length;

  function apply(){
    var q = (search.value || '').trim().toLowerCase();
    var shown = 0;
    items.forEach(function(li){
      var matchCat = activeCat === 'all' || (' ' + li.dataset.cats + ' ').indexOf(' ' + activeCat + ' ') !== -1;
      var matchQ = !q || li.dataset.title.indexOf(q) !== -1 || li.dataset.cats.indexOf(q) !== -1;
      var show = matchCat && matchQ;
      li.hidden = !show;
      if (show) shown++;
    });
    countEl.textContent = shown + ' of ' + total + ' articles';
    noRes.hidden = shown !== 0;
  }

  search.addEventListener('input', apply);
  chips.addEventListener('click', function(e){
    var btn = e.target.closest('.chip');
    if (!btn) return;
    activeCat = btn.dataset.cat;
    chips.querySelectorAll('.chip').forEach(function(c){ c.classList.toggle('is-active', c === btn); });
    apply();
  });
  apply();
})();
</script>
