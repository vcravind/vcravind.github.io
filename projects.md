---
layout: page
title: Projects
subtitle: Selected projects, software, and research artifacts.
permalink: /projects/
---

<div class="projects">
  {% for project in site.data.projects %}
  <div class="project">
    <h3>{{ project.title }}</h3>
    <p>{{ project.description }}</p>
    <p class="meta">{{ project.meta }}</p>
    {% if project.links %}
    <p class="links">
      {% if project.links.code %}<a href="{{ project.links.code }}">Code</a>{% endif %}
      {% if project.links.demo %}<a href="{{ project.links.demo }}">Demo</a>{% endif %}
      {% if project.links.docs %}<a href="{{ project.links.docs }}">Docs</a>{% endif %}
      {% if project.links.paper %}<a href="{{ project.links.paper }}">Paper</a>{% endif %}
    </p>
    {% endif %}
  </div>
  {% endfor %}
</div>

<p style="margin-top:2rem; font-family:var(--sans); font-size:0.9rem; color:var(--muted);">
  Edit <code>_data/projects.yml</code> to add or update projects.
</p>
