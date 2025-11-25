# Design Guidelines: Gov.br IBGE Informational Page - Exact Replication

## Core Design Directive

**Critical Requirement**: This project must be an **exact replica** of the provided HTML code. No modifications, additions, or creative interpretations are permitted. Every element must match the original precisely.

## Design Approach

**Reference-Based Approach**: Brazilian Government (gov.br) design system
- Official gov.br branding and visual identity
- Government portal standards for accessibility and trust
- Formal institutional aesthetic with blue color scheme

## Typography

**Font Families**:
- Primary: 'Rawline' (via CDN fonts)
- Fallback: sans-serif

**Hierarchy**:
- Dropcap: 3rem mobile, 3.5rem tablet, 4rem desktop
- H1 Title: text-2xl (1.5rem), font-medium, blue-900
- Subtitle: text-sm (0.875rem), gray-600
- Body: text-base to text-xl (1rem - 1.25rem), gray-800
- Small text: text-xs (0.75rem)
- Tags/Links: text-sm (0.875rem)

## Layout System

**Spacing Primitives**:
- Use Tailwind units: px-4, py-2, py-3, py-4, mb-2, mb-4, mt-2, mt-4, mt-6, mt-8, mx-1, mx-2, mx-3
- Consistent padding: px-4 for main content areas
- Vertical rhythm: py-3, py-4 for sections

**Container**:
- Content width: max-w-3xl mx-auto for article content
- Full-width sections for header and navigation

## Component Library

**Header Components**:
- Gov.br logo (left-aligned, h-6)
- Icon toolbar (ellipsis, palette, half-circle custom element, grid, user login button)
- Title bar with hamburger menu and search icon
- Breadcrumb navigation with mobile wrapping behavior

**Content Components**:
- Category label ("SELEÇÃO")
- Article title with subtitle
- Share icons bar (Facebook, Twitter, X, LinkedIn, WhatsApp, Link)
- Publication date
- Featured image with caption
- Dropcap first letter styling
- Highlighted content boxes (gray background with vertical accent bar)
- Category and tags section

**Custom Elements**:
- Half-circle icon (CSS-generated, gradient split blue/white)
- Dropcap styling (float left, blue-900)
- Vertical accent bars (12px width, gray-300) for content boxes

## Images

**Required Images**:
1. **Gov.br Logo**: `https://barra.sistema.gov.br/v1/assets/govbr.webp` (header)
2. **Article Featured Image**: IBGE DOU announcement image (full-width, shadow-md)
3. Image caption: "Divulgação / Presidência da República" (text-xs, gray-500)

## Accessibility

- Maintain all aria-labels for social icons
- Preserve mobile-responsive breadcrumb wrapping
- Keep semantic HTML structure
- Font sizing allows for user scaling

## Critical Specifications

**Exact Preservation Required**:
- All external links to FGV IBGE inscricao site
- All social sharing icon sizes and styling
- Custom CSS for half-circle, dropcap, portal-redes
- Mobile breakpoints and responsive behavior
- Border treatments (border-t, border-b, border-gray-200)
- Gray-scale variations (gray-500, gray-600, gray-700, gray-800)
- Blue-scale variations (blue-600, blue-700, blue-800, blue-900)

**Content Boxes Pattern**:
- Left vertical bar: 12px width, gray-300
- Content area: flex-1, gray-100 background, px-4 py-4
- Bold label in text-xs
- Body text in text-sm

**No Modifications Allowed**: Do not alter spacing, colors, font sizes, link destinations, image sources, or any visual elements from the original code.