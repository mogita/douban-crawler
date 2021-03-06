def book_model(attrs):
    data = (
        attrs['title'] if 'title' in attrs else "",
        attrs['subtitle'] if 'subtitle' in attrs else "",
        attrs['author'] if 'author' in attrs else "",
        attrs['author_url'] if 'author_url' in attrs else "",
        attrs['author_intro'] if 'author_intro' in attrs else "",
        attrs['publisher'] if 'publisher' in attrs else "",
        attrs['published_at'] if 'published_at' in attrs else None,
        attrs['original_title'] if 'original_title' in attrs else "",
        attrs['translator'] if 'translator' in attrs else "",
        attrs['producer'] if 'producer' in attrs else "",
        attrs['series'] if 'series' in attrs else "",
        attrs['price'] if 'price' in attrs else "",
        attrs['isbn'] if 'isbn' in attrs else "",
        attrs['pages'] if 'pages' in attrs else "0",
        attrs['bookbinding'] if 'bookbinding' in attrs else "",
        attrs['book_intro'] if 'book_intro' in attrs else "",
        attrs['toc'] if 'toc' in attrs else "",
        attrs['rating'] if 'rating' in attrs else 0,
        attrs['rating_count'] if 'rating_count' in attrs else 0,
        attrs['cover_img_url'] if 'cover_img_url' in attrs else "",
        attrs['origin'] if 'origin' in attrs else "",
        attrs['origin_id'] if 'origin_id' in attrs else "",
        attrs['origin_url'] if 'origin_url' in attrs else "",
        attrs['crawled'] if 'crawled' in attrs else False
    )
    if 'id' in attrs and attrs['id'] > 0:
        data = (attrs['id'],) + data
    return data

def tag_model(attrs):
    data = (
        attrs['name'] if 'name' in attrs else '',
        attrs['current_page_t'] if 'current_page_t' in attrs else 1,
        attrs['current_page_r'] if 'current_page_r' in attrs else 1,
        attrs['current_page_s'] if 'current_page_s' in attrs else 1,
        attrs['exhausted_t'] if 'exhausted_t' in attrs else False,
        attrs['exhausted_r'] if 'exhausted_r' in attrs else False,
        attrs['exhausted_s'] if 'exhausted_s' in attrs else False
    )
    if 'id' in attrs and attrs['id'] > 0:
        data = (attrs['id'],) + data
    return data
