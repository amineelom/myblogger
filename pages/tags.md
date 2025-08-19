---
title: Tags
permalink: /tags/
---
<h1>Tags</h1>
{% assign tag_names = site.tags | keys | sort_natural %}
<ul>
  {% for tag_name in tag_names %}
    <li id="{{ tag_name }}"><strong>#{{ tag_name }}</strong>
      <ul>
        {% assign posts_for_tag = site.tags[tag_name] %}
        {% for post in posts_for_tag %}
          <li><a href="{{ post.url | relative_url }}">{{ post.title }}</a> <span class="muted">({{ post.date | date: "%Y-%m-%d" }})</span></li>
        {% endfor %}
      </ul>
    </li>
  {% endfor %}
</ul>
