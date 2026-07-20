# tests/test_integration.py
from click.testing import CliRunner
from daily_notes.cli import main
from daily_notes.core.config import save_config, Config
from daily_notes.core.vault import get_current_month_dir, get_atomic_dir
import frontmatter


def test_full_workflow(tmp_vault):
    """完整流程: setup -> add -> review -> ingest -> link."""
    runner = CliRunner()

    # 1. setup
    result = runner.invoke(main, ["setup", "--vault", str(tmp_vault)])
    assert result.exit_code == 0

    # 2. add cited source
    result = runner.invoke(main, [
        "add", "A good article about Python async",
        "--url", "https://example.com/async-python",
        "--type", "article",
        "--title", "Python Async",
        "--tag", "python",
        "--tag", "async",
        "--vault", str(tmp_vault),
    ])
    assert result.exit_code == 0
    source_path = result.output.strip()

    # 3. add fleeting
    result = runner.invoke(main, [
        "add", "The essence of async vs sync is control flow",
        "--vault", str(tmp_vault),
    ])
    assert result.exit_code == 0

    # 4. review
    result = runner.invoke(main, [
        "review", "--period", "day", "--focus", "ingest",
        "--json", "--vault", str(tmp_vault),
    ])
    assert result.exit_code == 0
    import json
    data = json.loads(result.output)
    assert len(data["sources"]) >= 2

    # 5. ingest
    source_id = data["sources"][0]["id"]
    result = runner.invoke(main, [
        "ingest", "--source", source_id,
        "--title", "Async Programming Core",
        "--tag", "pattern",
        "--vault", str(tmp_vault),
    ])
    assert result.exit_code == 0

    # 6. create a second atomic to link
    result2 = runner.invoke(main, [
        "ingest", "--source", source_id,
        "--title", "Control Flow Perspective",
        "--vault", str(tmp_vault),
    ])
    assert result2.exit_code == 0

    # get atomic ids
    month_dir = get_current_month_dir(tmp_vault)
    atomic_dir = get_atomic_dir(month_dir)
    atomic_ids = [f.stem for f in atomic_dir.glob("*.md")]
    assert len(atomic_ids) == 2

    # 7. link them
    result = runner.invoke(main, [
        "link", atomic_ids[0], atomic_ids[1], "complementary views",
        "--vault", str(tmp_vault),
    ])
    assert result.exit_code == 0

    # verify link
    post = frontmatter.loads(
        (atomic_dir / f"{atomic_ids[0]}.md").read_text(encoding="utf-8")
    )
    assert any(l["target"] == atomic_ids[1] for l in post.get("links", []))
