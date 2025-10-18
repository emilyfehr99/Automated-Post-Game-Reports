Apple Health UI — Structure and Sections

This document summarizes common UI sections and patterns of Apple’s Health app to guide our implementation.

Core Tabs

- Summary: Customizable overview with Favorites, Highlights, Trends. Card-based tiles with sparklines.
- Browse: Category-first navigation (e.g., Activity, Heart, Sleep, Mindfulness, Nutrition, Vitals, Medications, Mobility, Hearing, Respiratory, Cycle Tracking).
- Sharing: Share health data with family/caregivers/providers; manage permissions.

Common Tiles (Summary)

- Activity: Move/Exercise/Stand rings with daily goal progress and recent trend.
- Steps: Today’s steps and a short history bar chart.
- Heart Rate: Resting/Walking HR with line sparkline.
- Sleep: Last night total and stages overview.
- Mindfulness: Minutes today and weekly trend.
- Medications: Today’s schedule and adherence.

Design Patterns

- Cards: Rounded rectangles, subtle borders, dense info with top-left title and small subtitle.
- Color Coding: Activity red, Sleep blue, Heart pink/red, Mindfulness green/teal, etc.
- Typography: San Francisco; bold metrics; muted subtitles; compact spacing.
- Charts: Minimal axes, smooth lines/bars, small multiples.
- Segmented Controls: For sub-sections or filters.

References (non-exhaustive)

- Apple Support — Use the Health app: `https://support.apple.com/en-us/HT203037`
- Apple — Health overview: `https://www.apple.com/ios/health/`
- Apple Human Interface Guidelines (general iOS): `https://developer.apple.com/design/human-interface-guidelines/ios/overview/themes/`
- HealthKit (data framework, informs domain and categories): `https://developer.apple.com/documentation/healthkit`

Notes

- This doc guides an original implementation inspired by Apple’s UI patterns, without using proprietary assets.


