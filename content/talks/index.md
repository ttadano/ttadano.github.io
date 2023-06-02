---
title: ''
date: 2023-06-01
type: landing

sections:
  - block: collection
    id: upcoming
    content:
      title: Upcoming Talks
      count: 0
      filters:
        folders:
          - event
        exclude_featured: false
        exclude_past: true
    design:
      columns: '2'
      view: list
  - block: collection
    id: featured
    content:
      title: Invited Talks & Seminars
      count: 0
      filters:
        folders:
          - event
        featured_only: true
        exclude_future: true
    design:
      columns: '2'
      view: list
  - block: collection
    content:
      title: Past Talks
      count: 3
      filters:
        folders:
          - event
        featured_only: false
        exclude_future: true
    design:
      columns: '2'
      view: list      


# Optional header image (relative to `static/media/` folder).
header:
  caption: ''
  image: ''
---