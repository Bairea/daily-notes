"""Front matter 解析与生成."""
from datetime import datetime
import frontmatter


def create_source_frontmatter(
    id_: str,
    source_type: str,
    title: str = "",
    url: str = "",
    tags: list[str] | None = None,
    summary: str = "",
    content: str = "",
) -> frontmatter.Post:
    """创建 Source 的 front matter."""
    fm = frontmatter.Post("")
    fm["id"] = id_
    fm["type"] = "source"
    fm["created"] = datetime.now().isoformat()
    fm["tags"] = tags or []
    fm["source_type"] = source_type
    if title:
        fm["title"] = title
    if url:
        fm["url"] = url
    if summary:
        fm["summary"] = summary
    if content:
        fm["content"] = content
    return fm


def create_atomic_frontmatter(
    id_: str,
    title: str = "",
    sources: list[str] | None = None,
    tags: list[str] | None = None,
    links: list[dict[str, str]] | None = None,
) -> frontmatter.Post:
    """创建 Atomic Note 的 front matter."""
    fm = frontmatter.Post("")
    fm["id"] = id_
    fm["type"] = "atomic"
    fm["created"] = datetime.now().isoformat()
    fm["tags"] = tags or []
    if title:
        fm["title"] = title
    if sources:
        fm["sources"] = sources
    if links:
        fm["links"] = links
    return fm


def create_review_frontmatter(
    id_: str,
    period: str,
    related_notes: list[str] | None = None,
) -> frontmatter.Post:
    """创建 Review Note 的 front matter."""
    fm = frontmatter.Post("")
    fm["id"] = id_
    fm["type"] = "review"
    fm["created"] = datetime.now().isoformat()
    fm["period"] = period
    if related_notes:
        fm["related_notes"] = related_notes
    return fm


def serialize_note(post: frontmatter.Post, content: str = "") -> str:
    """将 Post 对象序列化为带 front matter 的 markdown 文本."""
    post.content = content
    return frontmatter.dumps(post)


def deserialize_note(text: str) -> frontmatter.Post:
    """从 markdown 文本解析 Post 对象."""
    return frontmatter.loads(text)
