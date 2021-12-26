def book_model(attrs):
    return (
        attrs['title'],
        attrs['subtitle'],
        attrs['author'],
        attrs['publisher'],
        attrs['published_at'],
        attrs['price'],
        attrs['isbn'],
        attrs['pages'],
        attrs['bookbinding'],
        attrs['book_intro'],
        attrs['author_intro'],
        attrs['toc'],
        attrs['rating'],
        attrs['rating_count'],
        attrs['cover_img_url'],
        attrs['origin'],
        attrs['origin_id'],
        attrs['origin_url'],
        attrs['crawled'],
    )

def tag_model(attrs):
    return (
        attrs['name'],
        attrs['current_page']
    )
