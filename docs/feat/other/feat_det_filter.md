---
id: feat_det_filter
title: Detection Filter
hide_title: true
---

# Detection Filter

With the _Detection Filter_ feature, detections in an image that fall into
specific field can be filtered.

A _Detection Filter_ is made up of a single or multiple areas defined by polygons.
Each polygon can be positive or negative, meaning detections in the polygon are
included or excluded by the filter. This allows for precise and versatile
filtering. If no positive areas are set, the whole screen is the searched area.

Polygons can be configured manually or drawn in the [Stream Configuration UI]
for easier configuration.

For each Detection Filter a confidence level can be defined, providing another
layer of filtering options.

Each Detection Filter runs in a separate microservice. If multiple filters are
needed, additional microservice instances are required.

When the Detection Filter is enabled, only detections that fall into the
specified area and reach the set confidence level, are recorded.

For more information, see [Starting the Detection Filter].



[Starting the Detection Filter]: ../../dev/start_det_filter.md
[Stream Configuration UI]: ../../dev/conf_sc_ui.md