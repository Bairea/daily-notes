import frontmatter
from daily_notes.core.frontmatter import (
    create_source_frontmatter,
    create_atomic_frontmatter,
    serialize_note,
    deserialize_note,
)


def test_create_source_cited():
    fm = create_source_frontmatter(
        id_="20260720-abc123",
        source_type="article",
        title="Test Article",
        url="https://example.com",
        tags=["python"],
        summary="A test",
    )
    assert fm["id"] == "20260720-abc123"
    assert fm["type"] == "source"
    assert fm["source_type"] == "article"
    assert fm["url"] == "https://example.com"
    assert "created" in fm


def test_create_source_fleeting():
    fm = create_source_frontmatter(
        id_="20260720-def456",
        source_type="fleeting",
        content="A fleeting thought",
    )
    assert fm["type"] == "source"
    assert fm["source_type"] == "fleeting"
    assert fm["content"] == "A fleeting thought"


def test_create_atomic():
    fm = create_atomic_frontmatter(
        id_="20260720-ghi789",
        title="Atomic Thought",
        sources=["20260720-abc123"],
        tags=["pattern"],
        links=[{"target": "20260715-xyz111", "reason": "related"}],
    )
    assert fm["id"] == "20260720-ghi789"
    assert fm["type"] == "atomic"
    assert fm["sources"] == ["20260720-abc123"]
    assert fm["links"][0]["target"] == "20260715-xyz111"


def test_serialize_deserialize_roundtrip():
    fm = create_source_frontmatter(
        id_="20260720-abc123",
        source_type="article",
        title="Test",
    )
    content = "正文内容"
    full_text = serialize_note(fm, content)
    post = deserialize_note(full_text)
    assert post["id"] == "20260720-abc123"
    assert post.content == "正文内容"
