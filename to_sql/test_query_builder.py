from convert import build_insert_stories_query, Story


def test_build_insert_stories_query():
    epoch_time = 1708551776
    story = Story(id="1", by="user", text="story text", time=epoch_time, score=1)
    expected_query = """
    INSERT INTO stories (id, by, text, time, score)
    VALUES (1, user, "story text", to_timestamp(1708551776), 1)
    """
    actual_query = build_insert_stories_query(story)

    assert expected_query == actual_query
