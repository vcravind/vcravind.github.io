---
layout: page
title: Contact
subtitle: Reach out — for collaboration, questions, or to say hello.
permalink: /contact/
---

The best way to reach me is by **email**:
[**{{ site.author.email }}**](mailto:{{ site.author.email }})

<!-- ### Office

[<em>Building name and room number</em>]
[<em>Department</em>]
[<em>University Name</em>]
[<em>Street address, City, State ZIP</em>] -->

### Online

{% if site.links.scholar %}<a href="{{ site.links.scholar }}">Google Scholar</a>{% endif %}{% if site.links.github %} · <a href="https://github.com/{{ site.links.github }}">GitHub</a>{% endif %}{% if site.links.orcid %} · <a href="https://orcid.org/{{ site.links.orcid }}">ORCID</a>{% endif %}{% if site.links.linkedin %} · <a href="https://linkedin.com/in/{{ site.links.linkedin }}">LinkedIn</a>{% endif %}
