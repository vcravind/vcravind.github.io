---
layout: page
title: Publications
subtitle: Selected peer-reviewed articles and granted patents.
permalink: /publications/
---

<section class="section">
  <h2>Peer-reviewed articles</h2>
  {% for p in site.data.publications %}
  <div class="pub">
    <div class="pub-year">{{ p.year }}</div>
    <div>
      <p class="pub-title">{{ p.title }}{% if p.award %} <span style="color:var(--accent); font-weight:normal; font-size:0.9em;">— {{ p.award }}</span>{% endif %}</p>
      <p class="pub-authors">{{ p.authors }}</p>
      <p class="pub-venue">{{ p.venue }}</p>
      {% if p.links %}
      <p class="pub-links">
        {% if p.links.pdf %}<a href="{{ p.links.pdf }}">PDF</a>{% endif %}
        {% if p.links.code %}<a href="{{ p.links.code }}">Code</a>{% endif %}
        {% if p.links.slides %}<a href="{{ p.links.slides }}">Slides</a>{% endif %}
        {% if p.links.doi %}<a href="{{ p.links.doi }}">DOI</a>{% endif %}
        {% if p.links.bibtex %}<a href="{{ p.links.bibtex }}">BibTeX</a>{% endif %}
      </p>
      {% endif %}
    </div>
  </div>
  {% endfor %}
</section>

<section class="section">
  <h2>Patents (granted)</h2>
  {% for p in site.data.patents %}
  <div class="pub">
    <div class="pub-year">{{ p.year }}</div>
    <div>
      <p class="pub-title">{{ p.title }}</p>
      <p class="pub-authors">{{ p.authors }}</p>
      <p class="pub-venue">{{ p.venue }}</p>
      {% if p.links.pdf %}
      <p class="pub-links">
        <a href="{{ p.links.pdf }}">View patent</a>
      </p>
      {% endif %}
    </div>
  </div>
  {% endfor %}
</section>

<p style="margin-top:2.5rem; font-family:var(--sans); font-size:0.9rem; color:var(--muted);">
  See also: <a href="{{ site.links.scholar | default: '#' }}">Google Scholar</a>{% if site.links.orcid %} · <a href="https://orcid.org/{{ site.links.orcid }}">ORCID</a>{% endif %}.
</p>
