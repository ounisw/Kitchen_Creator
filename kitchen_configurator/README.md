# Kitchen & Wardrobe Configurator 3D

3D configurator for kitchens and wardrobes, embedded in Odoo 19. Salespeople and portal customers
design the project in the browser; the configurator writes the quotation lines and a dimensioned
technical drawing.

## Features

- **Kitchens**: linear, L-shaped or U-shaped rooms; base, drawer, tall and wall units, appliances and
  sinks; four front styles (Modern, Classic, Gola, Shaker); solid, wood-effect and marble finishes.
- **Wardrobes**: sliding (2 to 4 leaves), hinged or open; wood, glass, mirror or mixed doors in an
  aluminium frame; predefined interior layouts per section.
- **Room**: wall lengths and height, windows and doors with their dimensions, worktop with corner
  joints and sink cut-outs, backsplash chosen wall by wall.
- **Technical drawing**: top view, front view of each wall and cabinet schedule, in millimetres,
  saved with the project and printed as a PDF report from Odoo.
- **Quotation**, two methods chosen per project:
  - *per cabinet*: cabinets, hardware, worktop and backsplash per m²;
  - *per m² / linear metre*: each wall per m² (length × ceiling height with base and wall units,
    length × 0.8 m with base units only), worktop and backsplash per linear metre, 0.6 m taken off
    at each worktop corner.
- **Languages**: English, French, Arabic (right-to-left).

## Installation

1. Copy the `kitchen_configurator` folder into your addons path.
2. Update the apps list and install **Kitchen & Wardrobe Configurator 3D**.

Dependencies: `sale`, `portal` (Odoo 19 Community or Enterprise). No Python library to install.

## Usage

- **Salespeople**: open a quotation (draft or sent) and click **Kitchen configurator**. In the
  configurator, **Quote → Create / update the quotation in Odoo** replaces the lines it generated;
  lines added by hand are kept. A confirmed order is never changed: a new quotation is created.
- **Portal customers**: **My account → My kitchen & wardrobe projects**. They design their project and send a
  quote request; a draft quotation is created for their salesperson.
- **All projects**: *Sales → Orders → 3D projects (kitchen & wardrobe)*, with the 3D design and the
  technical drawing (**Technical drawing** button).

Products missing from Odoo are created on the first quotation made by a salesperson, in the
*Kitchen* product category (field *Kitchen configurator reference*); they are then managed in Odoo
like any other product. Quote requests from the portal never create products.

## Good to know

- The catalogue and the price list shipped with the configurator are samples (Saudi riyal, 15 % VAT).
- The configurator runs in the web browser and needs WebGL.

## License

Odoo Proprietary License v1.0 (OPL-1), see `LICENSE`. The configurator web application bundles
open-source libraries listed in `THIRD_PARTY_NOTICES.md`.

© 2026 Classic Decoration
