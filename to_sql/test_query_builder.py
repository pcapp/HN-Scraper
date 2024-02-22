from convert import (
    build_insert_stories_query,
    build_insert_comment_query,
    Comment,
    Story,
)


# def test_build_insert_stories_query():
#     epoch_time = 1708551776
#     story = Story(id="1", by="user", text="story text", time=epoch_time, score=1)
#     expected_query = """
#     INSERT INTO stories (id, by, text, time, score)
#     VALUES (1, user, "story text", to_timestamp(1708551776), 1)
#     """
#     actual_query, _ = build_insert_stories_query(story)

#     assert expected_query == actual_query


def test_build_insert_comment_query():
    epoch_time = 1708551776
    stories = set([1])

    comment = Comment(
        id="1",
        by="user",
        text="I'm a top level comment.",
        time=epoch_time,
        parent=1,
        kids=[2],
    )

    expected_query = """
    INSERT INTO comments (id, by, parent, kids, is_top_level, text, time)
    VALUES (%s, %s, %s, %s, %s, %s, to_timestamp(%s))
    """
    actual_query, _ = build_insert_comment_query(comment, stories)

    assert expected_query.strip() == actual_query.strip()
