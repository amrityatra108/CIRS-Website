"""Content-aware index composition; mirrored by compose() in blog-index.js."""
SPANS = {'feature': 7, 'essay': 5, 'text': 4, 'brief': 3, 'micro': 2,
         'portrait': 4, 'strip': 9, 'visual': 6, 'wide': 8}

def compose(items):
    result = []
    previous = ''
    for i, item in enumerate(items):
        image, ratio = item['image'], item['ratio']
        long_title = item['title_length'] > 55
        if i == 0:
            role = 'feature'
        elif image:
            role = ('portrait' if ratio < .85 else
                    ('strip' if previous != 'strip' else 'wide') if ratio > 2.3 else
                    'wide' if long_title else 'visual')
        else:
            role = ('essay' if long_title or item['minutes'] >= 5 else
                    'micro' if item['excerpt_length'] < 80 else
                    'brief' if previous in ('feature', 'essay', 'wide') else 'text')
        override = item.get('override', '')
        if i and override in SPANS:
            photo_role = override in ('portrait', 'strip', 'visual', 'wide')
            if (not photo_role or image) and (not long_title or SPANS[override] >= 5):
                role = override
        result.append({'role': role, 'span': SPANS[role]})
        previous = role
    split = int(len(items) * .45 + .5) if len(items) >= 6 else 0
    # Pack consecutive stories, never CSS dense/reordering. Grow the strongest
    # entry to absorb small gaps; a two-column breathing space is intentional.
    start = 0
    while start < len(result):
        end, used = start, 0
        while end < len(result) and (end == start or end != split):
            span = result[end]['span']
            if used + span > 12 or end - start == 3:
                break
            used += span
            end += 1
        band = result[start:end]
        largest = max(band, key=lambda entry: entry['span'])
        largest['span'] += max(0, 12 - used - (2 if used < 7 else 0))
        for entry in band:
            entry['start'] = entry is band[0]
        start = end
    return result, split
