def test_healthz(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_readyz(client):
    # Hits the real DB configured via DATABASE_URL (not the test DB override,
    # since /readyz uses the engine directly rather than Depends(get_db)) -
    # just confirm it responds with a valid shape either way.
    response = client.get("/readyz")
    assert response.status_code in (200, 503)
    assert "status" in response.json()


def test_create_url(client):
    response = client.post("/urls", json={"original_url": "https://example.com"})
    assert response.status_code == 201
    body = response.json()
    assert len(body["short_code"]) == 6
    assert body["original_url"] == "https://example.com/"
    assert "id" in body
    assert "created_at" in body


def test_create_url_rejects_invalid_url(client):
    response = client.post("/urls", json={"original_url": "not-a-url"})
    assert response.status_code == 422


def test_list_urls(client):
    client.post("/urls", json={"original_url": "https://example.com"})
    client.post("/urls", json={"original_url": "https://example.org"})

    response = client.get("/urls")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    assert {url["original_url"] for url in body} == {
        "https://example.com/",
        "https://example.org/",
    }


def test_redirect_follows_to_original_url_and_logs_click(client):
    create_response = client.post("/urls", json={"original_url": "https://example.com"})
    short_code = create_response.json()["short_code"]

    redirect_response = client.get(f"/{short_code}", follow_redirects=False)
    assert redirect_response.status_code == 302
    assert redirect_response.headers["location"] == "https://example.com/"

    stats_response = client.get(f"/urls/{short_code}/stats")
    assert stats_response.json()["total_clicks"] == 1


def test_redirect_unknown_code_returns_404(client):
    response = client.get("/aaaaaa", follow_redirects=False)
    assert response.status_code == 404


def test_redirect_wrong_length_code_returns_422(client):
    response = client.get("/abc", follow_redirects=False)
    assert response.status_code == 422


def test_stats_for_never_clicked_url(client):
    create_response = client.post("/urls", json={"original_url": "https://example.com"})
    short_code = create_response.json()["short_code"]

    response = client.get(f"/urls/{short_code}/stats")
    assert response.status_code == 200
    body = response.json()
    assert body["total_clicks"] == 0
    assert body["recent_clicks"] == []


def test_stats_unknown_code_returns_404(client):
    response = client.get("/urls/aaaaaa/stats")
    assert response.status_code == 404
